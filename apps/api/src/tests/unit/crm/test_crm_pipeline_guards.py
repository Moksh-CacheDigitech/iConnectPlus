"""CRM sales pipeline gate tests (quote / OVF / blueprint attach)."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.exceptions import ConflictException
from modules.crm.service.blueprint_service import OpportunityBlueprintService
from modules.crm.service.ovf_service import OvfService
from modules.crm.service.quote_service import QuoteService


def test_ovf_create_requires_accepted_quote() -> None:
    service = OvfService(MagicMock())
    ctx = MagicMock()
    opportunity = SimpleNamespace(
        id=uuid4(),
        company_id=uuid4(),
        branch_id=uuid4(),
        blueprint_state="ovf_ready",
        customer_po_approved=True,
        locked=False,
    )
    quote = SimpleNamespace(
        id=uuid4(),
        opportunity_id=opportunity.id,
        quote_stage="sent_to_customer",
        parent_quote_id=None,
        quote_no="Q-1",
    )
    service._quotes.get = MagicMock(return_value=quote)
    service._opportunities.get = MagicMock(return_value=opportunity)
    service._quotes.list_quotes = MagicMock(return_value=[quote])
    service._repo.list_ovfs = MagicMock(return_value=[])

    with pytest.raises(ConflictException, match="No accepted quote|accepted"):
        service.create(ctx, quote_id=quote.id, branch_id=uuid4())


def test_ovf_create_rejects_when_ovf_already_exists() -> None:
    service = OvfService(MagicMock())
    ctx = MagicMock()
    opportunity = SimpleNamespace(
        id=uuid4(),
        company_id=uuid4(),
        branch_id=uuid4(),
        blueprint_state="ovf_ready",
        customer_po_approved=True,
        locked=False,
    )
    quote = SimpleNamespace(
        id=uuid4(),
        opportunity_id=opportunity.id,
        quote_stage="accepted",
        parent_quote_id=None,
        quote_no="Q-1",
    )
    service._quotes.get = MagicMock(return_value=quote)
    service._opportunities.get = MagicMock(return_value=opportunity)
    service._quotes.list_quotes = MagicMock(return_value=[quote])
    service._repo.list_ovfs = MagicMock(
        return_value=[SimpleNamespace(id=uuid4(), quote_id=quote.id)]
    )

    with pytest.raises(ConflictException, match="already exists for this opportunity"):
        service.create(ctx, quote_id=quote.id, branch_id=uuid4())


def test_ovf_create_rejects_split_parent_without_accepted_children() -> None:
    service = OvfService(MagicMock())
    ctx = MagicMock()
    opportunity = SimpleNamespace(
        id=uuid4(),
        company_id=uuid4(),
        branch_id=uuid4(),
        blueprint_state="ovf_ready",
        customer_po_approved=True,
        locked=False,
    )
    parent = SimpleNamespace(
        id=uuid4(),
        opportunity_id=opportunity.id,
        quote_stage="accepted",
        parent_quote_id=None,
        quote_no="Q-1",
    )
    child = SimpleNamespace(
        id=uuid4(),
        opportunity_id=opportunity.id,
        quote_stage="draft",
        parent_quote_id=parent.id,
        quote_no="Q-2",
    )
    service._quotes.get = MagicMock(return_value=parent)
    service._opportunities.get = MagicMock(return_value=opportunity)
    service._repo.list_ovfs = MagicMock(return_value=[])
    service._quotes.list_quotes = MagicMock(return_value=[parent, child])

    with pytest.raises(ConflictException, match="No accepted quote"):
        service.create(ctx, quote_id=parent.id, branch_id=uuid4())


def test_ovf_create_rejects_second_ovf_on_same_opportunity() -> None:
    """One opportunity gets one OVF; a sibling quote cannot raise another."""
    service = OvfService(MagicMock())
    ctx = MagicMock()
    company_id = uuid4()
    opportunity = SimpleNamespace(
        id=uuid4(),
        company_id=company_id,
        branch_id=uuid4(),
        blueprint_state="ovf_ready",
        customer_po_approved=True,
        locked=False,
        company_account_id=uuid4(),
        deal_reg_number="D-1",
    )
    quote_a = SimpleNamespace(
        id=uuid4(),
        opportunity_id=opportunity.id,
        quote_stage="accepted",
        parent_quote_id=None,
        quote_no="Q-A",
    )
    quote_b = SimpleNamespace(
        id=uuid4(),
        opportunity_id=opportunity.id,
        quote_stage="accepted",
        parent_quote_id=None,
        quote_no="Q-B",
        avg_margin_pct=Decimal("10"),
        total_margin_amount=Decimal("100"),
    )
    service._quotes.get = MagicMock(return_value=quote_b)
    service._opportunities.get = MagicMock(return_value=opportunity)
    service._repo.list_ovfs = MagicMock(
        return_value=[SimpleNamespace(id=uuid4(), quote_id=quote_a.id)]
    )
    service._quotes.list_quotes = MagicMock(return_value=[quote_a, quote_b])

    with pytest.raises(ConflictException, match="already exists for this opportunity"):
        service.create(ctx, quote_id=quote_b.id, branch_id=opportunity.branch_id)


def test_ovf_create_merges_accepted_split_children() -> None:
    """Split children combine into one opportunity OVF under an anchor quote."""
    service = OvfService(MagicMock())
    ctx = MagicMock()
    company_id = uuid4()
    opportunity = SimpleNamespace(
        id=uuid4(),
        company_id=company_id,
        branch_id=uuid4(),
        blueprint_state="ovf_ready",
        customer_po_approved=True,
        locked=False,
        company_account_id=uuid4(),
        deal_reg_number="D-1",
    )
    parent = SimpleNamespace(
        id=uuid4(),
        opportunity_id=opportunity.id,
        quote_stage="accepted",
        parent_quote_id=None,
        quote_no="DR-1/Q1",
    )
    child_a = SimpleNamespace(
        id=uuid4(),
        opportunity_id=opportunity.id,
        quote_stage="accepted",
        parent_quote_id=parent.id,
        quote_no="DR-1/Q2",
        entity_name="Entity A",
        avg_margin_pct=Decimal("10"),
        total_margin_amount=Decimal("50"),
    )
    child_b = SimpleNamespace(
        id=uuid4(),
        opportunity_id=opportunity.id,
        quote_stage="accepted",
        parent_quote_id=parent.id,
        quote_no="DR-1/Q3",
        entity_name="Entity B",
        avg_margin_pct=Decimal("12"),
        total_margin_amount=Decimal("60"),
    )
    line_parent = SimpleNamespace(
        id=uuid4(),
        line_no=1,
        product_name="SKU-PARENT",
        description="Parent line",
        qty=Decimal("3"),
        unit_sell=Decimal("100"),
        unit_cost=Decimal("80"),
        gst_pct=Decimal("18"),
    )
    line_a = SimpleNamespace(
        id=uuid4(),
        line_no=1,
        product_name="SKU-A",
        description="Line A",
        qty=Decimal("2"),
        unit_sell=Decimal("100"),
        unit_cost=Decimal("80"),
        gst_pct=Decimal("18"),
    )
    line_b = SimpleNamespace(
        id=uuid4(),
        line_no=1,
        product_name="SKU-B",
        description="Line B",
        qty=Decimal("1"),
        unit_sell=Decimal("200"),
        unit_cost=Decimal("150"),
        gst_pct=Decimal("18"),
    )
    service._quotes.get = MagicMock(return_value=parent)
    service._opportunities.get = MagicMock(return_value=opportunity)
    service._repo.list_ovfs = MagicMock(return_value=[])
    service._quotes.list_quotes = MagicMock(return_value=[parent, child_a, child_b])
    service._companies.get = MagicMock(return_value=None)
    service._snapshot_fields_from_related = MagicMock(return_value={})
    service._normalize_commercial_fields = MagicMock()
    service._delivery_fields = MagicMock(return_value={})
    service._numbers.generate_for_deal = MagicMock(return_value="DR-1/OVF1")
    created = SimpleNamespace(
        id=uuid4(),
        quote_id=parent.id,
        opportunity_id=opportunity.id,
        company_id=company_id,
        branch_id=opportunity.branch_id,
        ovf_no="DR-1/OVF1",
        original_vendor_total=None,
    )
    service._repo.create = MagicMock(return_value=created)

    def _lines_for(_ctx, qid):
        if qid == parent.id:
            return [line_parent]
        if qid == child_a.id:
            return [line_a]
        return [line_b]

    service._quote_lines.list_for_quote = MagicMock(side_effect=_lines_for)
    service._lines.create = MagicMock()
    service._recompute_margin = MagicMock()
    service._opportunities.update = MagicMock()

    row = service.create(ctx, quote_id=parent.id, branch_id=opportunity.branch_id)
    assert row.ovf_no == "DR-1/OVF1"
    # Split-source parent is the OVF quote_id (Quote No = Q1)
    assert service._repo.create.call_args.kwargs["quote_id"] == parent.id
    # Customer lines from parent (1) + vendor lines from 2 children (2) = 3 OVF lines
    assert service._lines.create.call_count == 3
    sides = [call.kwargs["side"] for call in service._lines.create.call_args_list]
    assert sides.count("customer_po") == 1
    assert sides.count("vendor") == 2
    vendor_descs = [
        call.kwargs["description"]
        for call in service._lines.create.call_args_list
        if call.kwargs["side"] == "vendor"
    ]
    assert any("DR-1/Q2" in (d or "") for d in vendor_descs)
    assert any("DR-1/Q3" in (d or "") for d in vendor_descs)

def test_quote_approve_internally_blocks_low_margin_without_force() -> None:
    service = QuoteService(MagicMock())
    ctx = MagicMock()
    quote = SimpleNamespace(
        id=uuid4(),
        quote_stage="draft",
        locked=False,
        freight=0,
    )
    service.get = MagicMock(return_value=quote)
    service._recompute = MagicMock()
    service.margin_summary = MagicMock(
        return_value={
            "requires_management_approval": True,
            "avg_margin_pct": 5,
            "required_threshold_pct": 7,
        },
    )

    with pytest.raises(ConflictException, match="Management"):
        service.approve_internally(ctx, quote.id, force=False)


def test_blueprint_shows_attach_boq_after_sow_approved_without_boq() -> None:
    service = OpportunityBlueprintService(MagicMock())
    ctx = MagicMock()
    opp = SimpleNamespace(
        id=uuid4(),
        company_id=uuid4(),
        branch_id=uuid4(),
        blueprint_state="deal_reg",
        locked=False,
        boq_attached=False,
        sow_attached=True,
        boq_approved=False,
        sow_approved=True,
        customer_po_attached=False,
        customer_po_approved=False,
        opportunity_name="Test Opp",
        deal_reg_number=None,
        opportunity_code=None,
    )
    service.get = MagicMock(return_value=opp)
    service._reconcile_post_lead_docs = MagicMock(return_value=opp)
    service._filter_create_actions_when_children_exist = MagicMock(
        side_effect=lambda _ctx, _opp, allowed: allowed
    )
    allowed = service.state(ctx, opp.id)["allowed_actions"]
    # Self-attach is legacy; sales uses My Jobs attachment requests.
    assert "send_boq_for_attachment" in allowed
    assert "attach_boq" not in allowed
    assert "send_sow_approval" not in allowed


def test_attach_requires_file_content() -> None:
    service = OpportunityBlueprintService(MagicMock())
    ctx = MagicMock()
    opp = SimpleNamespace(
        id=uuid4(),
        company_id=uuid4(),
        branch_id=uuid4(),
        blueprint_state="open",
        locked=False,
        boq_attached=False,
        sow_attached=False,
        opportunity_name="Test Opp",
    )
    service.get = MagicMock(return_value=opp)
    service._require_blueprint = MagicMock(return_value="open")
    service._attachments = MagicMock()

    with pytest.raises(ConflictException, match="Upload file content"):
        service.perform_action(
            ctx,
            opp.id,
            "attach_boq",
            {"file_name": "boq.pdf"},
        )


def test_approve_po_requires_locked_opportunity() -> None:
    service = OpportunityBlueprintService(MagicMock())
    ctx = MagicMock()
    opp = SimpleNamespace(
        id=uuid4(),
        company_id=uuid4(),
        branch_id=uuid4(),
        blueprint_state="po_approval",
        locked=False,
        customer_po_attached=True,
        opportunity_name="Test Opp",
    )
    service.get = MagicMock(return_value=opp)
    service._require_blueprint = MagicMock(return_value="po_approval")

    with pytest.raises(ConflictException, match="My Jobs"):
        service.perform_action(ctx, opp.id, "approve_po", {})
