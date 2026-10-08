"""Approval / workflow policy matrix and config-over-code registry.

Workflow codes match the codes each module seeds (``WORKFLOW_CODES``), so the
matrix and module governance resolve the same ``wf_definition``. When a tenant
has no definition yet, the platform provisions a single-step default using
``approver_role``. Tenants override the code per entity with the setting
``approval.workflow_code.<entity_name>``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ApprovalMode(str, Enum):
    WORKFLOW = "workflow"
    LOCAL_STATUS = "local_status"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class DocumentApprovalPolicy:
    document_type: str
    module: str
    mode: ApprovalMode
    workflow_code: str | None = None
    entity_name: str | None = None
    approver_role: str = "TENANT_ADMIN"
    amount_threshold: float | None = None


def _wf(
    document_type: str,
    module: str,
    workflow_code: str,
    entity_name: str | None,
    approver_role: str,
) -> DocumentApprovalPolicy:
    return DocumentApprovalPolicy(
        document_type,
        module,
        ApprovalMode.WORKFLOW,
        workflow_code=workflow_code,
        entity_name=entity_name,
        approver_role=approver_role,
    )


def _local(document_type: str, module: str) -> DocumentApprovalPolicy:
    return DocumentApprovalPolicy(document_type, module, ApprovalMode.LOCAL_STATUS)


APPROVAL_POLICIES: dict[str, DocumentApprovalPolicy] = {
    # Procurement
    "procurement.requisition": _wf("requisition", "procurement", "PROC_PR_APPROVAL", "proc_requisition_header", "PROC_MANAGER"),
    "procurement.rfq": _wf("rfq", "procurement", "PROC_RFQ_APPROVAL", "proc_rfq_header", "PROC_MANAGER"),
    "procurement.purchase_order": _wf("purchase_order", "procurement", "PROC_PO_APPROVAL", "proc_order_header", "PROC_MANAGER"),
    "procurement.invoice": _wf("invoice", "procurement", "PROC_INVOICE_APPROVAL", "proc_invoice_header", "FIN_MANAGER"),
    "procurement.return": _wf("return", "procurement", "PROC_RETURN_APPROVAL", "proc_return_header", "PROC_MANAGER"),
    "procurement.contract": _wf("contract", "procurement", "PROC_CONTRACT_APPROVAL", "proc_vendor_contract", "PROC_MANAGER"),
    "procurement.grn": _local("grn", "procurement"),
    # Finance
    "finance.journal": _wf("journal", "finance", "FIN_JOURNAL_APPROVAL", "fin_journal_header", "FIN_MANAGER"),
    "finance.vendor_payment": _wf("vendor_payment", "finance", "FIN_VENDOR_PAYMENT", "fin_vendor_ledger", "FIN_MANAGER"),
    "finance.asset_posting": _wf("asset_posting", "finance", "FIN_ASSET_POSTING", "fin_asset_transaction", "FIN_MANAGER"),
    # Sales
    "sales.quotation": _wf("quotation", "sales", "SALES_QUOTATION_APPROVAL", "sales_quotation_header", "SALES_MANAGER"),
    "sales.discount_rule": _wf("discount_rule", "sales", "SALES_DISCOUNT_APPROVAL", "sales_discount_rule", "SALES_MANAGER"),
    "sales.order": _wf("order", "sales", "SALES_ORDER_APPROVAL", "sales_order_header", "SALES_MANAGER"),
    "sales.invoice": _wf("invoice", "sales", "SALES_INVOICE_APPROVAL", "sales_invoice_header", "FIN_MANAGER"),
    "sales.return": _wf("return", "sales", "SALES_RETURN_APPROVAL", "sales_return_header", "SALES_MANAGER"),
    "sales.delivery": _local("delivery", "sales"),
    # Master data
    "master_data.employee": _wf("employee", "master_data", "MDM_EMPLOYEE_CREATE", "master_employee", "HR_ADMIN"),
    "master_data.customer": _wf("customer", "master_data", "MDM_CUSTOMER_CREATE", "master_customer", "TENANT_ADMIN"),
    "master_data.product": _wf("product", "master_data", "MDM_PRODUCT_CREATE", "master_product", "TENANT_ADMIN"),
    # Asset
    "asset.asset": _wf("asset", "asset", "AST_ASSET_APPROVAL", "ast_asset", "ASSET_MANAGER"),
    "asset.assignment": _wf("assignment", "asset", "AST_ASSIGNMENT_APPROVAL", "ast_asset_assignment", "ASSET_MANAGER"),
    "asset.transfer": _wf("transfer", "asset", "AST_TRANSFER_APPROVAL", "ast_asset_transfer", "ASSET_MANAGER"),
    "asset.maintenance": _wf("maintenance", "asset", "AST_MAINTENANCE_APPROVAL", "ast_asset_maintenance", "ASSET_MANAGER"),
    "asset.disposal": _wf("disposal", "asset", "AST_DISPOSAL_APPROVAL", "ast_asset_disposal", "ASSET_ADMIN"),
    "asset.revaluation": _wf("revaluation", "asset", "AST_REVALUATION_APPROVAL", "ast_asset_revaluation", "ASSET_ADMIN"),
    # Modules with their own status machines (no wf_definition)
    "hr.leave_request": _local("leave_request", "hr"),
    "hr.attendance_correction": _local("attendance_correction", "hr"),
    "hr.separation": _local("separation", "hr"),
    "payroll.run": _local("payroll_run", "payroll"),
    "inventory.transfer": _local("transfer", "inventory"),
    "inventory.adjustment": _local("adjustment", "inventory"),
    "inventory.cycle_count": _local("cycle_count", "inventory"),
    "manufacturing.production_order": _local("production_order", "manufacturing"),
    "manufacturing.material_issue": _local("material_issue", "manufacturing"),
    "quality.ncr": _local("ncr", "quality"),
    "quality.incoming_inspection": _local("incoming_inspection", "quality"),
    "crm.opportunity": _local("opportunity", "crm"),
    "project.change_request": _local("change_request", "project"),
    "helpdesk.ticket_escalation": _local("ticket_escalation", "helpdesk"),
    "document.publish": _local("publish", "document"),
    "grc.incident": _local("incident", "grc"),
    "marketing.campaign_publish": _local("campaign_publish", "marketing"),
}

_BY_ENTITY: dict[str, DocumentApprovalPolicy] = {
    p.entity_name: p for p in APPROVAL_POLICIES.values() if p.entity_name
}

WORKFLOW_CODE_SETTING_PREFIX = "approval.workflow_code."


def approval_policy(document_key: str) -> DocumentApprovalPolicy | None:
    return APPROVAL_POLICIES.get(document_key)


def policy_for_entity(entity_name: str) -> DocumentApprovalPolicy | None:
    return _BY_ENTITY.get(entity_name)


def workflow_backed_keys() -> list[str]:
    return [k for k, p in APPROVAL_POLICIES.items() if p.mode == ApprovalMode.WORKFLOW]
