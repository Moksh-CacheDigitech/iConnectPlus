"""Recruitment permission constants per ERD_13 §14."""

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
