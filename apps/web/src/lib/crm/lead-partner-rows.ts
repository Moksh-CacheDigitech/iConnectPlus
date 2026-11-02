/** Structured OEM / distributor rows on CRM leads (table UI ↔ scalar DB columns). */

import { formatLeadDistributorNames, parseLeadDistributorNames } from "@/lib/crm/lead-distributor-options";
import { formatLeadOemNames, parseLeadOemNames } from "@/lib/crm/lead-oem-options";

/** Separates parallel contact values when multiple partner rows are saved. */
export const LEAD_PARTNER_CONTACT_SEP = " | ";

export type LeadPartnerRow = {
  id: string;
  name: string;
  contact_person: string;
  contact_number: string;
  contact_email: string;
};

export function emptyLeadPartnerRow(): LeadPartnerRow {
  return {
    id:
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `row-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    name: "",
    contact_person: "",
    contact_number: "",
    contact_email: "",
  };
}

function splitContactField(value: string | null | undefined): string[] {
  if (!value?.trim()) return [];
  if (value.includes(LEAD_PARTNER_CONTACT_SEP)) {
    return value.split(LEAD_PARTNER_CONTACT_SEP).map((part) => part.trim());
  }
  return [value.trim()];
}

function joinContactField(parts: readonly string[]): string {
  if (parts.every((part) => !part.trim())) return "";
  return parts.map((part) => part.trim()).join(LEAD_PARTNER_CONTACT_SEP);
}

function rowsFromParallelFields(
  names: readonly string[],
  persons: readonly string[],
  numbers: readonly string[],
  emails: readonly string[],
): LeadPartnerRow[] {
  const count = Math.max(names.length, persons.length, numbers.length, emails.length, 0);
  if (count === 0) return [emptyLeadPartnerRow()];
  return Array.from({ length: count }, (_, index) => ({
    ...emptyLeadPartnerRow(),
    name: names[index] ?? "",
    contact_person: persons[index] ?? "",
    contact_number: numbers[index] ?? "",
    contact_email: emails[index] ?? "",
  }));
}

export function parseOemPartnerRows(input: {
  oem_name?: string | null;
  oem_contact_person?: string | null;
  oem_contact_number?: string | null;
  oem_contact_email?: string | null;
}): LeadPartnerRow[] {
  return rowsFromParallelFields(
    parseLeadOemNames(input.oem_name),
    splitContactField(input.oem_contact_person),
    splitContactField(input.oem_contact_number),
    splitContactField(input.oem_contact_email),
  );
}

export function parseDistributorPartnerRows(input: {
  distributor_name?: string | null;
  distributor_contact_person?: string | null;
  distributor_contact?: string | null;
  distributor_contact_email?: string | null;
}): LeadPartnerRow[] {
  return rowsFromParallelFields(
    parseLeadDistributorNames(input.distributor_name),
    splitContactField(input.distributor_contact_person),
    splitContactField(input.distributor_contact),
    splitContactField(input.distributor_contact_email),
  );
}

/** Drop blank trailing rows; keep at least one empty row for the editor when nothing filled. */
export function normalizePartnerRowsForSave(rows: readonly LeadPartnerRow[]): LeadPartnerRow[] {
  const filled = rows.filter(
    (row) =>
      row.name.trim() ||
      row.contact_person.trim() ||
      row.contact_number.trim() ||
      row.contact_email.trim(),
  );
  return filled.length > 0 ? filled : [];
}

export function formatOemPartnerFields(rows: readonly LeadPartnerRow[]): {
  oem_name: string;
  oem_contact_person: string;
  oem_contact_number: string;
  oem_contact_email: string;
} {
  const saved = normalizePartnerRowsForSave(rows);
  return {
    oem_name: formatLeadOemNames(saved.map((row) => row.name.trim()).filter(Boolean)),
    oem_contact_person: joinContactField(saved.map((row) => row.contact_person)),
    oem_contact_number: joinContactField(saved.map((row) => row.contact_number)),
    oem_contact_email: joinContactField(saved.map((row) => row.contact_email)),
  };
}

export function formatDistributorPartnerFields(rows: readonly LeadPartnerRow[]): {
  distributor_name: string;
  distributor_contact_person: string;
  distributor_contact: string;
  distributor_contact_email: string;
} {
  const saved = normalizePartnerRowsForSave(rows);
  return {
    distributor_name: formatLeadDistributorNames(
      saved.map((row) => row.name.trim()).filter(Boolean),
    ),
    distributor_contact_person: joinContactField(saved.map((row) => row.contact_person)),
    distributor_contact: joinContactField(saved.map((row) => row.contact_number)),
    distributor_contact_email: joinContactField(saved.map((row) => row.contact_email)),
  };
}
