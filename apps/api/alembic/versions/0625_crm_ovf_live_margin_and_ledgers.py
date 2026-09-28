"""CRM: live OVF margin, payments, execution expenses, GST registrations, FOC ledger.

Also adds BOQ/SOW SLA columns on My Jobs tasks, sales T&C acceptance + lease
details + marketing event on opportunities, and quote split lineage.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0625_crm_ovf_live_margin"
down_revision: str | Sequence[str] | None = "0624_proc_inventory_warranty"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SCHEMA = "crm"


def _standard_columns() -> list[sa.Column]:
    return [
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
    ]


def _standard_fks() -> list[sa.ForeignKeyConstraint]:
    return [
        sa.ForeignKeyConstraint(["tenant_id"], ["foundation.sec_tenant.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["company_id"], ["organization.org_company.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["branch_id"], ["organization.org_branch.id"], ondelete="RESTRICT"),
    ]


def _index(table: str, column: str) -> None:
    op.create_index(f"ix_{table}_{column}", table, [column], unique=False, schema=_SCHEMA)


def upgrade() -> None:
    # -- OVF live margin / delivery timeline / negotiation / freight request --
    ovf_columns = [
        sa.Column("margin_at_approval_amount", sa.Numeric(18, 4), nullable=True),
        sa.Column("margin_at_approval_pct", sa.Numeric(6, 3), nullable=True),
        sa.Column("execution_expense_total", sa.Numeric(18, 4), server_default="0", nullable=False),
        sa.Column("overdue_finance_cost", sa.Numeric(18, 4), server_default="0", nullable=False),
        sa.Column("holding_cost", sa.Numeric(18, 4), server_default="0", nullable=False),
        sa.Column("early_payment_discount_pct", sa.Numeric(6, 3), server_default="0", nullable=False),
        sa.Column("live_margin_amount", sa.Numeric(18, 4), nullable=True),
        sa.Column("live_margin_pct", sa.Numeric(6, 3), nullable=True),
        sa.Column("live_margin_as_of", sa.DateTime(timezone=True), nullable=True),
        sa.Column("full_payment_received", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("full_payment_marked_by", sa.UUID(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_weeks_min", sa.SmallInteger(), nullable=True),
        sa.Column("delivery_weeks_max", sa.SmallInteger(), nullable=True),
        sa.Column("expected_delivery_date", sa.Date(), nullable=True),
        sa.Column("actual_delivery_date", sa.Date(), nullable=True),
        sa.Column("delivery_date_history", postgresql.JSONB(), nullable=True),
        sa.Column("negotiated_by", sa.String(50), nullable=True),
        sa.Column("negotiation_remark", sa.Text(), nullable=True),
        sa.Column("original_vendor_total", sa.Numeric(18, 4), nullable=True),
        sa.Column("freight_medium", sa.String(20), nullable=True),
        sa.Column("freight_weight_kg", sa.Numeric(12, 3), nullable=True),
        sa.Column("freight_insurance", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    ]
    for column in ovf_columns:
        op.add_column("crm_ovf", column, schema=_SCHEMA)
    op.create_check_constraint(
        "ck_crm_ovf_freight_medium",
        "crm_ovf",
        "freight_medium IS NULL OR freight_medium IN ('air','road','sea','courier')",
        schema=_SCHEMA,
    )

    op.add_column("crm_ovf_line", sa.Column("source_line_id", sa.UUID(), nullable=True), schema=_SCHEMA)
    _index("crm_ovf_line", "source_line_id")

    op.create_table(
        "crm_ovf_payment",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ovf_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("received_date", sa.Date(), nullable=False),
        sa.Column("reference", sa.String(120), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        *_standard_columns(),
        *_standard_fks(),
        sa.ForeignKeyConstraint(["ovf_id"], ["crm.crm_ovf.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("amount > 0", name="ck_crm_ovf_payment_amount"),
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    for column in ("tenant_id", "company_id", "branch_id", "ovf_id"):
        _index("crm_ovf_payment", column)

    op.create_table(
        "crm_ovf_expense",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ovf_id", sa.UUID(), nullable=False),
        sa.Column("expense_type", sa.String(30), nullable=False),
        sa.Column("raised_by_team", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("incurred_on", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("decided_by", sa.UUID(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_remark", sa.Text(), nullable=True),
        *_standard_columns(),
        *_standard_fks(),
        sa.ForeignKeyConstraint(["ovf_id"], ["crm.crm_ovf.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("amount > 0", name="ck_crm_ovf_expense_amount"),
        sa.CheckConstraint(
            "expense_type IN ('operations','purchase','cables','matad','site_visit','foc','installation','other')",
            name="ck_crm_ovf_expense_type",
        ),
        sa.CheckConstraint(
            "raised_by_team IN ('scm','operations','sales','presales','finance','other')",
            name="ck_crm_ovf_expense_team",
        ),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="ck_crm_ovf_expense_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    for column in ("tenant_id", "company_id", "branch_id", "ovf_id"):
        _index("crm_ovf_expense", column)

    # -- Opportunity: sales T&C acceptance, lease (OpEx), marketing event --
    opp_columns = [
        sa.Column("marketing_event_id", sa.UUID(), nullable=True),
        sa.Column("sales_terms_accepted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("sales_terms_accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sales_terms_accepted_by", sa.UUID(), nullable=True),
        sa.Column("purchase_model", sa.String(20), nullable=True),
        sa.Column("lease_type", sa.String(20), nullable=True),
        sa.Column("lease_partner", sa.String(255), nullable=True),
        sa.Column("lease_interest_rate_pct", sa.Numeric(6, 3), nullable=True),
        sa.Column("lease_tenure_months", sa.SmallInteger(), nullable=True),
        sa.Column("lease_monthly_rental", sa.Numeric(18, 4), nullable=True),
    ]
    for column in opp_columns:
        op.add_column("crm_opportunity", column, schema=_SCHEMA)
    _index("crm_opportunity", "marketing_event_id")
    op.create_check_constraint(
        "ck_crm_opp_purchase_model",
        "crm_opportunity",
        "purchase_model IS NULL OR purchase_model IN ('capex','opex')",
        schema=_SCHEMA,
    )
    op.create_check_constraint(
        "ck_crm_opp_lease_type",
        "crm_opportunity",
        "lease_type IS NULL OR lease_type IN ('finance','operating')",
        schema=_SCHEMA,
    )

    # -- My Jobs: BOQ/SOW response + attach SLA --
    task_columns = [
        sa.Column("response_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response", sa.String(20), nullable=True),
        sa.Column("response_reason", sa.Text(), nullable=True),
        sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("escalation_level", sa.SmallInteger(), server_default="0", nullable=False),
    ]
    for column in task_columns:
        op.add_column("crm_approval_task", column, schema=_SCHEMA)
    op.create_check_constraint(
        "ck_crm_approval_task_response",
        "crm_approval_task",
        "response IS NULL OR response IN ('can_submit','cannot_submit')",
        schema=_SCHEMA,
    )

    # -- Quote split lineage --
    op.add_column("crm_quote", sa.Column("parent_quote_id", sa.UUID(), nullable=True), schema=_SCHEMA)
    op.create_foreign_key(
        "fk_crm_quote_parent_quote",
        "crm_quote",
        "crm_quote",
        ["parent_quote_id"],
        ["id"],
        source_schema=_SCHEMA,
        referent_schema=_SCHEMA,
        ondelete="RESTRICT",
    )
    _index("crm_quote", "parent_quote_id")
    op.add_column("crm_quote_line", sa.Column("source_line_id", sa.UUID(), nullable=True), schema=_SCHEMA)
    op.create_foreign_key(
        "fk_crm_quote_line_source_line",
        "crm_quote_line",
        "crm_quote_line",
        ["source_line_id"],
        ["id"],
        source_schema=_SCHEMA,
        referent_schema=_SCHEMA,
        ondelete="RESTRICT",
    )
    _index("crm_quote_line", "source_line_id")

    # -- Customer GST registrations (one account, many GSTINs / branches) --
    op.create_table(
        "crm_company_gst",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_account_id", sa.UUID(), nullable=False),
        sa.Column("gstin", sa.String(15), nullable=False),
        sa.Column("state_code", sa.String(2), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("location_label", sa.String(255), nullable=True),
        sa.Column("billing_address", sa.Text(), nullable=True),
        sa.Column("shipping_address", sa.Text(), nullable=True),
        sa.Column("is_head_office", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("certificate_attachment_id", sa.UUID(), nullable=True),
        sa.Column("source", sa.String(20), server_default="manual", nullable=False),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        *_standard_columns(),
        *_standard_fks(),
        sa.ForeignKeyConstraint(["company_account_id"], ["crm.crm_company.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("source IN ('manual','customer_po','kyc')", name="ck_crm_company_gst_source"),
        sa.CheckConstraint("status IN ('active','inactive')", name="ck_crm_company_gst_status"),
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    for column in ("tenant_id", "company_id", "branch_id", "company_account_id"):
        _index("crm_company_gst", column)
    op.create_index(
        "uq_crm_company_gst_account_gstin",
        "crm_company_gst",
        ["company_account_id", "gstin"],
        unique=True,
        schema=_SCHEMA,
        postgresql_where=sa.text("is_deleted = false"),
    )

    # -- Customer expense / FOC ledger --
    op.create_table(
        "crm_customer_expense",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_account_id", sa.UUID(), nullable=False),
        sa.Column("opportunity_id", sa.UUID(), nullable=True),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("approved_by_name", sa.String(255), nullable=True),
        sa.Column("approval_reference", sa.Text(), nullable=True),
        sa.Column("adjust_in_future", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("status", sa.String(20), server_default="open", nullable=False),
        sa.Column("adjusted_ovf_id", sa.UUID(), nullable=True),
        sa.Column("adjusted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("adjustment_remark", sa.Text(), nullable=True),
        *_standard_columns(),
        *_standard_fks(),
        sa.ForeignKeyConstraint(["company_account_id"], ["crm.crm_company.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["crm.crm_opportunity.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["adjusted_ovf_id"], ["crm.crm_ovf.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("amount > 0", name="ck_crm_customer_expense_amount"),
        sa.CheckConstraint(
            "category IN ('foc_material','replacement','site_visit','service','cables','other')",
            name="ck_crm_customer_expense_category",
        ),
        sa.CheckConstraint(
            "status IN ('open','adjusted','written_off')",
            name="ck_crm_customer_expense_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    for column in ("tenant_id", "company_id", "branch_id", "company_account_id", "opportunity_id"):
        _index("crm_customer_expense", column)


def downgrade() -> None:
    op.drop_table("crm_customer_expense", schema=_SCHEMA)
    op.drop_table("crm_company_gst", schema=_SCHEMA)

    op.drop_index("ix_crm_quote_line_source_line_id", table_name="crm_quote_line", schema=_SCHEMA)
    op.drop_constraint("fk_crm_quote_line_source_line", "crm_quote_line", schema=_SCHEMA, type_="foreignkey")
    op.drop_column("crm_quote_line", "source_line_id", schema=_SCHEMA)
    op.drop_index("ix_crm_quote_parent_quote_id", table_name="crm_quote", schema=_SCHEMA)
    op.drop_constraint("fk_crm_quote_parent_quote", "crm_quote", schema=_SCHEMA, type_="foreignkey")
    op.drop_column("crm_quote", "parent_quote_id", schema=_SCHEMA)

    op.drop_constraint("ck_crm_approval_task_response", "crm_approval_task", schema=_SCHEMA, type_="check")
    for column in (
        "escalation_level",
        "escalated_at",
        "response_reason",
        "response",
        "responded_at",
        "response_due_at",
    ):
        op.drop_column("crm_approval_task", column, schema=_SCHEMA)

    op.drop_constraint("ck_crm_opp_lease_type", "crm_opportunity", schema=_SCHEMA, type_="check")
    op.drop_constraint("ck_crm_opp_purchase_model", "crm_opportunity", schema=_SCHEMA, type_="check")
    op.drop_index("ix_crm_opportunity_marketing_event_id", table_name="crm_opportunity", schema=_SCHEMA)
    for column in (
        "lease_monthly_rental",
        "lease_tenure_months",
        "lease_interest_rate_pct",
        "lease_partner",
        "lease_type",
        "purchase_model",
        "sales_terms_accepted_by",
        "sales_terms_accepted_at",
        "sales_terms_accepted",
        "marketing_event_id",
    ):
        op.drop_column("crm_opportunity", column, schema=_SCHEMA)

    op.drop_table("crm_ovf_expense", schema=_SCHEMA)
    op.drop_table("crm_ovf_payment", schema=_SCHEMA)
    op.drop_index("ix_crm_ovf_line_source_line_id", table_name="crm_ovf_line", schema=_SCHEMA)
    op.drop_column("crm_ovf_line", "source_line_id", schema=_SCHEMA)

    op.drop_constraint("ck_crm_ovf_freight_medium", "crm_ovf", schema=_SCHEMA, type_="check")
    for column in (
        "freight_insurance",
        "freight_weight_kg",
        "freight_medium",
        "original_vendor_total",
        "negotiation_remark",
        "negotiated_by",
        "delivery_date_history",
        "actual_delivery_date",
        "expected_delivery_date",
        "delivery_weeks_max",
        "delivery_weeks_min",
        "closed_at",
        "full_payment_marked_by",
        "full_payment_received",
        "live_margin_as_of",
        "live_margin_pct",
        "live_margin_amount",
        "early_payment_discount_pct",
        "holding_cost",
        "overdue_finance_cost",
        "execution_expense_total",
        "margin_at_approval_pct",
        "margin_at_approval_amount",
    ):
        op.drop_column("crm_ovf", column, schema=_SCHEMA)
