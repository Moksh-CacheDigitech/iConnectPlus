"""Generate Sprint 13 Recruitment module artifacts. Run from apps/api: python scripts/_gen_recruitment_module.py"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
REC = SRC / "modules" / "recruitment"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = SRC / "tests"
SHARED = SRC / "shared"

FILES_WRITTEN: list[Path] = []

OPT_BRANCH = '''
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
'''

WF_FIELDS = '''
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
'''


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    FILES_WRITTEN.append(path)
    print("wrote", path.relative_to(ROOT))


def patch_file(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new.strip() in text:
        print("skip (already)", path.relative_to(ROOT))
        return
    if old not in text:
        raise SystemExit(f"patch failed in {path}: marker not found")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("patched", path.relative_to(ROOT))


# ---------------------------------------------------------------------------
# Table registry: (module, ORM class, repo/service name, branch_scoped)
# ---------------------------------------------------------------------------

TABLES: list[tuple[str, str, str, bool]] = [
    ("job_requisition", "RecJobRequisition", "JobRequisition", True),
    ("job_posting", "RecJobPosting", "JobPosting", False),
    ("recruitment_source", "RecRecruitmentSource", "RecruitmentSource", False),
    ("recruiter", "RecRecruiter", "Recruiter", False),
    ("candidate", "RecCandidate", "Candidate", False),
    ("candidate_document", "RecCandidateDocument", "CandidateDocument", False),
    ("resume", "RecResume", "Resume", False),
    ("application", "RecApplication", "Application", True),
    ("application_stage", "RecApplicationStage", "ApplicationStage", False),
    ("interview", "RecInterview", "Interview", True),
    ("interview_feedback", "RecInterviewFeedback", "InterviewFeedback", False),
    ("offer", "RecOffer", "Offer", True),
    ("offer_approval", "RecOfferApproval", "OfferApproval", False),
    ("background_verification", "RecBackgroundVerification", "BackgroundVerification", True),
    ("reference_check", "RecReferenceCheck", "ReferenceCheck", False),
    ("talent_pool", "RecTalentPool", "TalentPool", False),
    ("candidate_note", "RecCandidateNote", "CandidateNote", False),
    ("onboarding", "RecOnboarding", "Onboarding", True),
    ("onboarding_task", "RecOnboardingTask", "OnboardingTask", False),
    ("recruitment_report", "RecRecruitmentReport", "RecruitmentReport", False),
]

CLASS_MAP = {t[0]: t[1] for t in TABLES}

MIGRATIONS: list[tuple[str, str | list[str], str]] = [
    ("0201_create_recruitment_schema", "schema", "0200_seed_payroll_workflows"),
    ("0202_rec_job_requisition", "job_requisition", "0201_create_recruitment_schema"),
    ("0203_rec_job_posting", "job_posting", "0202_rec_job_requisition"),
    ("0204_rec_recruitment_source", "recruitment_source", "0203_rec_job_posting"),
    ("0205_rec_recruiter", "recruiter", "0204_rec_recruitment_source"),
    ("0206_rec_candidate", "candidate", "0205_rec_recruiter"),
    ("0207_rec_cand_doc_resume", ["candidate_document", "resume"], "0206_rec_candidate"),
    ("0208_rec_application", "application", "0207_rec_cand_doc_resume"),
    ("0209_rec_application_stage", "application_stage", "0208_rec_application"),
    ("0210_rec_interview", "interview", "0209_rec_application_stage"),
    ("0211_rec_interview_feedback", "interview_feedback", "0210_rec_interview"),
    ("0212_rec_offer", "offer", "0211_rec_interview_feedback"),
    ("0213_rec_offer_approval", "offer_approval", "0212_rec_offer"),
    ("0214_rec_background_verif", "background_verification", "0213_rec_offer_approval"),
    ("0215_rec_reference_check", "reference_check", "0214_rec_background_verif"),
    ("0216_rec_talent_pool", "talent_pool", "0215_rec_reference_check"),
    ("0217_rec_candidate_note", "candidate_note", "0216_rec_talent_pool"),
    ("0218_rec_onboarding", "onboarding", "0217_rec_candidate_note"),
    ("0219_rec_onboarding_task", "onboarding_task", "0218_rec_onboarding"),
    ("0220_rec_recruitment_report", "recruitment_report", "0219_rec_onboarding_task"),
    ("0221_seed_rec_permissions", "seed_perms", "0220_rec_recruitment_report"),
    ("0222_seed_recruitment_workflows", "seed_wf", "0221_seed_rec_permissions"),
]

ROUTE_SPECS: list[tuple[str, str, str, str, bool]] = [
    ("job-requisitions", "JobRequisition", "JobRequisitionService", "recruitment.requisition", True),
    ("job-postings", "JobPosting", "JobPostingService", "recruitment.posting", False),
    ("recruitment-sources", "RecruitmentSource", "RecruitmentSourceService", "recruitment.source", False),
    ("recruiters", "Recruiter", "RecruiterService", "recruitment.recruiter", False),
    ("candidates", "Candidate", "CandidateService", "recruitment.candidate", False),
    ("candidate-documents", "CandidateDocument", "CandidateDocumentService", "recruitment.candidate", False),
    ("resumes", "Resume", "ResumeService", "recruitment.candidate", False),
    ("applications", "Application", "ApplicationService", "recruitment.application", True),
    ("application-stages", "ApplicationStage", "ApplicationStageService", "recruitment.application", False),
    ("interviews", "Interview", "InterviewService", "recruitment.interview", True),
    ("interview-feedback", "InterviewFeedback", "InterviewFeedbackService", "recruitment.interview", False),
    ("offers", "Offer", "OfferService", "recruitment.offer", True),
    ("offer-approvals", "OfferApproval", "OfferApprovalService", "recruitment.offer", False),
    ("background-verifications", "BackgroundVerification", "BackgroundVerificationService", "recruitment.verification", True),
    ("reference-checks", "ReferenceCheck", "ReferenceCheckService", "recruitment.verification", False),
    ("talent-pools", "TalentPool", "TalentPoolService", "recruitment.talent_pool", False),
    ("candidate-notes", "CandidateNote", "CandidateNoteService", "recruitment.note", False),
    ("onboarding", "Onboarding", "OnboardingService", "recruitment.onboarding", True),
    ("onboarding-tasks", "OnboardingTask", "OnboardingTaskService", "recruitment.onboarding", False),
    ("reports", "RecruitmentReport", "RecruitmentReportService", "recruitment.report", False),
]

MODELS: dict[str, str] = {}

MODELS["job_requisition"] = rf'''"""Job requisition ORM per ERD_13 §6.1."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecTransactionMixin


