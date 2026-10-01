"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  ArrowLeft,
  Building2,
  FileText,
  MapPin,
  Scale,
} from "lucide-react";

import {
  CrmErrorBanner,
  CrmInfoBanner,
  CrmPage,
  CrmSection,
  CrmWarnBanner,
} from "@/components/crm/crm-ui";
import {
  CrmReadOnlyField,
  CrmReadOnlyTextarea,
  textOrDash,
} from "@/components/crm/sales/crm-readonly-field";
import { ApprovalBanner } from "@/components/crm/sales/approval-banner";
import { CrmEntityRejectionAlert } from "@/components/crm/sales/crm-approval-inbox-listener";
import { BlueprintActions } from "@/components/crm/sales/blueprint-actions";
import { resolveSalesStageLabel } from "@/lib/crm/sales-blueprint-stages";
import { CrmDetailEditLink } from "@/components/crm/sales/crm-detail-edit-link";
import { CrmRecordActionsMenu } from "@/components/crm/sales/crm-record-actions-menu";
import { QuoteLineTable } from "@/components/crm/sales/quote-line-table";
import { QuoteSplitPanel } from "@/components/crm/sales/quote-split-panel";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { cloneQuoteRecord, downloadQuoteExport, printQuotePreview } from "@/lib/crm/crm-record-actions";
import { formatCrmCode } from "@/lib/crm/format-crm-code";
import { ApiClientError } from "@/services/api-client";
import {
  applyOpportunityAction,
  applyQuoteAction,
  approveQuoteInternally,
  deleteQuote,
  fullName,
  getOpportunity,
  getOpportunityBlueprint,
  getQuote,
  getQuoteBlueprint,
  getQuoteMargin,
  listContacts,
  listQuoteLines,
  listQuotes,
  listOvfs,
  sendQuoteForApproval,
  type BlueprintActionPayload,
  type BlueprintState,
  type Contact,
  type Opportunity,
  type Ovf,
  type Quote,
  type QuoteLine,
  type QuoteMarginSummary,
} from "@/services/sales-crm-service";

function formatQuoteStage(stage: string): string {
  if (!stage) return "-";
  return stage.replaceAll("_", " ");
}

