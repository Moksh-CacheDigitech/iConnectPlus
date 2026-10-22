"""Authentication service."""

import base64
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import settings
from core.exceptions import UnauthorizedException
from core.redis import SessionStore
from modules.foundation.adapters.graph_directory_adapter import GraphDirectoryAdapter
from modules.foundation.domain.exceptions import (
    AccountLockedException,
    InvalidCredentialsException,
)
from modules.foundation.domain.erp_modules import resolve_session_user_type
from modules.foundation.models.security import SecRole, SecTenant, SecUser, SecUserRole
from modules.foundation.repository.session_repository import SessionRepository
from modules.foundation.repository.user_repository import UserRepository
from modules.foundation.service.audit_service import AuditService
from modules.foundation.service.microsoft_oauth_service import (
    MicrosoftOAuthService,
    resolve_frontend_base,
)
from modules.master_data.models.employee import MasterEmployee
from security.ess_default_password import normalize_employee_code
from security.ess_login_captcha import verify_challenge
from security.jwt import JWTService
from security.password import PasswordHasher


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._sessions = SessionRepository(db)
        self._audit = AuditService(db)
        self._jwt = JWTService()
        self._store = SessionStore()

    def login(
        self,
        *,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        import time

        from modules.platform.observability import log_path_metric

        started = time.perf_counter()
        success = False
        try:
            result = self._login_inner(
                email=email,
                password=password,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            success = True
            return result
        finally:
            log_path_metric(
                "auth.login",
                latency_ms=(time.perf_counter() - started) * 1000,
                success=success,
            )

    def _login_inner(
        self,
        *,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        # Block well-known demo credentials unless explicitly allowed (VAPT 7.1.1).
        demo_password = "Secure1!"
        demo_emails = {
            "admin@example.com",
            "tenant.admin@example.com",
        }
        allow_demo = settings.allow_demo_login
        if (
            not allow_demo
            and email.strip().lower() in demo_emails
            and password == demo_password
        ):
            self._audit.log_security_event(
                tenant_id=None,
                event_type="auth.demo_login_blocked",
                user_id=None,
                ip_address=ip_address,
            )
            raise InvalidCredentialsException()

        user = self._users.get_active_by_email(email)
        if user is None or not PasswordHasher.verify_password(password, user.password_hash):
            if user is not None:
                self._users.record_failed_login(user)
                if user.failed_login_count >= settings.account_lockout_threshold:
                    locked_until = datetime.now(timezone.utc) + timedelta(
                        minutes=settings.account_lockout_minutes
                    )
                    self._users.lock_account(user, locked_until)
            raise InvalidCredentialsException()

        if (
            not allow_demo
            and password == demo_password
            and user.email.lower() in demo_emails
        ):
            raise InvalidCredentialsException()

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AccountLockedException()

        if user.mfa_enabled:
            challenge = self._jwt.create_access_token(
                user_id=user.id,
                tenant_id=user.tenant_id,
                user_type=user.user_type,
                session_id=uuid4(),
            )
            return {"mfa_required": True, "mfa_challenge_token": challenge}

        return self._issue_tokens(user, ip_address=ip_address, user_agent=user_agent)

    def login_ess(
        self,
        *,
        company_code: str,
        employee_code: str,
        password: str,
        captcha_id: str | None = None,
        captcha_answer: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        if not verify_challenge(captcha_id, captcha_answer):
            raise InvalidCredentialsException("CAPTCHA verification failed")

        code = company_code.strip().upper()
        emp_code = normalize_employee_code(employee_code)
        company = self._db.scalar(
            select(OrgCompany).where(
                OrgCompany.company_code == code,
                OrgCompany.is_deleted.is_(False),
            )
        )
        if company is None:
            raise InvalidCredentialsException()

        candidates = list(
            self._db.scalars(
                select(MasterEmployee).where(
                    MasterEmployee.company_id == company.id,
                    MasterEmployee.is_deleted.is_(False),
                )
            ).all()
        )
        employee = None
        for row in candidates:
            if normalize_employee_code(row.employee_code) == emp_code:
                employee = row
                break
        if employee is None:
            raise InvalidCredentialsException()

        from modules.hr.models import HrEmployeeProfile
        from security.ess_default_password import verify_ess_dob_password

        profile = self._db.scalar(
            select(HrEmployeeProfile).where(
                HrEmployeeProfile.employee_id == employee.id,
                HrEmployeeProfile.is_deleted.is_(False),
            )
        )

        user = self._db.get(SecUser, employee.user_id) if employee.user_id else None

        password_valid = False
        if user and user.password_hash:
            password_valid = PasswordHasher.verify_password(password, user.password_hash)

        if not password_valid and profile and profile.date_of_birth:
            if verify_ess_dob_password(password, employee.employee_code, profile.date_of_birth):
                password_valid = True
                if user is None:
                    user = SecUser(
                        tenant_id=employee.tenant_id,
                        email=employee.email or f"{emp_code.lower()}@{code.lower()}.local",
                        display_name=f"{employee.first_name} {employee.last_name or ''}".strip(),
                        user_type="employee",
                        status="active",
                        password_hash=PasswordHasher.hash_password(password, validate=False),
                    )
                    self._db.add(user)
                    self._db.flush()
                    employee.user_id = user.id
                    self._db.flush()
                else:
                    user.password_hash = PasswordHasher.hash_password(password, validate=False)
                    self._db.flush()

        if user is None or user.is_deleted or not password_valid:
            if user:
                self._users.record_failed_login(user)
                if user.failed_login_count >= settings.account_lockout_threshold:
                    locked_until = datetime.now(timezone.utc) + timedelta(
                        minutes=settings.account_lockout_minutes
                    )
                    self._users.lock_account(user, locked_until)
            raise InvalidCredentialsException()

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AccountLockedException(
                "Account is temporarily locked. Try again later or contact HR."
            )

        if user.mfa_enabled:
            challenge = self._jwt.create_access_token(
                user_id=user.id,
                tenant_id=user.tenant_id,
                user_type=user.user_type,
                session_id=uuid4(),
            )
            return {"mfa_required": True, "mfa_challenge_token": challenge}

        return self._issue_tokens(user, ip_address=ip_address, user_agent=user_agent)

    def verify_mfa(
        self,
        *,
        email: str,
        otp: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        import pyotp

        user = self._users.get_active_by_email(email)
        if user is None or not user.mfa_enabled or not user.mfa_secret_encrypted:
            raise InvalidCredentialsException()
        totp = pyotp.TOTP(user.mfa_secret_encrypted)
        if not totp.verify(otp, valid_window=1):
            raise InvalidCredentialsException()
        return self._issue_tokens(user, ip_address=ip_address, user_agent=user_agent)

    def login_with_microsoft(
        self,
        *,
        email: str,
        display_name: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        user = self._users.get_active_by_email(email)
        if user is None:
            user = self._provision_microsoft_user(email=email, display_name=display_name)
        if user is None:
            raise InvalidCredentialsException(
                "No ERP account is linked to this Microsoft identity"
            )

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AccountLockedException()

        return self._issue_tokens(user, ip_address=ip_address, user_agent=user_agent)

    def _microsoft_email_allowed(self, email: str) -> bool:
        normalized = email.strip().lower()
        if normalized in settings.microsoft_platform_admin_email_set():
            return True
        domain = settings.microsoft_user_email_domain.strip().lower().lstrip("@")
        return bool(domain and normalized.endswith(f"@{domain}"))

    def _provision_microsoft_user(
        self,
        *,
        email: str,
        display_name: str | None,
    ) -> SecUser | None:
        """Just-in-time link for org-domain (or platform-admin) Microsoft accounts."""
        if not self._microsoft_email_allowed(email):
            return None

        tenant = self._db.scalar(
            select(SecTenant).where(
                SecTenant.tenant_code == "BOOTSTRAP",
                SecTenant.is_deleted.is_(False),
            )
        )
        if tenant is None:
            return None

        from core.exceptions import ConflictException
        from modules.foundation.service.org_context_service import OrgContextService
        from modules.foundation.service.user_service import UserService

        normalized = email.strip().lower()
        existing = self._db.scalar(
            select(SecUser).where(
                SecUser.tenant_id == tenant.id,
                SecUser.email == normalized,
            )
        )
        if existing is not None:
            if existing.is_deleted:
                existing.is_deleted = False
                existing.deleted_at = None
                existing.deleted_by = None
                existing.status = "active"
                self._db.flush()
            return existing

        is_admin = normalized in settings.microsoft_platform_admin_email_set()
        name = (display_name or "").strip() or normalized.split("@")[0]
        service = UserService(self._db)
        try:
            user_row = service.create_user(
                tenant_id=tenant.id,
                email=normalized,
                password=f"Ms0!{secrets.token_urlsafe(18)}",
                display_name=name,
                user_type="super_admin" if is_admin else "employee",
            )
        except ConflictException:
            return self._users.get_active_by_email(normalized)

        user = self._db.get(SecUser, user_row.id)
        if user is None:
            return None

        if is_admin:
            role = self._db.scalar(
                select(SecRole).where(
                    SecRole.tenant_id == tenant.id,
                    SecRole.role_code == "SUPER_ADMIN",
                    SecRole.is_deleted.is_(False),
                )
            )
            if role is not None:
                service.assign_role(
                    tenant_id=tenant.id,
                    user_id=user.id,
                    role_id=role.id,
                    assigned_by=None,
                )

        org = OrgContextService(self._db)
        company, branch = org.get_tenant_primary_org(tenant.id)
        if company is not None:
            org.ensure_default_scope(
                tenant_id=tenant.id,
                user_id=user.id,
                company_id=company.id,
                branch_id=branch.id if branch else None,
            )
        return user

    def complete_microsoft_oauth(
        self,
        *,
        code: str,
        state: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str, str | None]:
        oauth = MicrosoftOAuthService()
        stored = self._store.pop_oauth_state(state)
        if stored is None:
            raise InvalidCredentialsException("Microsoft sign-in session expired. Try again.")

        return_to = (
            stored.get("return_to") if isinstance(stored.get("return_to"), str) else "/"
        )
        frontend_origin = stored.get("frontend_origin")
        frontend_base = resolve_frontend_base(
            frontend_origin if isinstance(frontend_origin, str) else None
        )
        claims_bundle = oauth.exchange_authorization_code(code)
        claims = claims_bundle.get("claims")
        if not isinstance(claims, dict):
            raise InvalidCredentialsException("Microsoft sign-in did not return identity claims")
        ms_access_token = claims_bundle.get("access_token")
        email = MicrosoftOAuthService.email_from_claims(claims)
        if not email:
            raise InvalidCredentialsException("Microsoft account did not include an email address")

        display_name = claims.get("name")
        if not isinstance(display_name, str):
            display_name = None

        tokens = self.login_with_microsoft(
            email=email,
            display_name=display_name,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        user = self._users.get_active_by_email(email)
        if user is not None and isinstance(ms_access_token, str) and ms_access_token:
            self._cache_microsoft_avatar(user.id, ms_access_token)

        exchange_code = oauth.create_exchange_code()
        self._store.set_oauth_exchange(
            exchange_code,
            {**tokens, "return_to": return_to, "frontend_base": frontend_base},
        )
        return exchange_code, return_to, frontend_base

    def resolve_user_avatar(self, *, user_id: UUID, email: str) -> tuple[bytes, str] | None:
        """Return cached Microsoft profile photo, refreshing from Graph when needed."""
        cached = self._store.get_user_avatar(user_id)
        if cached is not None:
            try:
                return base64.b64decode(cached["data_b64"]), cached["content_type"]
            except Exception:
                pass

        if self._store.has_user_avatar_miss(user_id):
            return None

        adapter = GraphDirectoryAdapter()
        if not adapter.configured:
            self._store.set_user_avatar_miss(user_id)
            return None

        try:
            photo = adapter.fetch_user_photo(email)
        except Exception:
            self._store.set_user_avatar_miss(user_id)
            return None

        if photo is None:
            self._store.set_user_avatar_miss(user_id)
            return None

        content, content_type = photo
        self._store.set_user_avatar(
            user_id,
            content_type=content_type,
            data_b64=base64.b64encode(content).decode("ascii"),
        )
        return content, content_type

    def _cache_microsoft_avatar(self, user_id: UUID, ms_access_token: str) -> None:
        photo = MicrosoftOAuthService.fetch_profile_photo(ms_access_token)
        if photo is None:
            self._store.set_user_avatar_miss(user_id)
            return
        content, content_type = photo
        self._store.set_user_avatar(
            user_id,
            content_type=content_type,
            data_b64=base64.b64encode(content).decode("ascii"),
        )

    def redeem_microsoft_exchange(self, exchange_code: str) -> dict:
        payload = self._store.pop_oauth_exchange(exchange_code)
        if payload is None:
            raise InvalidCredentialsException("Sign-in code expired or already used")
        return payload

    def refresh(
        self,
        refresh_token: str,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        payload = self._jwt.decode_token(refresh_token, expected_type="refresh")
        stored = self._sessions.get_refresh_token(refresh_token)
        if stored is None:
            # Refresh-token reuse: a previously rotated token presented again → kill family.
            if settings.refresh_reuse_detection:
                prior = self._sessions.get_refresh_token_any(refresh_token)
                if prior is not None and prior.revoked_at is not None:
                    self._sessions.revoke(prior.session_id, revoked_by=UUID(payload["sub"]))
                    self._sessions.revoke_all_refresh_for_session(prior.session_id)
                    self._store.delete_session(prior.session_id)
                    self._audit.log_security_event(
                        tenant_id=prior.tenant_id,
                        event_type="auth.refresh_reuse",
                        user_id=prior.user_id,
                    )
            raise UnauthorizedException("Refresh token revoked or invalid")

        user_id = UUID(payload["sub"])
        session_id = UUID(payload["session_id"])
        session = self._sessions.get_active(session_id)
        if session is None:
            raise UnauthorizedException("Session expired or revoked")

        # Session-to-client binding (VAPT 7.1.6) — reject replay from mismatched clients.
        if settings.session_bind_user_agent:
            issued_ua = (session.user_agent or "").strip()
            current_ua = (user_agent or "").strip()
            if issued_ua and current_ua and issued_ua != current_ua:
                self._sessions.revoke(session_id, revoked_by=user_id)
                self._store.delete_session(session_id)
                raise UnauthorizedException("Session binding mismatch — please sign in again")
        if settings.session_bind_ip:
            issued_ip = (session.ip_address or "").strip()
            current_ip = (ip_address or "").strip()
            if issued_ip and current_ip and issued_ip != current_ip:
                self._sessions.revoke(session_id, revoked_by=user_id)
                self._store.delete_session(session_id)
                raise UnauthorizedException("Session binding mismatch — please sign in again")

        user_model = self._db.get(SecUser, user_id)
        if user_model is None:
            raise UnauthorizedException("User not found")

        session_user_type = self._session_user_type(user_model)
        new_refresh, _ = self._jwt.create_refresh_token(user_id=user_id, session_id=session_id)
        refresh_days = settings.jwt_refresh_token_expire_days
        new_row = self._sessions.store_refresh_token(
            tenant_id=session.tenant_id,
            user_id=user_id,
            session_id=session_id,
            token=new_refresh,
            expires_at=datetime.now(timezone.utc) + timedelta(days=refresh_days),
        )
        self._sessions.revoke_refresh_token(stored, replaced_by=new_row.id)

        access = self._jwt.create_access_token(
            user_id=user_id,
            tenant_id=session.tenant_id,
            user_type=session_user_type,
            session_id=session_id,
        )
        # Keep Redis session alive alongside refreshed tokens.
        self._store.touch_session(session_id)
        return {
            "access_token": access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "session_id": str(session_id),
        }

    def logout(self, session_id: UUID, user_id: UUID, tenant_id: UUID) -> None:
        self._sessions.revoke(session_id, revoked_by=user_id)
        self._store.delete_session(session_id)
        self._audit.log_security_event(
            tenant_id=tenant_id,
            event_type="auth.logout",
            user_id=user_id,
        )

    def _role_codes_for_user(self, user_id: UUID) -> list[str]:
        stmt = (
            select(SecRole.role_code)
            .join(SecUserRole, SecUserRole.role_id == SecRole.id)
            .where(SecUserRole.user_id == user_id, SecRole.is_deleted.is_(False))
        )
        return list(self._db.scalars(stmt).all())

    def _session_user_type(self, user: SecUser) -> str:
        resolved = resolve_session_user_type(
            user.user_type,
            user.email,
            self._role_codes_for_user(user.id),
            platform_admin_emails=settings.microsoft_platform_admin_email_set(),
        )
        if resolved != user.user_type:
            user.user_type = resolved
            self._db.flush()
        return resolved

    def _issue_tokens(
        self,
        user: SecUser,
        *,
        ip_address: str | None,
        user_agent: str | None,
    ) -> dict:
        user_type = self._session_user_type(user)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.session_ttl_seconds)
        provisional_session_id = uuid4()
        session = self._sessions.create_session(
            tenant_id=user.tenant_id,
            user_id=user.id,
            session_token=str(provisional_session_id),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )
        access = self._jwt.create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            user_type=user_type,
            session_id=session.id,
        )
        refresh, _ = self._jwt.create_refresh_token(user_id=user.id, session_id=session.id)
        refresh_days = settings.jwt_refresh_token_expire_days
        self._sessions.store_refresh_token(
            tenant_id=user.tenant_id,
            user_id=user.id,
            session_id=session.id,
            token=refresh,
            expires_at=datetime.now(timezone.utc) + timedelta(days=refresh_days),
        )
        from modules.foundation.service.org_context_service import OrgContextService

        company_id, branch_id = OrgContextService(self._db).resolve_company_and_branch(
            user_id=user.id,
            tenant_id=user.tenant_id,
            user_type=user.user_type,
        )
        session_payload: dict[str, str | None] = {
            "user_id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "ip": ip_address,
            "user_agent": user_agent,
        }
        if company_id:
            session_payload["company_id"] = str(company_id)
        if branch_id:
            session_payload["branch_id"] = str(branch_id)
        self._store.set_session(session.id, session_payload)
        self._users.record_successful_login(user)
        self._audit.log_security_event(
            tenant_id=user.tenant_id,
            event_type="auth.login",
            user_id=user.id,
            ip_address=ip_address,
        )
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "session_id": str(session.id),
        }