class RecJobRequisition(Base, *RecTransactionMixin):
    __tablename__ = "rec_job_requisition"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_rec_req_company_doc"),
        CheckConstraint("openings_count > 0", name="ck_rec_req_openings"),
        CheckConstraint("filled_count >= 0", name="ck_rec_req_filled_nonneg"),
        CheckConstraint("filled_count <= openings_count", name="ck_rec_req_filled_le_openings"),
        CheckConstraint(
            "employment_type IN ('permanent','contract','intern','consultant')",
            name="ck_rec_req_employment_type",
        ),
        CheckConstraint(
            "priority IN ('low','medium','high','critical')",
            name="ck_rec_req_priority",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','open','on_hold','filled','closed','cancelled','rejected')",
            name="ck_rec_req_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    requisition_title: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    designation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    employment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    openings_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    filled_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    hiring_manager_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    recruiter_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_recruiter.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    target_hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    min_experience_years: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    max_experience_years: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    salary_band_min: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    salary_band_max: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    currency_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    job_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["job_posting"] = rf'''"""Job posting ORM per ERD_13 §6.2."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecJobPosting(Base, *RecDetailMixin):
    __tablename__ = "rec_job_posting"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_rec_post_company_doc"),
        CheckConstraint(
            "channel IN ('internal','career_site','job_board','agency','referral','campus','other')",
            name="ck_rec_post_channel",
        ),
        CheckConstraint(
            "status IN ('draft','published','paused','closed','cancelled')",
            name="ck_rec_post_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    job_requisition_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_job_requisition.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    posting_title: Mapped[str] = mapped_column(String(255), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), nullable=False)
    recruitment_source_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_recruitment_source.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    publish_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    publish_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    crm_campaign_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["recruitment_source"] = rf'''"""Recruitment source catalog ORM per ERD_13 §6.15."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecMasterMixin


class RecRecruitmentSource(Base, *RecMasterMixin):
    __tablename__ = "rec_recruitment_source"
    __table_args__ = (
        UniqueConstraint("company_id", "source_code", name="uk_rec_source_company_code"),
        CheckConstraint(
            "source_type IN ('organic','paid','agency','referral','campus','internal')",
            name="ck_rec_source_type",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_rec_source_status"),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    source_code: Mapped[str] = mapped_column(String(50), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["recruiter"] = rf'''"""Recruiter staff ORM per ERD_13 §6.14."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecMasterMixin


class RecRecruiter(Base, *RecMasterMixin):
    __tablename__ = "rec_recruiter"
    __table_args__ = (
        UniqueConstraint("company_id", "recruiter_code", name="uk_rec_recruiter_company_code"),
        UniqueConstraint("company_id", "employee_id", name="uk_rec_recruiter_company_employee"),
        CheckConstraint("status IN ('active','inactive')", name="ck_rec_recruiter_status"),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    recruiter_code: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    max_open_requisitions: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["candidate"] = rf'''"""Candidate pre-master ORM per ERD_13 §6.3."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecMasterMixin


class RecCandidate(Base, *RecMasterMixin):
    __tablename__ = "rec_candidate"
    __table_args__ = (
        UniqueConstraint("company_id", "candidate_code", name="uk_rec_candidate_company_code"),
        CheckConstraint(
            "status IN ('prospect','applied','screening','interview','selected','offered','hired','rejected','on_hold','withdrawn','blacklisted')",
            name="ck_rec_candidate_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    candidate_code: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    mobile: Mapped[str | None] = mapped_column(String(30), nullable=True)
    current_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_employer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total_experience_years: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    highest_education: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recruitment_source_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_recruitment_source.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    primary_recruiter_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_recruiter.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="prospect", index=True)
'''

MODELS["candidate_document"] = rf'''"""Candidate document ORM per ERD_13 §6.4."""

from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecCandidateDocument(Base, *RecDetailMixin):
    __tablename__ = "rec_candidate_document"
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('identity','education','experience','portfolio','other')",
            name="ck_rec_cand_doc_type",
        ),
        CheckConstraint(
            "status IN ('uploaded','verified','rejected','archived')",
            name="ck_rec_cand_doc_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    verified_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="uploaded", index=True)
'''

MODELS["resume"] = rf'''"""Resume ORM per ERD_13 §6.5."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecResume(Base, *RecDetailMixin):
    __tablename__ = "rec_resume"
    __table_args__ = (
        UniqueConstraint("candidate_id", "version_no", name="uk_rec_resume_candidate_version"),
        CheckConstraint(
            "status IN ('active','superseded','archived')",
            name="ck_rec_resume_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    version_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    storage_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    parsed_skills_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["application"] = rf'''"""Application ORM per ERD_13 §6.6."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecTransactionMixin


class RecApplication(Base, *RecTransactionMixin):
    __tablename__ = "rec_application"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_rec_app_company_doc"),
        CheckConstraint(
            "status IN ('applied','screening','interview','selected','offer','hired','rejected','on_hold','withdrawn')",
            name="ck_rec_app_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    job_requisition_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_job_requisition.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    job_posting_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_job_posting.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    recruitment_source_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_recruitment_source.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    recruiter_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_recruiter.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_stage_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="applied", index=True)
'''

MODELS["application_stage"] = rf'''"""Application stage history ORM per ERD_13 §6.7."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecApplicationStage(Base, *RecDetailMixin):
    __tablename__ = "rec_application_stage"
    __table_args__ = (
        CheckConstraint(
            "stage_code IN ('applied','screening','interview','selected','offer','hired','rejected','on_hold')",
            name="ck_rec_app_stage_code",
        ),
        CheckConstraint(
            "status IN ('active','completed','skipped','cancelled')",
            name="ck_rec_app_stage_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    stage_code: Mapped[str] = mapped_column(String(50), nullable=False)
    stage_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    changed_by_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.sec_user.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["interview"] = rf'''"""Interview ORM per ERD_13 §6.8."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecTransactionMixin


class RecInterview(Base, *RecTransactionMixin):
    __tablename__ = "rec_interview"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_rec_intv_company_doc"),
        CheckConstraint(
            "interview_type IN ('hr_round','technical','manager','final','other')",
            name="ck_rec_intv_type",
        ),
        CheckConstraint(
            "result IN ('pending','pass','fail','hold')",
            name="ck_rec_intv_result",
        ),
        CheckConstraint(
            "status IN ('scheduled','completed','cancelled','no_show')",
            name="ck_rec_intv_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    interview_type: Mapped[str] = mapped_column(String(30), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meeting_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    interviewer_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    panel_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="scheduled", index=True)
'''

MODELS["interview_feedback"] = rf'''"""Interview feedback ORM per ERD_13 §6.9."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecInterviewFeedback(Base, *RecDetailMixin):
    __tablename__ = "rec_interview_feedback"
    __table_args__ = (
        UniqueConstraint(
            "interview_id",
            "interviewer_employee_id",
            name="uk_rec_intv_feedback_interviewer",
        ),
        CheckConstraint(
            "recommendation IN ('strong_hire','hire','no_hire','hold')",
            name="ck_rec_intv_feedback_recommendation",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','locked')",
            name="ck_rec_intv_feedback_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    interview_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_interview.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    interviewer_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(30), nullable=True)
    competency_scores_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["offer"] = rf'''"""Offer ORM per ERD_13 §6.10."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecTransactionMixin


class RecOffer(Base, *RecTransactionMixin):
    __tablename__ = "rec_offer"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_rec_offer_company_doc"),
        CheckConstraint(
            "employment_type IN ('permanent','contract','intern','consultant')",
            name="ck_rec_offer_employment_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','sent','accepted','rejected','expired','withdrawn','cancelled')",
            name="ck_rec_offer_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    job_requisition_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_job_requisition.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    designation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    offered_ctc: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    offered_gross: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    offer_valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    employment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    salary_structure_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    offer_letter_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["offer_approval"] = rf'''"""Offer approval ORM per ERD_13 §6.11."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecOfferApproval(Base, *RecDetailMixin):
    __tablename__ = "rec_offer_approval"
    __table_args__ = (
        UniqueConstraint("offer_id", "approval_level", name="uk_rec_offer_approval_level"),
        CheckConstraint(
            "decision IN ('pending','approved','rejected')",
            name="ck_rec_offer_approval_decision",
        ),
        CheckConstraint(
            "status IN ('pending','completed','skipped','cancelled')",
            name="ck_rec_offer_approval_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    offer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_offer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    approver_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    approval_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    decision: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
'''

MODELS["background_verification"] = rf'''"""Background verification ORM per ERD_13 §6.12."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecTransactionMixin


class RecBackgroundVerification(Base, *RecTransactionMixin):
    __tablename__ = "rec_background_verification"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_rec_bgv_company_doc"),
        CheckConstraint(
            "result IN ('pending','clear','adverse','inconclusive')",
            name="ck_rec_bgv_result",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','in_progress','cleared','failed','waived','cancelled')",
            name="ck_rec_bgv_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    offer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_offer.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    application_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verification_scope_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    initiated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    report_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["reference_check"] = rf'''"""Reference check ORM per ERD_13 §6.13."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecReferenceCheck(Base, *RecDetailMixin):
    __tablename__ = "rec_reference_check"
    __table_args__ = (
        CheckConstraint(
            "relationship IN ('manager','peer','client','academic','other')",
            name="ck_rec_ref_check_relationship",
        ),
        CheckConstraint(
            "status IN ('pending','contacted','completed','declined','cancelled')",
            name="ck_rec_ref_check_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    application_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reference_name: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_org: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reference_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reference_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    relationship: Mapped[str] = mapped_column(String(30), nullable=False)
    feedback_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checked_by_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
'''

MODELS["talent_pool"] = rf'''"""Talent pool membership ORM per ERD_13 §6.16."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecMasterMixin


class RecTalentPool(Base, *RecMasterMixin):
    __tablename__ = "rec_talent_pool"
    __table_args__ = (
        UniqueConstraint("company_id", "pool_code", "candidate_id", name="uk_rec_talent_pool_membership"),
        CheckConstraint(
            "availability IN ('passive','active','do_not_contact')",
            name="ck_rec_talent_pool_availability",
        ),
        CheckConstraint(
            "status IN ('active','removed','hired_out')",
            name="ck_rec_talent_pool_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    pool_code: Mapped[str] = mapped_column(String(50), nullable=False)
    pool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    skill_tags_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    availability: Mapped[str] = mapped_column(String(30), nullable=False, default="passive")
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["candidate_note"] = rf'''"""Candidate note ORM per ERD_13 §6.17."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecCandidateNote(Base, *RecDetailMixin):
    __tablename__ = "rec_candidate_note"
    __table_args__ = (
        CheckConstraint(
            "note_type IN ('general','screening','risk','compensation','other')",
            name="ck_rec_cand_note_type",
        ),
        CheckConstraint("status IN ('active','archived')", name="ck_rec_cand_note_status"),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    application_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    author_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.sec_user.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    note_type: Mapped[str] = mapped_column(String(30), nullable=False, default="general")
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["onboarding"] = rf'''"""Onboarding header ORM per ERD_13 §6.18."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecTransactionMixin


class RecOnboarding(Base, *RecTransactionMixin):
    __tablename__ = "rec_onboarding"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_rec_onb_company_doc"),
        CheckConstraint(
            "payroll_handoff_status IN ('not_required','pending','completed','failed')",
            name="ck_rec_onb_payroll_handoff",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','in_progress','completed','cancelled','failed')",
            name="ck_rec_onb_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    offer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_offer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    job_requisition_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_job_requisition.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    designation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    planned_joining_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    actual_joining_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    hr_employment_request_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    payroll_handoff_status: Mapped[str] = mapped_column(String(30), nullable=False, default="not_required")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["onboarding_task"] = rf'''"""Onboarding task ORM per ERD_13 §6.19."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecOnboardingTask(Base, *RecDetailMixin):
    __tablename__ = "rec_onboarding_task"
    __table_args__ = (
        UniqueConstraint("onboarding_id", "task_code", name="uk_rec_onb_task_code"),
        CheckConstraint(
            "status IN ('pending','in_progress','completed','waived','blocked','cancelled')",
            name="ck_rec_onb_task_status",
        ),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    onboarding_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_onboarding.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    task_code: Mapped[str] = mapped_column(String(50), nullable=False)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assignee_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    completion_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
'''

MODELS["recruitment_report"] = rf'''"""Recruitment report snapshot ORM per ERD_13 §6.20."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecMasterMixin


class RecRecruitmentReport(Base, *RecMasterMixin):
    __tablename__ = "rec_recruitment_report"
    __table_args__ = (
        UniqueConstraint("company_id", "report_code", name="uk_rec_report_company_code"),
        CheckConstraint(
            "report_type IN ('funnel','time_to_hire','source_roi','recruiter_productivity')",
            name="ck_rec_report_type",
        ),
        CheckConstraint("status IN ('draft','finalized')", name="ck_rec_report_status"),
        {{"schema": "recruitment"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    report_code: Mapped[str] = mapped_column(String(50), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    job_requisition_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_job_requisition.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

def gen_scaffold() -> None:
    w(REC / "__init__.py", '"""Recruitment module — Sprint 13."""\n')
    w(REC / "domain" / "__init__.py", '"""Recruitment domain layer."""\n')
    w(REC / "adapters" / "__init__.py", '"""Recruitment cross-module adapters."""\n')
    w(REC / "service" / "__init__.py", '"""Recruitment services — populated after generation."""\n')
    w(REC / "service" / "engines" / "__init__.py", '"""Recruitment engines — populated after generation."""\n')
    w(REC / "repository" / "__init__.py", '"""Recruitment repositories."""\n')
    w(REC / "models" / "__init__.py", '"""Recruitment models — populated after generation."""\n')
    w(
        REC / "models" / "mixins.py",
        '''
"""Recruitment ORM mixin bundles per ERD_13."""

from database.mixins import (
    AuditMixin,
    BranchMixin,
    CompanyMixin,
    SoftDeleteMixin,
    TenantMixin,
    VersionMixin,
)

RecMasterMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)

RecTransactionMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    BranchMixin,
    SoftDeleteMixin,
    VersionMixin,
)

RecDetailMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)
''',
    )


def gen_domain() -> None:
    w(
        REC / "domain" / "enums.py",
        '''
"""Recruitment domain enums per ERD_13 §11."""

from enum import Enum


class ActiveInactive(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class JobRequisitionStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    OPEN = "open"
    ON_HOLD = "on_hold"
    FILLED = "filled"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class JobPostingStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PAUSED = "paused"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class CandidateStatus(str, Enum):
    PROSPECT = "prospect"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    SELECTED = "selected"
    OFFERED = "offered"
    HIRED = "hired"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"
    WITHDRAWN = "withdrawn"
    BLACKLISTED = "blacklisted"


class CandidateDocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    VERIFIED = "verified"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ResumeStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    SELECTED = "selected"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"
    WITHDRAWN = "withdrawn"


class ApplicationStageStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class InterviewFeedbackStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    LOCKED = "locked"


class OfferStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    CANCELLED = "cancelled"


class OfferApprovalStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class BackgroundVerificationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    CLEARED = "cleared"
    FAILED = "failed"
    WAIVED = "waived"
    CANCELLED = "cancelled"


class ReferenceCheckStatus(str, Enum):
    PENDING = "pending"
    CONTACTED = "contacted"
    COMPLETED = "completed"
    DECLINED = "declined"
    CANCELLED = "cancelled"


class TalentPoolStatus(str, Enum):
    ACTIVE = "active"
    REMOVED = "removed"
    HIRED_OUT = "hired_out"


class CandidateNoteStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class OnboardingStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class OnboardingTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    WAIVED = "waived"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class RecruitmentReportStatus(str, Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"


class PayrollHandoffStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class RecEntityType(str, Enum):
    JOB_REQUISITION = "job_requisition"
    JOB_POSTING = "job_posting"
    CANDIDATE = "candidate"
    APPLICATION = "application"
    INTERVIEW = "interview"
    OFFER = "offer"
    BACKGROUND_VERIFICATION = "background_verification"
    ONBOARDING = "onboarding"
    RECRUITER = "recruiter"
    RECRUITMENT_SOURCE = "recruitment_source"
    TALENT_POOL = "talent_pool"
    RECRUITMENT_REPORT = "recruitment_report"


CODE_PREFIXES: dict[RecEntityType, tuple[str, int, bool]] = {
    RecEntityType.JOB_REQUISITION: ("REQ-", 6, True),
    RecEntityType.JOB_POSTING: ("POST-", 6, True),
    RecEntityType.CANDIDATE: ("CAN-", 6, False),
    RecEntityType.APPLICATION: ("APP-", 6, True),
    RecEntityType.INTERVIEW: ("INTV-", 6, True),
    RecEntityType.OFFER: ("OFF-", 6, True),
    RecEntityType.BACKGROUND_VERIFICATION: ("BGV-", 6, True),
    RecEntityType.ONBOARDING: ("ONB-", 6, True),
    RecEntityType.RECRUITER: ("RCR-", 6, False),
    RecEntityType.RECRUITMENT_SOURCE: ("SRC-", 6, False),
    RecEntityType.TALENT_POOL: ("POOL-", 6, False),
    RecEntityType.RECRUITMENT_REPORT: ("RPT-", 6, True),
}
''',
    )

    exceptions = [t[2] for t in TABLES]
    exc_lines = [
        f'''
class Invalid{name}State(ConflictException):
    def __init__(self, message: str = "Invalid {name.lower()} state") -> None:
        super().__init__(message)
'''
        for name in exceptions
    ]
    w(
        REC / "domain" / "exceptions.py",
        '"""Recruitment domain exceptions."""\n\nfrom core.exceptions import ConflictException\n'
        + "".join(exc_lines),
    )

    w(
        REC / "domain" / "value_objects.py",
        '''
"""Recruitment value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateIdentity:
    first_name: str
    last_name: str
    email: str
    mobile: str | None = None


@dataclass(frozen=True)
class OfferCompensation:
    offered_ctc: float | None
    currency_code: str
''',
    )

    agg_lines = "\n".join(f'    {t[2].upper()} = "rec_{t[0]}"' for t in TABLES)
    w(
        REC / "domain" / "entities.py",
        f'''"""Recruitment domain entity markers."""

from enum import Enum


class RecAggregate(str, Enum):
{agg_lines}
''',
    )


def gen_models() -> None:
    for name, content in MODELS.items():
        w(REC / "models" / f"{name}.py", content)
    init_imports = "\n".join(
        f"from modules.recruitment.models.{k} import {CLASS_MAP[k]}" for k in CLASS_MAP
    )
    all_list = ",\n    ".join(f'"{CLASS_MAP[k]}"' for k in CLASS_MAP)
    w(
        REC / "models" / "__init__.py",
        f'''"""Recruitment ORM models."""

{init_imports}

__all__ = [
    {all_list},
]
''',
    )


def gen_migrations() -> None:
    w(
        ALEMBIC / "0201_create_recruitment_schema.py",
        '''"""Create recruitment schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0201_create_recruitment_schema"
down_revision: str | None = "0200_seed_payroll_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS recruitment")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS recruitment CASCADE")
''',
    )
    for rev, target, down in MIGRATIONS:
        if target == "schema" or (isinstance(target, str) and target.startswith("seed")):
            continue
        if isinstance(target, list):
            imports = "\n".join(
                f"from modules.recruitment.models.{m} import {CLASS_MAP[m]}  # noqa: F401"
                for m in target
            )
            creates = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.create(bind=op.get_bind(), checkfirst=True)" for m in target
            )
            drops = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.drop(bind=op.get_bind(), checkfirst=True)"
                for m in reversed(target)
            )
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create recruitment document tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

{imports}

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {creates}


def downgrade() -> None:
    {drops}
''',
            )
        else:
            cls = CLASS_MAP[target]
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create {cls} table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.recruitment.models.{target} import {cls}  # noqa: F401

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {cls}.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    {cls}.__table__.drop(bind=op.get_bind(), checkfirst=True)
''',
            )


def repo_template(module: str, cls: str, name: str, branch: bool) -> str:
    return f'''"""Recruitment {cls} repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.recruitment.models import {cls}
from modules.recruitment.repository.base import RecScopedRepository, utcnow


class {name}Repository(RecScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls} | None:
        stmt = select({cls}).where({cls}.id == row_id, {cls}.is_deleted.is_(False))
        stmt = self.apply_rec_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select({cls}).where(
            {cls}.company_id == company_id,
            {cls}.is_deleted.is_(False),
        )
        stmt = self.apply_rec_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> {cls}:
        row = {cls}(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> {cls} | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        if hasattr(row, "version"):
            row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
'''


ENGINE_BODIES: dict[str, str] = {
    "JobRequisition": '''
class JobRequisitionEngine:
    def submit(self, row) -> None:
        if row.status != JobRequisitionStatus.DRAFT.value:
            raise InvalidJobRequisitionState("Only draft requisitions can be submitted")
        row.status = JobRequisitionStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != JobRequisitionStatus.SUBMITTED.value:
            raise InvalidJobRequisitionState("Only submitted requisitions can be approved")
        row.status = JobRequisitionStatus.APPROVED.value

    def open(self, row) -> None:
        if row.status not in {JobRequisitionStatus.APPROVED.value, JobRequisitionStatus.ON_HOLD.value}:
            raise InvalidJobRequisitionState("Requisition not openable")
        row.status = JobRequisitionStatus.OPEN.value

    def fill(self, row) -> None:
        if row.status != JobRequisitionStatus.OPEN.value:
            raise InvalidJobRequisitionState("Only open requisitions can be filled")
        row.status = JobRequisitionStatus.FILLED.value

    def close(self, row) -> None:
        if row.status not in {JobRequisitionStatus.OPEN.value, JobRequisitionStatus.FILLED.value}:
            raise InvalidJobRequisitionState("Requisition not closable")
        row.status = JobRequisitionStatus.CLOSED.value

    def hold(self, row) -> None:
        if row.status not in {JobRequisitionStatus.OPEN.value, JobRequisitionStatus.APPROVED.value}:
            raise InvalidJobRequisitionState("Requisition not holdable")
        row.status = JobRequisitionStatus.ON_HOLD.value

    def cancel(self, row) -> None:
        if row.status in {JobRequisitionStatus.CLOSED.value, JobRequisitionStatus.CANCELLED.value}:
            raise InvalidJobRequisitionState("Requisition already terminal")
        row.status = JobRequisitionStatus.CANCELLED.value

    def reject(self, row) -> None:
        if row.status != JobRequisitionStatus.SUBMITTED.value:
            raise InvalidJobRequisitionState("Only submitted requisitions can be rejected")
        row.status = JobRequisitionStatus.REJECTED.value
''',
    "JobPosting": '''
class JobPostingEngine:
    def publish(self, row) -> None:
        if row.status not in {JobPostingStatus.DRAFT.value, JobPostingStatus.PAUSED.value}:
            raise InvalidJobPostingState("Posting not publishable")
        row.status = JobPostingStatus.PUBLISHED.value

    def pause(self, row) -> None:
        if row.status != JobPostingStatus.PUBLISHED.value:
            raise InvalidJobPostingState("Only published postings can be paused")
        row.status = JobPostingStatus.PAUSED.value

    def close(self, row) -> None:
        if row.status not in {JobPostingStatus.PUBLISHED.value, JobPostingStatus.PAUSED.value}:
            raise InvalidJobPostingState("Posting not closable")
        row.status = JobPostingStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status == JobPostingStatus.CANCELLED.value:
            raise InvalidJobPostingState("Posting already cancelled")
        row.status = JobPostingStatus.CANCELLED.value
''',
    "RecruitmentSource": '''
class RecruitmentSourceEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
        row.is_active = False
''',
    "Recruiter": '''
class RecruiterEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "Candidate": '''
class CandidateEngine:
    def advance_to_applied(self, row) -> None:
        row.status = CandidateStatus.APPLIED.value

    def advance_to_screening(self, row) -> None:
        row.status = CandidateStatus.SCREENING.value

    def advance_to_interview(self, row) -> None:
        row.status = CandidateStatus.INTERVIEW.value

    def advance_to_selected(self, row) -> None:
        row.status = CandidateStatus.SELECTED.value

    def advance_to_offered(self, row) -> None:
        row.status = CandidateStatus.OFFERED.value

    def mark_hired(self, row) -> None:
        row.status = CandidateStatus.HIRED.value

    def reject(self, row) -> None:
        row.status = CandidateStatus.REJECTED.value

    def hold(self, row) -> None:
        row.status = CandidateStatus.ON_HOLD.value

    def withdraw(self, row) -> None:
        row.status = CandidateStatus.WITHDRAWN.value

    def blacklist(self, row) -> None:
        row.status = CandidateStatus.BLACKLISTED.value
''',
    "CandidateDocument": '''
class CandidateDocumentEngine:
    def verify(self, row) -> None:
        row.status = CandidateDocumentStatus.VERIFIED.value
        row.verified_flag = True

    def reject(self, row) -> None:
        row.status = CandidateDocumentStatus.REJECTED.value

    def archive(self, row) -> None:
        row.status = CandidateDocumentStatus.ARCHIVED.value
''',
    "Resume": '''
class ResumeEngine:
    def supersede(self, row) -> None:
        row.status = ResumeStatus.SUPERSEDED.value
        row.is_primary = False

    def archive(self, row) -> None:
        row.status = ResumeStatus.ARCHIVED.value
''',
    "Application": '''
class ApplicationEngine:
    def advance(self, row, *, stage: str) -> None:
        allowed = {
            ApplicationStatus.APPLIED.value: ApplicationStatus.SCREENING.value,
            ApplicationStatus.SCREENING.value: ApplicationStatus.INTERVIEW.value,
            ApplicationStatus.INTERVIEW.value: ApplicationStatus.SELECTED.value,
            ApplicationStatus.SELECTED.value: ApplicationStatus.OFFER.value,
            ApplicationStatus.OFFER.value: ApplicationStatus.HIRED.value,
        }
        if row.status not in allowed or allowed[row.status] != stage:
            raise InvalidApplicationState("Invalid application stage transition")
        row.status = stage
        row.current_stage_code = stage

    def reject(self, row, *, reason: str | None = None) -> None:
        row.status = ApplicationStatus.REJECTED.value
        row.rejection_reason = reason

    def hold(self, row) -> None:
        row.status = ApplicationStatus.ON_HOLD.value

    def withdraw(self, row) -> None:
        row.status = ApplicationStatus.WITHDRAWN.value
''',
    "ApplicationStage": '''
class ApplicationStageEngine:
    def complete(self, row) -> None:
        row.status = ApplicationStageStatus.COMPLETED.value

    def skip(self, row) -> None:
        row.status = ApplicationStageStatus.SKIPPED.value

    def cancel(self, row) -> None:
        row.status = ApplicationStageStatus.CANCELLED.value
''',
    "Interview": '''
class InterviewEngine:
    def schedule(self, row) -> None:
        row.status = InterviewStatus.SCHEDULED.value
        row.result = "pending"

    def complete(self, row) -> None:
        if row.status != InterviewStatus.SCHEDULED.value:
            raise InvalidInterviewState("Only scheduled interviews can complete")
        row.status = InterviewStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = InterviewStatus.CANCELLED.value

    def mark_no_show(self, row) -> None:
        row.status = InterviewStatus.NO_SHOW.value
''',
    "InterviewFeedback": '''
class InterviewFeedbackEngine:
    def submit(self, row) -> None:
        if row.status != InterviewFeedbackStatus.DRAFT.value:
            raise InvalidInterviewFeedbackState("Only draft feedback can be submitted")
        row.status = InterviewFeedbackStatus.SUBMITTED.value

    def lock(self, row) -> None:
        if row.status != InterviewFeedbackStatus.SUBMITTED.value:
            raise InvalidInterviewFeedbackState("Only submitted feedback can be locked")
        row.status = InterviewFeedbackStatus.LOCKED.value
''',
    "Offer": '''
class OfferEngine:
    def submit(self, row) -> None:
        if row.status != OfferStatus.DRAFT.value:
            raise InvalidOfferState("Only draft offers can be submitted")
        row.status = OfferStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != OfferStatus.SUBMITTED.value:
            raise InvalidOfferState("Only submitted offers can be approved")
        row.status = OfferStatus.APPROVED.value

    def send(self, row) -> None:
        if row.status != OfferStatus.APPROVED.value:
            raise InvalidOfferState("Only approved offers can be sent")
        row.status = OfferStatus.SENT.value

    def accept(self, row) -> None:
        if row.status != OfferStatus.SENT.value:
            raise InvalidOfferState("Only sent offers can be accepted")
        row.status = OfferStatus.ACCEPTED.value

    def reject(self, row) -> None:
        row.status = OfferStatus.REJECTED.value

    def expire(self, row) -> None:
        row.status = OfferStatus.EXPIRED.value

    def withdraw(self, row) -> None:
        row.status = OfferStatus.WITHDRAWN.value

    def cancel(self, row) -> None:
        row.status = OfferStatus.CANCELLED.value
''',
    "OfferApproval": '''
class OfferApprovalEngine:
    def complete(self, row) -> None:
        row.status = OfferApprovalStatus.COMPLETED.value

    def skip(self, row) -> None:
        row.status = OfferApprovalStatus.SKIPPED.value

    def cancel(self, row) -> None:
        row.status = OfferApprovalStatus.CANCELLED.value
''',
    "BackgroundVerification": '''
class BackgroundVerificationEngine:
    def submit(self, row) -> None:
        if row.status != BackgroundVerificationStatus.DRAFT.value:
            raise InvalidBackgroundVerificationState("Only draft BGV can be submitted")
        row.status = BackgroundVerificationStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status not in {
            BackgroundVerificationStatus.SUBMITTED.value,
            BackgroundVerificationStatus.IN_PROGRESS.value,
        }:
            raise InvalidBackgroundVerificationState("BGV not approvable")
        row.status = BackgroundVerificationStatus.CLEARED.value
        row.result = "clear"

    def start_progress(self, row) -> None:
        row.status = BackgroundVerificationStatus.IN_PROGRESS.value

    def fail(self, row) -> None:
        row.status = BackgroundVerificationStatus.FAILED.value
        row.result = "adverse"

    def waive(self, row) -> None:
        row.status = BackgroundVerificationStatus.WAIVED.value

    def cancel(self, row) -> None:
        row.status = BackgroundVerificationStatus.CANCELLED.value
''',
    "ReferenceCheck": '''
class ReferenceCheckEngine:
    def contact(self, row) -> None:
        row.status = ReferenceCheckStatus.CONTACTED.value

    def complete(self, row) -> None:
        row.status = ReferenceCheckStatus.COMPLETED.value

    def decline(self, row) -> None:
        row.status = ReferenceCheckStatus.DECLINED.value

    def cancel(self, row) -> None:
        row.status = ReferenceCheckStatus.CANCELLED.value
''',
    "TalentPool": '''
class TalentPoolEngine:
    def remove(self, row) -> None:
        row.status = TalentPoolStatus.REMOVED.value

    def mark_hired_out(self, row) -> None:
        row.status = TalentPoolStatus.HIRED_OUT.value
''',
    "CandidateNote": '''
class CandidateNoteEngine:
    def archive(self, row) -> None:
        row.status = CandidateNoteStatus.ARCHIVED.value
''',
    "Onboarding": '''
class OnboardingEngine:
    def submit(self, row) -> None:
        if row.status != OnboardingStatus.DRAFT.value:
            raise InvalidOnboardingState("Only draft onboarding can be submitted")
        row.status = OnboardingStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != OnboardingStatus.SUBMITTED.value:
            raise InvalidOnboardingState("Only submitted onboarding can be approved")
        row.status = OnboardingStatus.IN_PROGRESS.value

    def start(self, row) -> None:
        row.status = OnboardingStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status != OnboardingStatus.IN_PROGRESS.value:
            raise InvalidOnboardingState("Only in-progress onboarding can complete")
        if row.employee_id is None:
            raise InvalidOnboardingState("Employee must exist before completion")
        row.status = OnboardingStatus.COMPLETED.value

    def fail(self, row) -> None:
        row.status = OnboardingStatus.FAILED.value

    def cancel(self, row) -> None:
        row.status = OnboardingStatus.CANCELLED.value
''',
    "OnboardingTask": '''
class OnboardingTaskEngine:
    def start(self, row) -> None:
        row.status = OnboardingTaskStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        row.status = OnboardingTaskStatus.COMPLETED.value

    def waive(self, row) -> None:
        row.status = OnboardingTaskStatus.WAIVED.value

    def block(self, row) -> None:
        row.status = OnboardingTaskStatus.BLOCKED.value

    def cancel(self, row) -> None:
        row.status = OnboardingTaskStatus.CANCELLED.value
''',
    "RecruitmentReport": '''
class RecruitmentReportEngine:
    def finalize(self, row) -> None:
        if row.status != RecruitmentReportStatus.DRAFT.value:
            raise InvalidRecruitmentReportState("Only draft reports can finalize")
        row.status = RecruitmentReportStatus.FINALIZED.value
''',
}

ENGINE_IMPORTS = '''
from modules.recruitment.domain.enums import (
    ActiveInactive,
    ApplicationStageStatus,
    ApplicationStatus,
    BackgroundVerificationStatus,
    CandidateDocumentStatus,
    CandidateNoteStatus,
    CandidateStatus,
    InterviewFeedbackStatus,
    InterviewStatus,
    JobPostingStatus,
    JobRequisitionStatus,
    OfferApprovalStatus,
    OfferStatus,
    OnboardingStatus,
    OnboardingTaskStatus,
    ReferenceCheckStatus,
    RecruitmentReportStatus,
    ResumeStatus,
    TalentPoolStatus,
)
from modules.recruitment.domain.exceptions import (
    InvalidApplicationStageState,
    InvalidApplicationState,
    InvalidBackgroundVerificationState,
    InvalidCandidateDocumentState,
    InvalidCandidateNoteState,
    InvalidCandidateState,
    InvalidInterviewFeedbackState,
    InvalidInterviewState,
    InvalidJobPostingState,
    InvalidJobRequisitionState,
    InvalidOfferApprovalState,
    InvalidOfferState,
    InvalidOnboardingState,
    InvalidOnboardingTaskState,
    InvalidRecruiterState,
    InvalidRecruitmentReportState,
    InvalidRecruitmentSourceState,
    InvalidReferenceCheckState,
    InvalidResumeState,
    InvalidTalentPoolState,
)
'''

ENGINE_FILE_MAP = {t[2]: t[0] for t in TABLES}


def gen_repos() -> None:
    w(
        REC / "repository" / "base.py",
        '''"""Recruitment repository base utilities."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RecScopedRepository(OrgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    @staticmethod
    def apply_rec_filter(stmt, model, ctx: TenantContext, *, branch_scoped: bool = False):
        stmt = RecScopedRepository.apply_tenant_filter(stmt, model, ctx)
        if ctx.company_id and ctx.user_type not in {"super_admin", "tenant_admin"}:
            stmt = stmt.where(model.company_id == ctx.company_id)
        if (
            branch_scoped
            and ctx.branch_id
            and ctx.user_type not in {"super_admin", "tenant_admin"}
            and hasattr(model, "branch_id")
        ):
            stmt = stmt.where(model.branch_id == ctx.branch_id)
        return stmt

    @staticmethod
    def resolve_company_id(ctx: TenantContext, company_id: UUID | None) -> UUID:
        if company_id is not None:
            RecScopedRepository.ensure_company_access(ctx, company_id)
            return company_id
        if ctx.company_id is None:
            raise ForbiddenException("Company context required")
        return ctx.company_id
''',
    )
    w(
        REC / "repository" / "code_sequence_repository.py",
        '''"""Recruitment document code sequences."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.recruitment.domain.enums import CODE_PREFIXES, RecEntityType


class CodeSequenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_code(self, entity: RecEntityType, company_id: UUID, model, code_column: str) -> str:
        prefix, width, include_year = CODE_PREFIXES[entity]
        year = datetime.now(timezone.utc).year
        full_prefix = f"{prefix}{year}-" if include_year else prefix
        stmt = select(getattr(model, code_column)).where(
            model.company_id == company_id,
            getattr(model, code_column).like(f"{full_prefix}%"),
            model.is_deleted.is_(False),
        )
        existing = list(self.db.scalars(stmt).all())
        seq = 1
        if existing:
            nums = []
            for code in existing:
                try:
                    nums.append(int(str(code).rsplit("-", 1)[-1]))
                except ValueError:
                    continue
            if nums:
                seq = max(nums) + 1
        return f"{full_prefix}{seq:0{width}d}"
''',
    )
    for module, cls, name, branch in TABLES:
        w(REC / "repository" / f"{module}_repository.py", repo_template(module, cls, name, branch))


def gen_engines() -> None:
    for eng_name, body in ENGINE_BODIES.items():
        fname = ENGINE_FILE_MAP[eng_name]
        w(
            REC / "service" / "engines" / f"{fname}_engine.py",
            f'"""{eng_name} lifecycle engine."""\n{ENGINE_IMPORTS}\n{body}\n',
        )
    lines = [
        f"from modules.recruitment.service.engines.{ENGINE_FILE_MAP[n]}_engine import {n}Engine"
        for n in ENGINE_BODIES
    ]
    all_names = ",\n    ".join(f'"{n}Engine"' for n in ENGINE_BODIES)
    w(
        REC / "service" / "engines" / "__init__.py",
        '"""Recruitment business engines."""\n\n'
        + "\n".join(lines)
        + f"\n\n__all__ = [\n    {all_names},\n]\n",
    )


def catalog_service(name: str, cls: str, repo_name: str, entity: str, branch: bool) -> str:
    branch_arg = ", *, branch_id: UUID | None = None" if branch else ""
    branch_fields = (
        "\n        if branch_id is not None:\n"
        "            self._scope.validate_branch_access(ctx, branch_id)\n"
        if branch
        else ""
    )
    branch_create = "branch_id=branch_id," if branch else ""
    return f'''"""{name} application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.recruitment.models import {cls}
from modules.recruitment.repository.{entity}_repository import {repo_name}Repository
from modules.recruitment.service.engines import {repo_name}Engine
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class {name}Service:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = RecruitmentScopeValidator(db)
        self._engine = {repo_name}Engine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls}:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("{name} not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None{branch_arg}, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
{branch_fields}
        row = self._repo.create(ctx, company_id=cid, {branch_create} **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="rec_{entity}",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("{name} not found")
        return row
'''


def gen_services() -> None:
    w(
        REC / "service" / "recruitment_scope_validator.py",
        '''"""Recruitment scope validator."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.recruitment.repository.base import RecScopedRepository


class RecruitmentScopeValidator(RecScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self.ensure_company_access(ctx, company_id)

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self.ensure_branch_access(ctx, branch_id)
''',
    )
    w(
        REC / "service" / "document_number_service.py",
        '''"""Recruitment document numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.recruitment.domain.enums import RecEntityType
from modules.recruitment.repository.code_sequence_repository import CodeSequenceRepository


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: RecEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
''',
    )

    svc_map = [(t[2], t[1], t[2], t[0], t[3]) for t in TABLES]
    for name, cls, repo, mod, branch in svc_map:
        if name in {
            "JobRequisition",
            "JobPosting",
            "Offer",
            "BackgroundVerification",
            "Onboarding",
            "Application",
            "Interview",
            "Candidate",
        }:
            continue
        w(REC / "service" / f"{mod}_service.py", catalog_service(name, cls, repo, mod, branch))

    w(
        REC / "service" / "job_requisition_service.py",
        '''"""Job requisition service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.recruitment.domain.enums import RecEntityType
from modules.recruitment.models import RecJobRequisition
from modules.recruitment.repository.job_requisition_repository import JobRequisitionRepository
from modules.recruitment.service.document_number_service import DocumentNumberService
from modules.recruitment.service.engines import JobRequisitionEngine
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class JobRequisitionService:
    def __init__(self, db: Session) -> None:
        self._repo = JobRequisitionRepository(db)
        self._scope = RecruitmentScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = JobRequisitionEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> RecJobRequisition:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Job requisition not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(RecEntityType.JOB_REQUISITION, cid, RecJobRequisition, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Job requisition not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)
''',
    )

    w(
        REC / "service" / "job_posting_service.py",
        '''"""Job posting service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.recruitment.domain.enums import RecEntityType
from modules.recruitment.models import RecJobPosting
from modules.recruitment.repository.job_posting_repository import JobPostingRepository
from modules.recruitment.service.document_number_service import DocumentNumberService
from modules.recruitment.service.engines import JobPostingEngine
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class JobPostingService:
    def __init__(self, db: Session) -> None:
        self._repo = JobPostingRepository(db)
        self._scope = RecruitmentScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = JobPostingEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> RecJobPosting:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Job posting not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(RecEntityType.JOB_POSTING, cid, RecJobPosting, "document_number")
        return self._repo.create(ctx, company_id=cid, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Job posting not found")
        return row

    def publish(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.publish(row)
        return self._repo.update(ctx, row_id, status=row.status)
''',
    )

    w(
        REC / "service" / "candidate_service.py",
        '''"""Candidate service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.recruitment.domain.enums import RecEntityType
from modules.recruitment.models import RecCandidate
from modules.recruitment.repository.candidate_repository import CandidateRepository
from modules.recruitment.service.document_number_service import DocumentNumberService
from modules.recruitment.service.engines import CandidateEngine
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class CandidateService:
    def __init__(self, db: Session) -> None:
        self._repo = CandidateRepository(db)
        self._scope = RecruitmentScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = CandidateEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> RecCandidate:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Candidate not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        code = self._numbers.generate(RecEntityType.CANDIDATE, cid, RecCandidate, "candidate_code")
        return self._repo.create(ctx, company_id=cid, candidate_code=code, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Candidate not found")
        return row
''',
    )

    w(
        REC / "service" / "application_service.py",
        '''"""Application pipeline service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.recruitment.domain.enums import RecEntityType
from modules.recruitment.models import RecApplication
from modules.recruitment.repository.application_repository import ApplicationRepository
from modules.recruitment.service.document_number_service import DocumentNumberService
from modules.recruitment.service.engines import ApplicationEngine
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class ApplicationService:
    def __init__(self, db: Session) -> None:
        self._repo = ApplicationRepository(db)
        self._scope = RecruitmentScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = ApplicationEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> RecApplication:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Application not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(RecEntityType.APPLICATION, cid, RecApplication, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Application not found")
        return row

    def advance(self, ctx: TenantContext, row_id: UUID, *, stage: str):
        row = self.get(ctx, row_id)
        self._engine.advance(row, stage=stage)
        return self._repo.update(ctx, row_id, status=row.status, current_stage_code=row.current_stage_code)

    def reject(self, ctx: TenantContext, row_id: UUID, *, reason: str | None = None):
        row = self.get(ctx, row_id)
        self._engine.reject(row, reason=reason)
        return self._repo.update(ctx, row_id, status=row.status, rejection_reason=row.rejection_reason)
''',
    )

    w(
        REC / "service" / "interview_service.py",
        '''"""Interview service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.recruitment.domain.enums import RecEntityType
from modules.recruitment.models import RecInterview
from modules.recruitment.repository.interview_repository import InterviewRepository
from modules.recruitment.service.document_number_service import DocumentNumberService
from modules.recruitment.service.engines import InterviewEngine
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class InterviewService:
    def __init__(self, db: Session) -> None:
        self._repo = InterviewRepository(db)
        self._scope = RecruitmentScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = InterviewEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> RecInterview:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Interview not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(RecEntityType.INTERVIEW, cid, RecInterview, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Interview not found")
        return row

    def schedule(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.schedule(row)
        return self._repo.update(ctx, row_id, status=row.status, result=row.result)

    def complete(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.complete(row)
        return self._repo.update(ctx, row_id, status=row.status)
''',
    )

    w(
        REC / "service" / "offer_service.py",
        '''"""Offer service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.recruitment.domain.enums import RecEntityType
from modules.recruitment.models import RecOffer
from modules.recruitment.repository.offer_repository import OfferRepository
from modules.recruitment.service.document_number_service import DocumentNumberService
from modules.recruitment.service.engines import OfferEngine
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class OfferService:
    def __init__(self, db: Session) -> None:
        self._repo = OfferRepository(db)
        self._scope = RecruitmentScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = OfferEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> RecOffer:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Offer not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(RecEntityType.OFFER, cid, RecOffer, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Offer not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def send(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.send(row)
        updated = self._repo.update(ctx, row_id, status=row.status)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="rec_offer",
            entity_id=row_id,
            operation="send",
            performed_by=ctx.user_id,
        )
        return updated
''',
    )

    w(
        REC / "service" / "background_verification_service.py",
        '''"""Background verification service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.recruitment.domain.enums import RecEntityType
from modules.recruitment.models import RecBackgroundVerification
from modules.recruitment.repository.background_verification_repository import BackgroundVerificationRepository
from modules.recruitment.service.document_number_service import DocumentNumberService
from modules.recruitment.service.engines import BackgroundVerificationEngine
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class BackgroundVerificationService:
    def __init__(self, db: Session) -> None:
        self._repo = BackgroundVerificationRepository(db)
        self._scope = RecruitmentScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = BackgroundVerificationEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> RecBackgroundVerification:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Background verification not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(
            RecEntityType.BACKGROUND_VERIFICATION,
            cid,
            RecBackgroundVerification,
            "document_number",
        )
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Background verification not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status, result=row.result)
''',
    )

    w(
        REC / "service" / "onboarding_service.py",
        '''"""Onboarding service — employee conversion via adapters only."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.recruitment.adapters.hr_port import RecruitmentHrAdapter
from modules.recruitment.adapters.master_data_port import RecruitmentMasterDataAdapter
from modules.recruitment.domain.enums import OnboardingStatus, PayrollHandoffStatus, RecEntityType
from modules.recruitment.domain.exceptions import InvalidOnboardingState
from modules.recruitment.models import RecOnboarding
from modules.recruitment.repository.candidate_repository import CandidateRepository
from modules.recruitment.repository.offer_repository import OfferRepository
from modules.recruitment.repository.onboarding_repository import OnboardingRepository
from modules.recruitment.service.document_number_service import DocumentNumberService
from modules.recruitment.service.engines import CandidateEngine, OnboardingEngine
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class OnboardingService:
    def __init__(self, db: Session) -> None:
        self._repo = OnboardingRepository(db)
        self._candidates = CandidateRepository(db)
        self._offers = OfferRepository(db)
        self._scope = RecruitmentScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = OnboardingEngine()
        self._candidate_engine = CandidateEngine()
        self._master = RecruitmentMasterDataAdapter(db)
        self._hr = RecruitmentHrAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> RecOnboarding:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Onboarding not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(RecEntityType.ONBOARDING, cid, RecOnboarding, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Onboarding not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def complete(self, ctx: TenantContext, row_id: UUID, *, designation: str):
        """Critical hire completion — Master Data + HR adapters only."""
        row = self.get(ctx, row_id)
        if row.status != OnboardingStatus.IN_PROGRESS.value:
            raise InvalidOnboardingState("Only in-progress onboarding can complete")

        candidate = self._candidates.get(ctx, row.candidate_id)
        offer = self._offers.get(ctx, row.offer_id)
        if candidate is None or offer is None:
            raise NotFoundException("Candidate or offer not found for onboarding")

        employee = self._master.create_employee(
            ctx,
            branch_id=row.branch_id,
            department_id=row.department_id,
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            email=candidate.email,
            mobile=candidate.mobile or "",
            designation=designation,
            date_of_joining=offer.joining_date,
            company_id=row.company_id,
        )

        row.employee_id = employee.id
        self._candidate_engine.mark_hired(candidate)

        employment = self._hr.create_employment(
            ctx,
            branch_id=row.branch_id,
            employee_id=employee.id,
            company_id=row.company_id,
            department_id=row.department_id,
            designation_id=row.designation_id,
            joining_date=offer.joining_date,
        )
        row.hr_employment_request_id = employment.id
        row.payroll_handoff_status = PayrollHandoffStatus.PENDING.value

        self._engine.complete(row)
        updated = self._repo.update(
            ctx,
            row_id,
            status=row.status,
            employee_id=row.employee_id,
            hr_employment_request_id=row.hr_employment_request_id,
            payroll_handoff_status=row.payroll_handoff_status,
            actual_joining_date=offer.joining_date,
        )
        self._candidates.update(ctx, candidate.id, employee_id=employee.id, status=candidate.status)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="rec_onboarding",
            entity_id=row_id,
            operation="complete",
            performed_by=ctx.user_id,
        )
        return updated
''',
    )

    w(
        REC / "service" / "integration_service.py",
        '''"""Recruitment integration facade."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.recruitment.adapters.hr_port import RecruitmentHrAdapter
from modules.recruitment.adapters.master_data_port import RecruitmentMasterDataAdapter
from modules.recruitment.adapters.organization_port import RecruitmentOrganizationAdapter
from modules.recruitment.adapters.payroll_port import RecruitmentPayrollAdapter
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class RecruitmentIntegrationService:
    def __init__(self, db: Session) -> None:
        self._scope = RecruitmentScopeValidator(db)
        self._master = RecruitmentMasterDataAdapter(db)
        self._org = RecruitmentOrganizationAdapter(db)
        self._hr = RecruitmentHrAdapter(db)
        self._payroll = RecruitmentPayrollAdapter(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        return self._org.get_department(ctx, department_id)

    def get_designation(self, ctx: TenantContext, designation_id: UUID):
        return self._hr.get_designation(ctx, designation_id)

    def get_salary_structure(self, ctx: TenantContext, salary_structure_id: UUID):
        return self._payroll.get_salary_structure(ctx, salary_structure_id)
''',
    )

    w(
        REC / "service" / "application_service_facade.py",
        '''"""Recruitment application service facade."""

from sqlalchemy.orm import Session

from modules.recruitment.service.application_service import ApplicationService
from modules.recruitment.service.background_verification_service import BackgroundVerificationService
from modules.recruitment.service.candidate_document_service import CandidateDocumentService
from modules.recruitment.service.candidate_note_service import CandidateNoteService
from modules.recruitment.service.candidate_service import CandidateService
from modules.recruitment.service.integration_service import RecruitmentIntegrationService
from modules.recruitment.service.interview_feedback_service import InterviewFeedbackService
from modules.recruitment.service.interview_service import InterviewService
from modules.recruitment.service.job_posting_service import JobPostingService
from modules.recruitment.service.job_requisition_service import JobRequisitionService
from modules.recruitment.service.offer_approval_service import OfferApprovalService
from modules.recruitment.service.offer_service import OfferService
from modules.recruitment.service.onboarding_service import OnboardingService
from modules.recruitment.service.onboarding_task_service import OnboardingTaskService
from modules.recruitment.service.recruiter_service import RecruiterService
from modules.recruitment.service.recruitment_report_service import RecruitmentReportService
from modules.recruitment.service.recruitment_source_service import RecruitmentSourceService
from modules.recruitment.service.reference_check_service import ReferenceCheckService
from modules.recruitment.service.resume_service import ResumeService
from modules.recruitment.service.talent_pool_service import TalentPoolService


class RecruitmentApplicationService:
    def __init__(self, db: Session) -> None:
        self.requisitions = JobRequisitionService(db)
        self.postings = JobPostingService(db)
        self.sources = RecruitmentSourceService(db)
        self.recruiters = RecruiterService(db)
        self.candidates = CandidateService(db)
        self.documents = CandidateDocumentService(db)
        self.resumes = ResumeService(db)
        self.applications = ApplicationService(db)
        self.interviews = InterviewService(db)
        self.feedback = InterviewFeedbackService(db)
        self.offers = OfferService(db)
        self.offer_approvals = OfferApprovalService(db)
        self.verifications = BackgroundVerificationService(db)
        self.references = ReferenceCheckService(db)
        self.talent_pools = TalentPoolService(db)
        self.notes = CandidateNoteService(db)
        self.onboarding = OnboardingService(db)
        self.onboarding_tasks = OnboardingTaskService(db)
        self.reports = RecruitmentReportService(db)
        self.integration = RecruitmentIntegrationService(db)
''',
    )

    service_exports = [
        "ApplicationService",
        "ApplicationStageService",
        "BackgroundVerificationService",
        "CandidateDocumentService",
        "CandidateNoteService",
        "CandidateService",
        "InterviewFeedbackService",
        "InterviewService",
        "JobPostingService",
        "JobRequisitionService",
        "OfferApprovalService",
        "OfferService",
        "OnboardingService",
        "OnboardingTaskService",
        "RecruiterService",
        "RecruitmentApplicationService",
        "RecruitmentIntegrationService",
        "RecruitmentReportService",
        "RecruitmentSourceService",
        "ReferenceCheckService",
        "ResumeService",
        "TalentPoolService",
    ]
    import_lines = [
        f"from modules.recruitment.service.{t[0]}_service import {t[2]}Service"
        for t in TABLES
        if t[2]
        not in {
            "JobRequisition",
            "JobPosting",
            "Candidate",
            "Application",
            "Interview",
            "Offer",
            "BackgroundVerification",
            "Onboarding",
        }
    ]
    import_lines += [
        "from modules.recruitment.service.application_service import ApplicationService",
        "from modules.recruitment.service.application_service_facade import RecruitmentApplicationService",
        "from modules.recruitment.service.background_verification_service import BackgroundVerificationService",
        "from modules.recruitment.service.candidate_service import CandidateService",
        "from modules.recruitment.service.integration_service import RecruitmentIntegrationService",
        "from modules.recruitment.service.interview_service import InterviewService",
        "from modules.recruitment.service.job_posting_service import JobPostingService",
        "from modules.recruitment.service.job_requisition_service import JobRequisitionService",
        "from modules.recruitment.service.offer_service import OfferService",
        "from modules.recruitment.service.onboarding_service import OnboardingService",
    ]
    w(
        REC / "service" / "__init__.py",
        '"""Recruitment services."""\n\n'
        + "\n".join(sorted(set(import_lines)))
        + "\n\n__all__ = [\n    "
        + ",\n    ".join(f'"{n}"' for n in service_exports)
        + ",\n]\n",
    )


def gen_adapters() -> None:
    w(
        REC / "adapters" / "master_data_port.py",
        '''"""Master Data port — create employee only at onboarding complete."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.service.employee_service import EmployeeService


class RecruitmentMasterDataAdapter:
    def __init__(self, db: Session) -> None:
        self._employees = EmployeeService(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._employees.get_employee(ctx, employee_id)

    def create_employee(
        self,
        ctx: TenantContext,
        *,
        branch_id: UUID,
        department_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        mobile: str,
        designation: str,
        date_of_joining: date,
        company_id: UUID | None = None,
    ):
        return self._employees.create_employee(
            ctx,
            company_id=company_id,
            branch_id=branch_id,
            department_id=department_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            designation=designation,
            date_of_joining=date_of_joining,
        )
''',
    )
    w(
        REC / "adapters" / "organization_port.py",
        '''"""Organization port — read org_department only."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.hierarchy_repository import DepartmentRepository


class RecruitmentOrganizationAdapter:
    def __init__(self, db: Session) -> None:
        self._departments = DepartmentRepository(db)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        department = self._departments.get_by_id(ctx, department_id)
        if department is None:
            raise NotFoundException("Department not found")
        return department
''',
    )
    w(
        REC / "adapters" / "hr_port.py",
        '''"""HR port — employment request via EmploymentService; no hr_* ORM writes."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.hr.service.designation_service import DesignationService
from modules.hr.service.employment_service import EmploymentService


class RecruitmentHrAdapter:
    def __init__(self, db: Session) -> None:
        self._employment = EmploymentService(db)
        self._designations = DesignationService(db)

    def create_employment(
        self,
        ctx: TenantContext,
        *,
        branch_id: UUID,
        employee_id: UUID,
        company_id: UUID | None = None,
        department_id: UUID | None = None,
        designation_id: UUID | None = None,
        joining_date: date | None = None,
        **fields,
    ):
        payload = dict(fields)
        if department_id is not None:
            payload["department_id"] = department_id
        if designation_id is not None:
            payload["designation_id"] = designation_id
        if joining_date is not None:
            payload["joining_date"] = joining_date
        return self._employment.create(
            ctx,
            branch_id=branch_id,
            employee_id=employee_id,
            company_id=company_id,
            **payload,
        )

    def get_designation(self, ctx: TenantContext, designation_id: UUID):
        return self._designations.get(ctx, designation_id)
''',
    )
    w(
        REC / "adapters" / "payroll_port.py",
        '''"""Payroll port — read-only salary structure hints; no pay_* writes."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.repository.salary_structure_repository import SalaryStructureRepository


class RecruitmentPayrollAdapter:
    def __init__(self, db: Session) -> None:
        self._structures = SalaryStructureRepository(db)

    def get_salary_structure(self, ctx: TenantContext, salary_structure_id: UUID):
        row = self._structures.get(ctx, salary_structure_id)
        if row is None:
            raise NotFoundException("Salary structure not found")
        return row
''',
    )
    w(
        REC / "adapters" / "__init__.py",
        '''"""Recruitment adapters."""

from modules.recruitment.adapters.hr_port import RecruitmentHrAdapter
from modules.recruitment.adapters.master_data_port import RecruitmentMasterDataAdapter
from modules.recruitment.adapters.organization_port import RecruitmentOrganizationAdapter
from modules.recruitment.adapters.payroll_port import RecruitmentPayrollAdapter

__all__ = [
    "RecruitmentHrAdapter",
    "RecruitmentMasterDataAdapter",
    "RecruitmentOrganizationAdapter",
    "RecruitmentPayrollAdapter",
]
''',
    )


def gen_permissions() -> None:
    w(
        REC / "permissions.py",
        '''"""Recruitment permission constants per ERD_13 §14."""

RECRUITMENT_PERMISSIONS: list[tuple[str, str, str, str]] = [
    ("recruitment.requisition:read", "recruitment.requisition", "read", "recruitment"),
    ("recruitment.requisition:create", "recruitment.requisition", "create", "recruitment"),
    ("recruitment.requisition:update", "recruitment.requisition", "update", "recruitment"),
    ("recruitment.requisition:submit", "recruitment.requisition", "submit", "recruitment"),
    ("recruitment.requisition:approve", "recruitment.requisition", "approve", "recruitment"),
    ("recruitment.posting:read", "recruitment.posting", "read", "recruitment"),
    ("recruitment.posting:create", "recruitment.posting", "create", "recruitment"),
    ("recruitment.posting:publish", "recruitment.posting", "publish", "recruitment"),
    ("recruitment.posting:close", "recruitment.posting", "close", "recruitment"),
    ("recruitment.candidate:read", "recruitment.candidate", "read", "recruitment"),
    ("recruitment.candidate:create", "recruitment.candidate", "create", "recruitment"),
    ("recruitment.candidate:update", "recruitment.candidate", "update", "recruitment"),
    ("recruitment.application:read", "recruitment.application", "read", "recruitment"),
    ("recruitment.application:create", "recruitment.application", "create", "recruitment"),
    ("recruitment.application:update", "recruitment.application", "update", "recruitment"),
    ("recruitment.application:advance", "recruitment.application", "advance", "recruitment"),
    ("recruitment.application:reject", "recruitment.application", "reject", "recruitment"),
    ("recruitment.interview:read", "recruitment.interview", "read", "recruitment"),
    ("recruitment.interview:create", "recruitment.interview", "create", "recruitment"),
    ("recruitment.interview:schedule", "recruitment.interview", "schedule", "recruitment"),
    ("recruitment.interview:complete", "recruitment.interview", "complete", "recruitment"),
    ("recruitment.offer:read", "recruitment.offer", "read", "recruitment"),
    ("recruitment.offer:create", "recruitment.offer", "create", "recruitment"),
    ("recruitment.offer:submit", "recruitment.offer", "submit", "recruitment"),
    ("recruitment.offer:approve", "recruitment.offer", "approve", "recruitment"),
    ("recruitment.offer:send", "recruitment.offer", "send", "recruitment"),
    ("recruitment.verification:read", "recruitment.verification", "read", "recruitment"),
    ("recruitment.verification:create", "recruitment.verification", "create", "recruitment"),
    ("recruitment.verification:submit", "recruitment.verification", "submit", "recruitment"),
    ("recruitment.verification:approve", "recruitment.verification", "approve", "recruitment"),
    ("recruitment.onboarding:read", "recruitment.onboarding", "read", "recruitment"),
    ("recruitment.onboarding:create", "recruitment.onboarding", "create", "recruitment"),
    ("recruitment.onboarding:submit", "recruitment.onboarding", "submit", "recruitment"),
    ("recruitment.onboarding:approve", "recruitment.onboarding", "approve", "recruitment"),
    ("recruitment.onboarding:complete", "recruitment.onboarding", "complete", "recruitment"),
    ("recruitment.talent_pool:read", "recruitment.talent_pool", "read", "recruitment"),
    ("recruitment.talent_pool:create", "recruitment.talent_pool", "create", "recruitment"),
    ("recruitment.talent_pool:update", "recruitment.talent_pool", "update", "recruitment"),
    ("recruitment.report:read", "recruitment.report", "read", "recruitment"),
    ("recruitment.report:export", "recruitment.report", "export", "recruitment"),
    ("recruitment.recruiter:read", "recruitment.recruiter", "read", "recruitment"),
    ("recruitment.recruiter:create", "recruitment.recruiter", "create", "recruitment"),
    ("recruitment.recruiter:update", "recruitment.recruiter", "update", "recruitment"),
    ("recruitment.source:read", "recruitment.source", "read", "recruitment"),
    ("recruitment.source:create", "recruitment.source", "create", "recruitment"),
    ("recruitment.source:update", "recruitment.source", "update", "recruitment"),
    ("recruitment.note:read", "recruitment.note", "read", "recruitment"),
    ("recruitment.note:create", "recruitment.note", "create", "recruitment"),
    ("recruitment.note:update", "recruitment.note", "update", "recruitment"),
]

RECRUITER_PERMISSIONS = list(
    dict.fromkeys(
        [
            p[0]
            for p in RECRUITMENT_PERMISSIONS
            if p[2] in {"read", "create", "update", "submit", "schedule", "complete", "advance", "reject", "send"}
        ]
    )
)

RECRUITMENT_MANAGER_PERMISSIONS = list(
    dict.fromkeys(
        RECRUITER_PERMISSIONS
        + [
            "recruitment.requisition:approve",
            "recruitment.offer:approve",
            "recruitment.verification:approve",
            "recruitment.posting:publish",
            "recruitment.posting:close",
            "recruitment.source:update",
            "recruitment.recruiter:update",
        ]
    )
)

HR_ONBOARDING_PERMISSIONS = list(
    dict.fromkeys(
        RECRUITMENT_MANAGER_PERMISSIONS
        + [
            "recruitment.onboarding:complete",
            "recruitment.onboarding:approve",
            "recruitment.verification:submit",
        ]
    )
)

HIRING_MANAGER_PERMISSIONS = list(
    dict.fromkeys(
        RECRUITER_PERMISSIONS
        + [
            "recruitment.requisition:submit",
            "recruitment.requisition:approve",
            "recruitment.offer:approve",
            "recruitment.interview:complete",
        ]
    )
)
''',
    )


def gen_api() -> None:
    w(
        REC / "dependencies.py",
        '''"""Recruitment module dependencies."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Query

from database.session import get_db
from modules.foundation.dependencies import get_tenant_context, require_permission
from modules.foundation.domain.value_objects import TenantContext

__all__ = [
    "PaginationParams",
    "get_pagination",
    "get_tenant_context",
    "require_permission",
    "TenantContext",
    "get_db",
    "paginate",
    "extract_update_fields",
]


@dataclass(frozen=True)
class PaginationParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 25,
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


def paginate(items: list, pagination: PaginationParams) -> list:
    return items[pagination.offset : pagination.offset + pagination.page_size]


def extract_update_fields(body) -> dict:
    fields = body.model_dump(exclude_unset=True)
    fields.pop("version", None)
    return fields
''',
    )

    schema_lines = [
        '"""Recruitment Pydantic schemas."""',
        "",
        "from uuid import UUID",
        "",
        "from pydantic import BaseModel, ConfigDict",
        "",
        "",
        "class OrmModel(BaseModel):",
        "    model_config = ConfigDict(from_attributes=True)",
        "",
    ]
    for _, name, _, _, branch in ROUTE_SPECS:
        schema_lines += [
            "",
            f"class {name}Create(BaseModel):",
            "    company_id: UUID | None = None",
        ]
        if branch:
            schema_lines.append("    branch_id: UUID")
        schema_lines += [
            "    status: str | None = None",
            "",
            f"class {name}Update(BaseModel):",
            "    status: str | None = None",
            "    version: int | None = None",
            "",
            f"class {name}Response(OrmModel):",
            "    id: UUID",
            "    company_id: UUID",
            "    status: str",
            "    version: int",
        ]
    schema_lines += [
        "",
        "class OnboardingCompleteRequest(BaseModel):",
        "    designation: str",
    ]
    w(REC / "schemas.py", "\n".join(schema_lines) + "\n")

    router_imports = [
        "from typing import Annotated",
        "from uuid import UUID",
        "",
        "from fastapi import APIRouter, Depends",
        "from sqlalchemy.orm import Session",
        "",
        "from database.session import get_db",
        "from modules.foundation.dependencies import require_permission",
        "from modules.foundation.domain.value_objects import TenantContext",
        "from modules.recruitment.dependencies import PaginationParams, extract_update_fields, get_pagination, paginate",
    ]
    for _, name, _, _, _ in ROUTE_SPECS:
        router_imports.append(
            f"from modules.recruitment.schemas import {name}Create, {name}Response, {name}Update"
        )
    router_imports.append("from modules.recruitment.schemas import OnboardingCompleteRequest")
    router_imports.append("from modules.recruitment.service import (")
    for _, _, svc, _, _ in ROUTE_SPECS:
        router_imports.append(f"    {svc},")
    router_imports += [
        ")",
        "from shared.schemas import APIResponse",
        "",
    ]

    router_defs = []
    route_handlers = []
    for prefix, name, svc, perm, branch in ROUTE_SPECS:
        rname = prefix.replace("-", "_") + "_router"
        router_defs.append(
            f'{rname} = APIRouter(prefix="/{prefix}", tags=["Recruitment - {name}"])'
        )
        read_perm = f"{perm}:read"
        create_perm = f"{perm}:create"
        update_perm = f"{perm}:update" if perm.split(".")[-1] in {
            "requisition",
            "candidate",
            "application",
            "talent_pool",
            "source",
            "recruiter",
            "note",
        } else read_perm
        route_handlers += [
            "",
            f"@{rname}.get(\"\", response_model=APIResponse[list[{name}Response]])",
            f"def list_{prefix.replace('-', '_')}(",
            f"    ctx: Annotated[TenantContext, Depends(require_permission(\"{read_perm}\"))],",
            "    db: Annotated[Session, Depends(get_db)],",
            "    pagination: Annotated[PaginationParams, Depends(get_pagination)],",
            "    company_id: UUID | None = None,",
            "):",
            f"    return APIResponse(message=\"OK\", data=paginate({svc}(db).list(ctx, company_id), pagination))",
            "",
            f"@{rname}.post(\"\", response_model=APIResponse[{name}Response])",
            f"def create_{prefix.replace('-', '_')}(",
            f"    body: {name}Create,",
            f"    ctx: Annotated[TenantContext, Depends(require_permission(\"{create_perm}\"))],",
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f"    return APIResponse(message=\"Created\", data={svc}(db).create(ctx, **body.model_dump()))",
            "",
            f"@{rname}.patch(\"/{{row_id}}\", response_model=APIResponse[{name}Response])",
            f"def update_{prefix.replace('-', '_')}(",
            "    row_id: UUID,",
            f"    body: {name}Update,",
            f"    ctx: Annotated[TenantContext, Depends(require_permission(\"{update_perm}\"))],",
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f"    return APIResponse(message=\"Updated\", data={svc}(db).update(ctx, row_id, **extract_update_fields(body)))",
        ]
        if svc == "JobRequisitionService":
            route_handlers += [
                "",
                f"@{rname}.post(\"/{{row_id}}/submit\", response_model=APIResponse[{name}Response])",
                f"def submit_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.requisition:submit"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Submitted\", data={svc}(db).submit(ctx, row_id))",
                "",
                f"@{rname}.post(\"/{{row_id}}/approve\", response_model=APIResponse[{name}Response])",
                f"def approve_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.requisition:approve"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Approved\", data={svc}(db).approve(ctx, row_id))",
            ]
        if svc == "JobPostingService":
            route_handlers += [
                "",
                f"@{rname}.post(\"/{{row_id}}/publish\", response_model=APIResponse[{name}Response])",
                f"def publish_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.posting:publish"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Published\", data={svc}(db).publish(ctx, row_id))",
            ]
        if svc == "OfferService":
            route_handlers += [
                "",
                f"@{rname}.post(\"/{{row_id}}/submit\", response_model=APIResponse[{name}Response])",
                f"def submit_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.offer:submit"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Submitted\", data={svc}(db).submit(ctx, row_id))",
                "",
                f"@{rname}.post(\"/{{row_id}}/approve\", response_model=APIResponse[{name}Response])",
                f"def approve_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.offer:approve"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Approved\", data={svc}(db).approve(ctx, row_id))",
                "",
                f"@{rname}.post(\"/{{row_id}}/send\", response_model=APIResponse[{name}Response])",
                f"def send_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.offer:send"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Sent\", data={svc}(db).send(ctx, row_id))",
            ]
        if svc == "BackgroundVerificationService":
            route_handlers += [
                "",
                f"@{rname}.post(\"/{{row_id}}/submit\", response_model=APIResponse[{name}Response])",
                f"def submit_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.verification:submit"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Submitted\", data={svc}(db).submit(ctx, row_id))",
                "",
                f"@{rname}.post(\"/{{row_id}}/approve\", response_model=APIResponse[{name}Response])",
                f"def approve_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.verification:approve"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Approved\", data={svc}(db).approve(ctx, row_id))",
            ]
        if svc == "OnboardingService":
            route_handlers += [
                "",
                f"@{rname}.post(\"/{{row_id}}/submit\", response_model=APIResponse[{name}Response])",
                f"def submit_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.onboarding:submit"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Submitted\", data={svc}(db).submit(ctx, row_id))",
                "",
                f"@{rname}.post(\"/{{row_id}}/approve\", response_model=APIResponse[{name}Response])",
                f"def approve_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.onboarding:approve"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Approved\", data={svc}(db).approve(ctx, row_id))",
                "",
                f"@{rname}.post(\"/{{row_id}}/complete\", response_model=APIResponse[{name}Response])",
                f"def complete_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                "    body: OnboardingCompleteRequest,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("recruitment.onboarding:complete"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Completed\", data={svc}(db).complete(ctx, row_id, designation=body.designation))",
            ]

    w(
        REC / "routers" / "__init__.py",
        '"""Recruitment REST routers."""\n\n'
        + "\n".join(router_imports)
        + "\n".join(router_defs)
        + "\n".join(route_handlers)
        + "\n",
    )

    include_lines = [f"    {prefix.replace('-', '_')}_router," for prefix, _, _, _, _ in ROUTE_SPECS]
    w(
        REC / "router.py",
        '''"""Recruitment module router aggregation."""

from fastapi import APIRouter

from modules.recruitment.routers import (
'''
        + "\n".join(include_lines)
        + '''
)

recruitment_router = APIRouter(prefix="/recruitment")
'''
        + "\n".join(
            f"recruitment_router.include_router({prefix.replace('-', '_')}_router)"
            for prefix, _, _, _, _ in ROUTE_SPECS
        )
        + "\n",
    )


def gen_tasks_tests() -> None:
    w(
        REC / "tasks.py",
        '''"""Recruitment Celery tasks."""

from workers.celery_app import celery_app


@celery_app.task(name="recruitment.interview_reminders")
def interview_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecInterview

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecInterview).where(
                    RecInterview.is_deleted.is_(False),
                    RecInterview.status == "scheduled",
                )
            ).all()
        )
        return {"status": "ok", "scheduled_interviews": len(rows)}
    finally:
        db.close()


@celery_app.task(name="recruitment.offer_expiry_notifications")
def offer_expiry_notifications() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecOffer

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecOffer).where(
                    RecOffer.is_deleted.is_(False),
                    RecOffer.status == "sent",
                )
            ).all()
        )
        return {"status": "ok", "sent_offers": len(rows)}
    finally:
        db.close()


@celery_app.task(name="recruitment.background_verification_followups")
def background_verification_followups() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecBackgroundVerification

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecBackgroundVerification).where(
                    RecBackgroundVerification.is_deleted.is_(False),
                    RecBackgroundVerification.status == "in_progress",
                )
            ).all()
        )
        return {"status": "ok", "in_progress_bgv": len(rows)}
    finally:
        db.close()


@celery_app.task(name="recruitment.candidate_followup_alerts")
def candidate_followup_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecCandidate

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecCandidate).where(
                    RecCandidate.is_deleted.is_(False),
                    RecCandidate.status.in_(["applied", "screening", "interview"]),
                )
            ).all()
        )
        return {"status": "ok", "active_candidates": len(rows)}
    finally:
        db.close()


@celery_app.task(name="recruitment.onboarding_due_alerts")
def onboarding_due_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecOnboarding

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecOnboarding).where(
                    RecOnboarding.is_deleted.is_(False),
                    RecOnboarding.status == "in_progress",
                )
            ).all()
        )
        return {"status": "ok", "in_progress_onboarding": len(rows)}
    finally:
        db.close()


@celery_app.task(name="recruitment.retry_hr_handoff")
def retry_hr_handoff() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecOnboarding

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecOnboarding).where(
                    RecOnboarding.is_deleted.is_(False),
                    RecOnboarding.payroll_handoff_status == "failed",
                )
            ).all()
        )
        return {"status": "ok", "failed_handoffs": len(rows)}
    finally:
        db.close()
''',
    )

    w(
        TESTS / "unit" / "recruitment" / "test_recruitment_engines.py",
        '''"""Unit tests for recruitment engines."""

from types import SimpleNamespace

from modules.recruitment.service.engines import (
    JobPostingEngine,
    JobRequisitionEngine,
    OfferEngine,
    OnboardingEngine,
)


def test_job_requisition_lifecycle():
    engine = JobRequisitionEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    assert row.status == "submitted"
    engine.approve(row)
    assert row.status == "approved"
    engine.open(row)
    assert row.status == "open"


def test_job_posting_publish():
    engine = JobPostingEngine()
    row = SimpleNamespace(status="draft")
    engine.publish(row)
    assert row.status == "published"


def test_offer_submit_approve_send():
    engine = OfferEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.send(row)
    assert row.status == "sent"


def test_onboarding_submit_approve():
    engine = OnboardingEngine()
    row = SimpleNamespace(status="draft", employee_id=None)
    engine.submit(row)
    engine.approve(row)
    assert row.status == "in_progress"
''',
    )

    w(
        TESTS / "unit" / "recruitment" / "test_recruitment_tasks.py",
        '''"""Unit tests for recruitment Celery tasks."""

from modules.recruitment import tasks as recruitment_tasks


def test_recruitment_task_names_registered():
    assert recruitment_tasks.interview_reminders.name == "recruitment.interview_reminders"
    assert recruitment_tasks.offer_expiry_notifications.name == "recruitment.offer_expiry_notifications"
    assert recruitment_tasks.background_verification_followups.name == "recruitment.background_verification_followups"
    assert recruitment_tasks.candidate_followup_alerts.name == "recruitment.candidate_followup_alerts"
    assert recruitment_tasks.onboarding_due_alerts.name == "recruitment.onboarding_due_alerts"
    assert recruitment_tasks.retry_hr_handoff.name == "recruitment.retry_hr_handoff"
''',
    )

    w(
        TESTS / "security" / "recruitment" / "test_recruitment_permissions.py",
        '''"""Recruitment RBAC permission tests."""

from modules.recruitment.permissions import (
    HIRING_MANAGER_PERMISSIONS,
    HR_ONBOARDING_PERMISSIONS,
    RECRUITER_PERMISSIONS,
    RECRUITMENT_MANAGER_PERMISSIONS,
    RECRUITMENT_PERMISSIONS,
)


def test_recruitment_permissions_defined():
    assert len(RECRUITMENT_PERMISSIONS) >= 40
    assert "recruitment.onboarding:complete" in [p[0] for p in RECRUITMENT_PERMISSIONS]


def test_recruitment_roles():
    assert RECRUITER_PERMISSIONS
    assert RECRUITMENT_MANAGER_PERMISSIONS
    assert HR_ONBOARDING_PERMISSIONS
    assert HIRING_MANAGER_PERMISSIONS
    assert "recruitment.requisition:approve" in RECRUITMENT_MANAGER_PERMISSIONS
''',
    )

    w(
        TESTS / "integration" / "recruitment" / "test_recruitment_module_import.py",
        '''"""Integration smoke: Recruitment module imports and router mount."""

from modules.recruitment.models import RecApplication, RecCandidate, RecJobRequisition
from modules.recruitment.router import recruitment_router
from modules.recruitment.service import (
    JobRequisitionService,
    RecruitmentApplicationService,
    OfferService,
)
from modules.recruitment.service.engines import JobRequisitionEngine, OfferEngine


def test_recruitment_models_importable():
    assert RecJobRequisition.__tablename__ == "rec_job_requisition"
    assert RecCandidate.__tablename__ == "rec_candidate"
    assert RecApplication.__tablename__ == "rec_application"


def test_recruitment_router_mounted():
    assert recruitment_router.prefix == "/recruitment"
    assert len(recruitment_router.routes) > 20


def test_recruitment_services_and_engines_importable():
    assert RecruitmentApplicationService is not None
    assert JobRequisitionService is not None
    assert OfferService is not None
    assert JobRequisitionEngine is not None
    assert OfferEngine is not None
''',
    )


def gen_seeds() -> None:
    w(
        ALEMBIC / "0221_seed_rec_permissions.py",
        '''"""Seed recruitment permissions and roles."""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.recruitment.permissions import (
    HIRING_MANAGER_PERMISSIONS,
    HR_ONBOARDING_PERMISSIONS,
    RECRUITER_PERMISSIONS,
    RECRUITMENT_MANAGER_PERMISSIONS,
    RECRUITMENT_PERMISSIONS,
)

revision: str = "0221_seed_rec_permissions"
down_revision: str | None = "0220_rec_recruitment_report"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PERMISSION_TABLE = sa.table(
    "sec_permission",
    sa.column("id", sa.Uuid),
    sa.column("permission_code", sa.String),
    sa.column("resource", sa.String),
    sa.column("action", sa.String),
    sa.column("module", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("created_at", sa.DateTime(timezone=True)),
    schema="foundation",
)

ROLE_SPECS: list[tuple[str, str, list[str]]] = [
    ("RECRUITER", "Recruiter", RECRUITER_PERMISSIONS),
    ("RECRUITMENT_MANAGER", "Recruitment Manager", RECRUITMENT_MANAGER_PERMISSIONS),
    ("HR_ONBOARDING", "HR Onboarding", HR_ONBOARDING_PERMISSIONS),
    ("HIRING_MANAGER", "Hiring Manager", HIRING_MANAGER_PERMISSIONS),
]


def _ensure_permission(conn, now, code, resource, action, module):
    exists = conn.execute(
        sa.text("SELECT id FROM foundation.sec_permission WHERE permission_code = :code"),
        {"code": code},
    ).first()
    if exists:
        return str(exists[0])
    perm_id = str(uuid4())
    conn.execute(
        sa.insert(PERMISSION_TABLE).values(
            id=perm_id,
            permission_code=code,
            resource=resource,
            action=action,
            module=module,
            is_active=True,
            created_at=now,
        )
    )
    return perm_id


def _ensure_role(conn, now, tenant_id, role_code, role_name):
    exists = conn.execute(
        sa.text(
            """
            SELECT id FROM foundation.sec_role
            WHERE tenant_id = :tid AND role_code = :code AND is_deleted = false
            """
        ),
        {"tid": tenant_id, "code": role_code},
    ).first()
    if exists:
        return str(exists[0])
    role_id = str(uuid4())
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role
            (id, tenant_id, role_code, role_name, is_system_role, status,
             created_at, updated_at, is_deleted, version)
            VALUES (:id, :tid, :code, :name, true, 'active', :now, :now, false, 1)
            """
        ),
        {"id": role_id, "tid": tenant_id, "code": role_code, "name": role_name, "now": now},
    )
    return role_id


def _grant(conn, now, tenant_id, role_id, perm_id):
    exists = conn.execute(
        sa.text(
            """
            SELECT 1 FROM foundation.sec_role_permission
            WHERE role_id = :rid AND permission_id = :pid
            """
        ),
        {"rid": role_id, "pid": perm_id},
    ).first()
    if exists:
        return
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role_permission
            (id, tenant_id, role_id, permission_id, granted_at)
            VALUES (:id, :tid, :rid, :pid, :now)
            """
        ),
        {"id": str(uuid4()), "tid": tenant_id, "rid": role_id, "pid": perm_id, "now": now},
    )


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    perm_ids: dict[str, str] = {}
    for code, resource, action, module in RECRUITMENT_PERMISSIONS:
        perm_ids[code] = _ensure_permission(conn, now, code, resource, action, module)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for role_code, role_name, perms in ROLE_SPECS:
            role_id = _ensure_role(conn, now, tid, role_code, role_name)
            for perm_code in perms:
                _grant(conn, now, tid, role_id, perm_ids[perm_code])


def downgrade() -> None:
    conn = op.get_bind()
    for role_code, _, _ in reversed(ROLE_SPECS):
        conn.execute(
            sa.text(
                "DELETE FROM foundation.sec_role WHERE role_code = :code AND is_system_role = true"
            ),
            {"code": role_code},
        )
    for code, _, _, _ in RECRUITMENT_PERMISSIONS:
        conn.execute(
            sa.text("DELETE FROM foundation.sec_permission WHERE permission_code = :code"),
            {"code": code},
        )
''',
    )

    w(
        ALEMBIC / "0222_seed_recruitment_workflows.py",
        '''"""Seed recruitment workflow definitions per ERD_13."""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "0222_seed_recruitment_workflows"
down_revision: str | None = "0221_seed_rec_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORKFLOWS: list[tuple[str, str, str, list[tuple[int, str, str, str]]]] = [
    (
        "REC_JOB_APPROVAL",
        "Job Requisition Approval",
        "rec_job_requisition",
        [
            (1, "HIRING_MANAGER", "Hiring Manager Submit", "role"),
            (2, "RECRUITMENT_MANAGER", "Recruitment Manager Approval", "role"),
            (3, "HR_ONBOARDING", "HR Onboarding Review", "role"),
        ],
    ),
    (
        "REC_OFFER_APPROVAL",
        "Offer Approval",
        "rec_offer",
        [
            (1, "RECRUITER", "Recruiter Submit", "role"),
            (2, "HIRING_MANAGER", "Hiring Manager Approval", "role"),
            (3, "RECRUITMENT_MANAGER", "Recruitment Manager Approval", "role"),
        ],
    ),
    (
        "REC_BACKGROUND_APPROVAL",
        "Background Verification Approval",
        "rec_background_verification",
        [
            (1, "RECRUITER", "Recruiter Submit", "role"),
            (2, "RECRUITMENT_MANAGER", "Recruitment Manager Approval", "role"),
            (3, "HR_ONBOARDING", "HR Onboarding Review", "role"),
        ],
    ),
    (
        "REC_ONBOARDING_APPROVAL",
        "Onboarding Approval",
        "rec_onboarding",
        [
            (1, "HR_ONBOARDING", "HR Onboarding Submit", "role"),
            (2, "HIRING_MANAGER", "Hiring Manager Approval", "role"),
            (3, "RECRUITMENT_MANAGER", "Recruitment Manager Approval", "role"),
        ],
    ),
]


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for workflow_code, workflow_name, document_type, steps in WORKFLOWS:
            exists = conn.execute(
                sa.text(
                    """
                    SELECT id FROM foundation.wf_definition
                    WHERE tenant_id = :tid AND workflow_code = :code AND version_no = 1
                    """
                ),
                {"tid": tid, "code": workflow_code},
            ).first()
            if exists:
                wf_id = str(exists[0])
            else:
                wf_id = str(uuid4())
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_definition
                        (id, tenant_id, workflow_code, workflow_name, module,
                         document_type, version_no, is_active, created_at, updated_at)
                        VALUES (:id, :tid, :code, :name, 'recruitment', :doc, 1, true, :now, :now)
                        """
                    ),
                    {
                        "id": wf_id,
                        "tid": tid,
                        "code": workflow_code,
                        "name": workflow_name,
                        "doc": document_type,
                        "now": now,
                    },
                )
            for step_order, step_code, step_name, approver_type in steps:
                step_exists = conn.execute(
                    sa.text(
                        """
                        SELECT 1 FROM foundation.wf_step
                        WHERE workflow_id = :wid AND step_order = :ord
                        """
                    ),
                    {"wid": wf_id, "ord": step_order},
                ).first()
                if step_exists:
                    continue
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_step
                        (id, tenant_id, workflow_id, step_order, step_code, step_name,
                         approver_type, is_parallel, created_at, updated_at)
                        VALUES (:id, :tid, :wid, :ord, :code, :name, :atype, false, :now, :now)
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tid": tid,
                        "wid": wf_id,
                        "ord": step_order,
                        "code": step_code,
                        "name": step_name,
                        "atype": approver_type,
                        "now": now,
                    },
                )


def downgrade() -> None:
    conn = op.get_bind()
    for workflow_code, _, _, _ in WORKFLOWS:
        conn.execute(
            sa.text(
                """
                DELETE FROM foundation.wf_step
                WHERE workflow_id IN (
                    SELECT id FROM foundation.wf_definition WHERE workflow_code = :code
                )
                """
            ),
            {"code": workflow_code},
        )
        conn.execute(
            sa.text("DELETE FROM foundation.wf_definition WHERE workflow_code = :code"),
            {"code": workflow_code},
        )
''',
    )


def gen_wiring() -> None:
    patch_file(
        SHARED / "router.py",
        "from modules.payroll.router import payroll_router\n",
        "from modules.payroll.router import payroll_router\nfrom modules.recruitment.router import recruitment_router\n",
    )
    patch_file(
        SHARED / "router.py",
        "api_v1_router.include_router(payroll_router)\n",
        "api_v1_router.include_router(payroll_router)\napi_v1_router.include_router(recruitment_router)\n",
    )
    patch_file(
        ROOT / "alembic" / "env.py",
        "import modules.payroll.models  # noqa: F401 — register ORM metadata\n",
        "import modules.payroll.models  # noqa: F401 — register ORM metadata\n"
        "import modules.recruitment.models  # noqa: F401 — register ORM metadata\n",
    )
    patch_file(
        ROOT / "src" / "workers" / "celery_app.py",
        '        "modules.payroll",\n',
        '        "modules.payroll",\n        "modules.recruitment",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '    "modules.payroll.*",\n',
        '    "modules.payroll.*",\n    "modules.recruitment.*",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '"src/modules/payroll/domain/enums.py" = ["UP042"]\n',
        '"src/modules/payroll/domain/enums.py" = ["UP042"]\n'
        '"src/modules/recruitment/**" = ["E501", "SIM102"]\n'
        '"src/modules/recruitment/domain/enums.py" = ["UP042"]\n',
    )


def main() -> None:
    gen_scaffold()
    gen_domain()
    gen_models()
    gen_migrations()
    gen_repos()
    gen_engines()
    gen_services()
    gen_adapters()
    gen_permissions()
    gen_api()
    gen_tasks_tests()
    gen_seeds()
    gen_wiring()
    print(f"OK recruitment module generated — {len(FILES_WRITTEN)} files")
    print("Alembic head revision: 0222_seed_recruitment_workflows")


if __name__ == "__main__":
    main()