export function QuoteDetailPage({ quoteId }: { quoteId: string }) {
  const router = useRouter();
  const [quote, setQuote] = useState<Quote | null>(null);
  const [blueprint, setBlueprint] = useState<BlueprintState | null>(null);
  const [margin, setMargin] = useState<QuoteMarginSummary | null>(null);
  const [lines, setLines] = useState<QuoteLine[]>([]);
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [oppBlueprint, setOppBlueprint] = useState<BlueprintState | null>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [existingOvf, setExistingOvf] = useState<Ovf | null>(null);
  const [siblingQuotes, setSiblingQuotes] = useState<Quote[]>([]);
  const [opportunityOvfs, setOpportunityOvfs] = useState<Ovf[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [banner, setBanner] = useState<{ text: string; tone: "error" | "success" } | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [quoteRow, bp, marginRow, lineRows] = await Promise.all([
        getQuote(quoteId),
        getQuoteBlueprint(quoteId),
        getQuoteMargin(quoteId).catch(() => null),
        listQuoteLines(quoteId).catch(() => []),
      ]);
      setQuote(quoteRow);
      setBlueprint(bp);
      setMargin(marginRow);
      setLines(lineRows);
      const [opp, ovfRows, oppBp, siblingQuotes] = await Promise.all([
        getOpportunity(quoteRow.opportunity_id).catch(() => null),
        listOvfs({ opportunity_id: quoteRow.opportunity_id }).catch(() => []),
        getOpportunityBlueprint(quoteRow.opportunity_id).catch(() => null),
        listQuotes({ opportunity_id: quoteRow.opportunity_id }).catch(() => []),
      ]);
      setOpportunity(opp);
      setOppBlueprint(oppBp);
      setContacts(
        opp?.company_account_id
          ? await listContacts(opp.company_account_id).catch(() => [] as Contact[])
          : [],
      );
      // One OVF per opportunity (covers all accepted split quotes).
      setExistingOvf(ovfRows[0] ?? null);
      setSiblingQuotes(siblingQuotes);
      setOpportunityOvfs(ovfRows);
    } catch (err) {
      setQuote(null);
      setError(err instanceof ApiClientError ? err.message : "Failed to load quote");
    } finally {
      setLoading(false);
    }
  }, [quoteId]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  async function onBlueprintAction(action: string, payload: BlueprintActionPayload) {
    setBusy(true);
    setError(null);
    setBanner(null);
    try {
      if (action === "create_ovf" || action.startsWith("create_ovf:")) {
        const parentsWithChildren = new Set(
          siblingQuotes.map((q) => q.parent_quote_id).filter((id): id is string => Boolean(id)),
        );
        const splitSource = siblingQuotes.find((q) => parentsWithChildren.has(q.id)) ?? null;
        const childSources = siblingQuotes.filter(
          (q) => q.quote_stage === "accepted" && !parentsWithChildren.has(q.id),
        );
        const anchor = splitSource ?? childSources[0] ?? quote;
        if (!anchor || opportunityOvfs.length > 0 || childSources.length === 0) {
          throw new ApiClientError(
            opportunityOvfs.length > 0
              ? "An OVF already exists for this opportunity. Open that OVF to continue."
              : "No accepted quote is available for OVF.",
            409,
          );
        }
        router.push(`/crm/quotes/${anchor.id}/ovf/new`);
        return;
      }
      const oppActions = new Set([
        "attach_po",
        "send_po_approval",
        "lost",
        "attach_boq",
        "attach_sow",
        "send_boq_approval",
        "send_sow_approval",
        "skip_sow",
        "deal_reg",
        "oem_received",
        "attach_oem_quote",
        "create_ovf",
      ]);
      if (opportunity && oppActions.has(action)) {
        await applyOpportunityAction(opportunity.id, action, payload);
        await load();
        return;
      }
      if (action === "send_for_approval") {
        const assignedUserId = payload.assigned_user_id;
        const assignedUserIds = Array.isArray(payload.assigned_user_ids)
          ? payload.assigned_user_ids.filter((id): id is string => typeof id === "string" && Boolean(id.trim()))
          : [];
        if (typeof assignedUserId !== "string" || !assignedUserId.trim()) {
          throw new ApiClientError("Select an approver before sending for approval.", 400);
        }
        await sendQuoteForApproval(quoteId, {
          team_role: typeof payload.team_role === "string" ? payload.team_role : undefined,
          assigned_user_id: assignedUserId,
          assigned_user_ids: assignedUserIds.length > 0 ? assignedUserIds : [assignedUserId],
          remarks: typeof payload.remarks === "string" ? payload.remarks : null,
        });
      } else if (action === "approve_internally") {
        await approveQuoteInternally(quoteId, { remark: payload.remark });
      } else {
        await applyQuoteAction(quoteId, action, payload);
      }

      if (action === "send_to_customer") {
        setBanner({
          text: "Quote marked as sent to customer.",
          tone: "success",
        });
      }

      await load();
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : `Failed to ${action}`;
      setBanner({ text: message, tone: "error" });
      throw err;
    } finally {
      setBusy(false);
    }
  }

  if (loading && !quote) {
    return (
      <div className="space-y-3">
        <div className="h-8 w-48 animate-pulse rounded bg-muted" />
        <div className="h-40 animate-pulse rounded-xl bg-muted/60" />
      </div>
    );
  }

  if (error && !quote) {
    return (
      <CrmPage className="space-y-3">
        <Link href="/crm/quotes" className="inline-flex cursor-pointer items-center gap-1 text-xs font-medium text-primary">
          <ArrowLeft className="size-3.5" /> Quotes
        </Link>
        <CrmErrorBanner>{error}</CrmErrorBanner>
      </CrmPage>
    );
  }

  if (!quote || !blueprint) return null;

  const readOnlyLines = quote.locked || ["accepted", "lost", "sent_to_customer", "negotiation", "follow_up"].includes(quote.quote_stage);
  const contact =
    contacts.find((row) => row.id === quote.contact_id) ??
    contacts.find((row) => row.is_primary) ??
    null;
  const contactName = contact ? fullName(contact) : "-";

  const parentsWithChildren = new Set(
    siblingQuotes.map((q) => q.parent_quote_id).filter((id): id is string => Boolean(id)),
  );
  const quotesForOvf = siblingQuotes.filter(
    (q) => q.quote_stage === "accepted" && !parentsWithChildren.has(q.id),
  );
  const opportunityReadyForOvf =
    Boolean(oppBlueprint?.allowed_actions.includes("create_ovf")) ||
    ((oppBlueprint?.state === "ovf_ready" || opportunity?.blueprint_state === "ovf_ready") &&
      Boolean(opportunity?.customer_po_approved));
  const canCreateOvf =
    opportunityReadyForOvf &&
    quotesForOvf.length > 0 &&
    opportunityOvfs.length === 0 &&
    !blueprint.locked;
  const createOvfActions = canCreateOvf ? ["create_ovf"] : [];
  const createOvfLabels: Record<string, string> = canCreateOvf
    ? {
      create_ovf:
        quotesForOvf.length > 1
          ? `Create OVF · ${quotesForOvf.length} quotes`
          : "Create OVF",
    }
    : {};

  const oppTransitionActions =
    quote.quote_stage === "accepted" && oppBlueprint
      ? oppBlueprint.allowed_actions.filter(
        (action) =>
          action !== "create_quote" &&
          action !== "create_ovf" &&
          action !== "quote_accepted" &&
          !blueprint.allowed_actions.includes(action),
      )
      : [];

  const blueprintActions = Array.from(
    new Set([
      ...blueprint.allowed_actions,
      ...oppTransitionActions,
      ...createOvfActions,
    ]),
  );

  async function onPrintPreview() {
    const q = quote;
    if (!q) return;
    await printQuotePreview(q, lines);
  }

  async function onExport() {
    const q = quote;
    if (!q) return;
    await downloadQuoteExport(q, lines);
  }

  return (
    <CrmPage>
      <div>
        <Link href="/crm/quotes" className="inline-flex cursor-pointer items-center gap-1 text-xs font-medium text-primary transition-opacity duration-200 hover:opacity-80">
          <ArrowLeft className="size-3.5" /> Quotes
        </Link>
      </div>

      <CrmEntityRejectionAlert entityType="quote" entityId={quote.id} />
      <ApprovalBanner locked={blueprint.locked} approvalStatus={blueprint.state} label="This quote" />

      <PageHeader
        title={`${formatCrmCode(quote.quote_no)}${quote.quote_revision > 1 ? ` (Rev ${quote.quote_revision})` : ""}`}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <CrmDetailEditLink href={`/crm/quotes/${quote.id}/edit`} />
            {existingOvf ? (
              <Link
                href={`/crm/ovf/${existingOvf.id}`}
                className="inline-flex h-7 cursor-pointer items-center gap-1.5 rounded-lg border border-border bg-background px-2.5 text-[0.8rem] font-medium text-foreground shadow-sm transition-colors duration-200 hover:bg-muted/60"
              >
                Open OVF
              </Link>
            ) : null}
            {quote ? (
              <CrmRecordActionsMenu
                entityType="quote"
                entityId={quote.id}
                entityLabel="Quote"
                entityName={formatCrmCode(quote.quote_no)}
                shareTitle={formatCrmCode(quote.quote_no)}
                onClone={() => cloneQuoteRecord(quote, lines, router)}
                onPrintPreview={onPrintPreview}
                onExport={onExport}
                onDelete={() => deleteQuote(quote.id)}
                onDeleted={() =>
                  router.push(
                    opportunity ? `/crm/opportunities/${opportunity.id}` : "/crm/quotes",
                  )
                }
              />
            ) : null}
          </div>
        }
      />

      {opportunity ? (
        <p className="text-xs text-muted-foreground">
          For opportunity{" "}
          <Link
            href={`/crm/opportunities/${opportunity.id}`}
            className="cursor-pointer font-medium text-primary underline underline-offset-2"
          >
            {opportunity.opportunity_name}
          </Link>
        </p>
      ) : null}

      {banner ? (
        banner.tone === "success" ? (
          <CrmInfoBanner>{banner.text}</CrmInfoBanner>
        ) : (
          <CrmErrorBanner>{banner.text}</CrmErrorBanner>
        )
      ) : null}
      {error ? <CrmErrorBanner>{error}</CrmErrorBanner> : null}

      <BlueprintActions
        allowedActions={blueprintActions}
        locked={blueprint.locked && oppTransitionActions.length === 0 && createOvfActions.length === 0}
        entityType="quote"
        currentStageLabel={resolveSalesStageLabel({
          entityType: "quote",
          blueprintState: blueprint.state,
          locked: blueprint.locked,
          quote,
        })}
        excludeActions={["approve_internally"]}
        actionLabelOverrides={createOvfLabels}
        onAction={onBlueprintAction}
        disabled={busy}
      />
      {margin?.requires_management_approval && !blueprint.locked ? (
        <CrmWarnBanner>
          <span className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 size-3.5 shrink-0" />
            Margin is below the management threshold ({margin.required_threshold_pct}%). Use Send for
            Approval.
          </span>
        </CrmWarnBanner>
      ) : null}

      <CrmSection title="Quote Information" icon={FileText}>
        <div className="grid min-w-0 gap-x-6 gap-y-3 md:grid-cols-2">
          <CrmReadOnlyField
            label="Project Title"
            value={textOrDash(quote.project_title)}
          />
          <CrmReadOnlyField label="Account Name" value={textOrDash(quote.account_name)} />
          <CrmReadOnlyField label="Valid Until *" value={textOrDash(quote.valid_until)} />
          <CrmReadOnlyField label="Contact Name" value={contactName} />
          <CrmReadOnlyField label="Quote Owner" value={textOrDash(quote.owner_name)} />
          <CrmReadOnlyField label="Quote No." value={formatCrmCode(quote.quote_no)} />
          <CrmReadOnlyField
            label="Quote Stage"
            value={formatQuoteStage(quote.quote_stage)}
          />
          <CrmReadOnlyField label="Version" value={String(quote.version ?? 1)} />
        </div>
      </CrmSection>

      <CrmSection title="Entity Information" icon={Building2}>
        <div className="grid min-w-0 gap-x-6 gap-y-3 md:grid-cols-2">
          <CrmReadOnlyField label="Entity Name" value={textOrDash(quote.entity_name)} />
          <CrmReadOnlyField label="Entity Address" value={textOrDash(quote.entity_address)} />
          <CrmReadOnlyField
            label="Entity Contact Number"
            value={textOrDash(quote.entity_contact)}
          />
          <CrmReadOnlyField label="Entity Email" value={textOrDash(quote.entity_email)} />
          <CrmReadOnlyField label="Entity GST No." value={textOrDash(quote.entity_gst)} />
        </div>
      </CrmSection>

      <CrmSection title="Terms and Conditions" icon={Scale}>
        <div className="grid min-w-0 grid-cols-1 gap-y-3">
          <CrmReadOnlyTextarea label="Terms and Conditions" value={textOrDash(quote.terms)} />
          <CrmReadOnlyField
            label="AMC/Warranty"
            value={
              quote.amc_warranty === "yes"
                ? "Yes"
                : quote.amc_warranty === "no"
                  ? "No"
                  : "None"
            }
          />
          <CrmReadOnlyField label="Start Date" value={textOrDash(quote.amc_start_date)} />
          <CrmReadOnlyField label="End Date" value={textOrDash(quote.amc_end_date)} />
        </div>
      </CrmSection>

      <CrmSection title="Customer Address Information" icon={MapPin}>
        <div className="grid min-w-0 gap-x-10 gap-y-5 lg:grid-cols-2">
          <div className="grid min-w-0 grid-cols-1 gap-y-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Billing Address</p>
            <CrmReadOnlyField label="Street" value={textOrDash(quote.billing_street)} />
            <CrmReadOnlyField label="City" value={textOrDash(quote.billing_city)} />
            <CrmReadOnlyField label="State" value={textOrDash(quote.billing_state)} />
            <CrmReadOnlyField label="Zip Code" value={textOrDash(quote.billing_zip)} />
            <CrmReadOnlyField label="Country" value={textOrDash(quote.billing_country)} />
          </div>
          <div className="grid min-w-0 grid-cols-1 gap-y-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Shipping Address</p>
            <CrmReadOnlyField label="Street" value={textOrDash(quote.shipping_street)} />
            <CrmReadOnlyField label="City" value={textOrDash(quote.shipping_city)} />
            <CrmReadOnlyField label="State" value={textOrDash(quote.shipping_state)} />
            <CrmReadOnlyField label="Zip Code" value={textOrDash(quote.shipping_zip)} />
            <CrmReadOnlyField label="Country" value={textOrDash(quote.shipping_country)} />
          </div>
        </div>
      </CrmSection>

      <QuoteLineTable
        quoteId={quote.id}
        lines={lines}
        readOnly={readOnlyLines}
        initialDraft={{
          product_name: "",
          line_type: "hardware",
        }}
        onChanged={() => void load()}
      />

      <QuoteSplitPanel quote={quote} contacts={contacts} />
    </CrmPage>
  );
}
