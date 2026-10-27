"use client";

import { useEffect, useState } from "react";
import { PhoneCall } from "lucide-react";

import { CrmSection } from "@/components/crm/crm-ui";
import {
  FinanceField,
  FinanceSelect,
} from "@/components/finance/journals/finance-form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import {
  updateSalesLead,
  type SalesLead,
} from "@/services/sales-crm-service";

type LeadPresalesCallSectionProps = {
  lead: SalesLead;
  onSaved: (lead: SalesLead) => void;
};

function needsPresalesCallGate(lead: SalesLead): boolean {
  return Boolean(lead.company_account_id) && (Boolean(lead.requires_boq) || Boolean(lead.requires_sow));
}

function isCallReady(lead: SalesLead): boolean {
  return (
    lead.presales_call_aligned === true &&
    Boolean(lead.presales_call_contact_name?.trim())
  );
}

export function LeadPresalesCallSection({ lead, onSaved }: LeadPresalesCallSectionProps) {
  const [aligned, setAligned] = useState<"yes" | "no" | "">(
    lead.presales_call_aligned === true ? "yes" : lead.presales_call_aligned === false ? "no" : "",
  );
  const [contactName, setContactName] = useState(lead.presales_call_contact_name ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setAligned(
      lead.presales_call_aligned === true
        ? "yes"
        : lead.presales_call_aligned === false
          ? "no"
          : "",
    );
    setContactName(lead.presales_call_contact_name ?? "");
  }, [lead.id, lead.presales_call_aligned, lead.presales_call_contact_name]);

  if (!needsPresalesCallGate(lead)) return null;

  const ready = isCallReady(lead);
  const canEdit = lead.blueprint_state === "open";

  async function onSave() {
    if (!canEdit) return;
    if (!aligned) {
      setError("Select Yes or No for Call aligned with PreSales.");
      return;
    }
    if (aligned === "yes" && !contactName.trim()) {
      setError("Enter the PreSales contact person name when Call aligned is Yes.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const updated = await updateSalesLead(lead.id, {
        version: lead.version,
        presales_call_aligned: aligned === "yes",
        presales_call_contact_name: aligned === "yes" ? contactName.trim() : contactName.trim() || null,
      });
      onSaved(updated);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to save PreSales call step");
    } finally {
      setSaving(false);
    }
  }

  return (
    <CrmSection title="PreSales Call Alignment" icon={PhoneCall}>
      <p className="mb-3 text-sm text-muted-foreground">
        Confirm the PreSales call before BOQ and SOW attachment is routed to My Jobs.
      </p>
      <div className="grid gap-x-10 gap-y-3 md:grid-cols-2">
        <FinanceField label="Call aligned with PreSales? *">
          <FinanceSelect
            value={aligned}
            onChange={(event) => {
              const next = event.target.value as "yes" | "no" | "";
              setAligned(next);
              if (next !== "yes") setError(null);
            }}
            disabled={!canEdit || saving}
            required
          >
            <option value="">Select…</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
          </FinanceSelect>
        </FinanceField>
        <FinanceField label="PreSales contact person *">
          <Input
            value={contactName}
            onChange={(event) => setContactName(event.target.value)}
            placeholder="Contact person name"
            disabled={!canEdit || saving || aligned !== "yes"}
          />
        </FinanceField>
      </div>
      {error ? <p className="mt-2 text-sm text-destructive">{error}</p> : null}
      {ready ? (
        <p className="mt-3 text-sm text-emerald-700">
          Call aligned — BOQ / SOW attachment can proceed in My Jobs.
        </p>
      ) : aligned === "no" ? (
        <p className="mt-3 text-sm text-amber-700">
          Call not aligned yet. Change to Yes and add the contact person to unlock BOQ / SOW.
        </p>
      ) : (
        <p className="mt-3 text-sm text-muted-foreground">
          Save Yes with a contact person name to unlock BOQ and SOW.
        </p>
      )}
      {canEdit ? (
        <div className="mt-3">
          <Button
            type="button"
            size="sm"
            className="cursor-pointer"
            disabled={saving}
            onClick={() => void onSave()}
          >
            {saving ? "Saving…" : ready ? "Update PreSales call" : "Save & continue to BOQ / SOW"}
          </Button>
        </div>
      ) : null}
    </CrmSection>
  );
}

export function leadNeedsPresalesCallGate(lead: SalesLead): boolean {
  return needsPresalesCallGate(lead);
}

export function leadPresalesCallReady(lead: SalesLead): boolean {
  if (!needsPresalesCallGate(lead)) return true;
  return isCallReady(lead);
}
