import { listVendorOptions } from "@/services/procurement-service";

const RAW_LEAD_DISTRIBUTOR_OPTIONS = [
  "IN STOCK",
  "Redington",
  "Ingram Micro",
  "TD SYNNEX",
  "Tech Data",
  "Rashi Peripherals (RP Tech)",
  "Savex Technologies",
  "Supertron Electronics",
  "Iris Global Services",
  "Compuage Infocom",
  "e-Mall",
  "Exclusive Networks",
  "Westcon-Comstor",
  "Arrow Electronics",
  "Avnet",
  "Synnex",
  "ScanSource",
  "VAD Technologies",
  "CMS IT Services",
  "Beetel Teletech",
  "Creative Newtech",
  "Iris Global",
  "Astrum",
  "Nuvias",
  "Crayon",
  "Pax8",
  "ALSO",
  "Exertis",
  "D&H Distributing",
  "SYNNEX",
] as const;

export const LEAD_DISTRIBUTOR_OPTIONS: readonly string[] = [...new Set(RAW_LEAD_DISTRIBUTOR_OPTIONS)];

export const LEAD_DISTRIBUTOR_SEPARATOR = ", ";

export function parseLeadDistributorNames(value: string | null | undefined): string[] {
  if (!value?.trim()) return [];
  return value
    .split(",")
    .map((name) => name.trim())
    .filter(Boolean);
}

export function formatLeadDistributorNames(names: readonly string[]): string {
  return names.join(LEAD_DISTRIBUTOR_SEPARATOR);
}

function mergeDistributorNames(...groups: readonly (readonly string[])[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const group of groups) {
    for (const raw of group) {
      const name = raw.trim();
      if (!name) continue;
      const key = name.toLowerCase();
      if (seen.has(key)) continue;
      seen.add(key);
      out.push(name);
    }
  }
  return out;
}

/** Preset lead distributors plus any custom names saved on the lead (for single-select dropdowns). */
export function buildLeadDistributorDropdownOptions(
  leadDistributorField: string | null | undefined,
  scmVendorNames: readonly string[] = [],
): string[] {
  return mergeDistributorNames(
    LEAD_DISTRIBUTOR_OPTIONS,
    scmVendorNames,
    parseLeadDistributorNames(leadDistributorField),
  );
}

/** Load SCM Vendors master list and merge with presets + any names already on the lead. */
export async function loadCrmDistributorOptions(
  leadDistributorField?: string | null,
): Promise<string[]> {
  const scmNames = await listVendorOptions()
    .then((rows) =>
      rows
        .filter((vendor) => (vendor.status || "active").toLowerCase() !== "inactive")
        .map((vendor) => vendor.label.trim())
        .filter(Boolean),
    )
    .catch(() => [] as string[]);
  return buildLeadDistributorDropdownOptions(leadDistributorField, scmNames);
}
