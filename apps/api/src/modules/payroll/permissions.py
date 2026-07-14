"""Payroll permission constants per ERD_12 §14."""

PAYROLL_PERMISSIONS: list[tuple[str, str, str, str]] = [
    ("payroll.period:read", "payroll.period", "read", "payroll"),
    ("payroll.period:create", "payroll.period", "create", "payroll"),
    ("payroll.period:update", "payroll.period", "update", "payroll"),
    ("payroll.structure:read", "payroll.structure", "read", "payroll"),
    ("payroll.structure:create", "payroll.structure", "create", "payroll"),
    ("payroll.structure:update", "payroll.structure", "update", "payroll"),
    ("payroll.component:read", "payroll.component", "read", "payroll"),
    ("payroll.component:create", "payroll.component", "create", "payroll"),
    ("payroll.component:update", "payroll.component", "update", "payroll"),
    ("payroll.employee_salary:read", "payroll.employee_salary", "read", "payroll"),
    ("payroll.employee_salary:create", "payroll.employee_salary", "create", "payroll"),
    ("payroll.employee_salary:update", "payroll.employee_salary", "update", "payroll"),
    ("payroll.run:read", "payroll.run", "read", "payroll"),
    ("payroll.run:create", "payroll.run", "create", "payroll"),
    ("payroll.run:calculate", "payroll.run", "calculate", "payroll"),
    ("payroll.run:submit", "payroll.run", "submit", "payroll"),
    ("payroll.run:approve", "payroll.run", "approve", "payroll"),
    ("payroll.payslip:read", "payroll.payslip", "read", "payroll"),
    ("payroll.payslip:issue", "payroll.payslip", "issue", "payroll"),
    ("payroll.payslip:export", "payroll.payslip", "export", "payroll"),
    ("payroll.bonus:read", "payroll.bonus", "read", "payroll"),
    ("payroll.bonus:create", "payroll.bonus", "create", "payroll"),
    ("payroll.bonus:submit", "payroll.bonus", "submit", "payroll"),
    ("payroll.bonus:approve", "payroll.bonus", "approve", "payroll"),
    ("payroll.reimbursement:read", "payroll.reimbursement", "read", "payroll"),
    ("payroll.reimbursement:create", "payroll.reimbursement", "create", "payroll"),
    ("payroll.reimbursement:submit", "payroll.reimbursement", "submit", "payroll"),
    ("payroll.reimbursement:approve", "payroll.reimbursement", "approve", "payroll"),
    ("payroll.loan:read", "payroll.loan", "read", "payroll"),
    ("payroll.loan:create", "payroll.loan", "create", "payroll"),
    ("payroll.loan:submit", "payroll.loan", "submit", "payroll"),
    ("payroll.loan:approve", "payroll.loan", "approve", "payroll"),
    ("payroll.adjustment:read", "payroll.adjustment", "read", "payroll"),
    ("payroll.adjustment:create", "payroll.adjustment", "create", "payroll"),
    ("payroll.adjustment:apply", "payroll.adjustment", "apply", "payroll"),
    ("payroll.posting:read", "payroll.posting", "read", "payroll"),
    ("payroll.posting:submit", "payroll.posting", "submit", "payroll"),
    ("payroll.posting:approve", "payroll.posting", "approve", "payroll"),
    ("payroll.posting:post", "payroll.posting", "post", "payroll"),
    ("payroll.tax:read", "payroll.tax", "read", "payroll"),
    ("payroll.tax:create", "payroll.tax", "create", "payroll"),
    ("payroll.tax:update", "payroll.tax", "update", "payroll"),
    ("payroll.statutory:read", "payroll.statutory", "read", "payroll"),
    ("payroll.statutory:create", "payroll.statutory", "create", "payroll"),
    ("payroll.statutory:update", "payroll.statutory", "update", "payroll"),
    ("payroll.report:read", "payroll.report", "read", "payroll"),
    ("payroll.report:export", "payroll.report", "export", "payroll"),
]

PAYROLL_EXECUTIVE_PERMISSIONS = list(
    dict.fromkeys(
        [p[0] for p in PAYROLL_PERMISSIONS if p[2] in {"read", "create", "update", "calculate", "issue", "export"}]
    )
)

PAYROLL_MANAGER_PERMISSIONS = list(
    dict.fromkeys(
        PAYROLL_EXECUTIVE_PERMISSIONS
        + [
            "payroll.run:submit",
            "payroll.run:approve",
            "payroll.bonus:approve",
            "payroll.loan:approve",
            "payroll.posting:submit",
        ]
    )
)

HR_PAYROLL_ADMIN_PERMISSIONS = list(
    dict.fromkeys(
        PAYROLL_MANAGER_PERMISSIONS
        + [
            "payroll.reimbursement:approve",
            "payroll.adjustment:apply",
        ]
    )
)

FINANCE_PAYROLL_REVIEWER_PERMISSIONS = list(
    dict.fromkeys(
        HR_PAYROLL_ADMIN_PERMISSIONS
        + [
            "payroll.posting:approve",
            "payroll.posting:post",
            "payroll.report:export",
        ]
    )
)
