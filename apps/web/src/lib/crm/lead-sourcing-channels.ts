/** Hardware / Service sourcing channels driven by selected lead product types. */

export const HARDWARE_SOURCING_CHANNELS = ["B2B", "Open Market"] as const;
export const SERVICE_SOURCING_CHANNELS = ["Outsourced", "Cache Service"] as const;

export type HardwareSourcingChannel = (typeof HARDWARE_SOURCING_CHANNELS)[number];
export type ServiceSourcingChannel = (typeof SERVICE_SOURCING_CHANNELS)[number];

export type LeadSourcingChannels = {
  /** One or more hardware channels (B2B / Open Market). */
  hardware?: string[];
  service?: string;
};

function hasHardwareProductType(productTypes: readonly string[]): boolean {
  return productTypes.some((type) => type.trim().toLowerCase() === "hardware");
}

function hasServiceProductType(productTypes: readonly string[]): boolean {
  const key = (type: string) => type.trim().toLowerCase();
  return productTypes.some((type) => {
    const normalized = key(type);
    return normalized === "services" || normalized === "service";
  });
}

export function leadNeedsHardwareSourcing(productTypes: readonly string[]): boolean {
  return hasHardwareProductType(productTypes);
}

export function leadNeedsServiceSourcing(productTypes: readonly string[]): boolean {
  return hasServiceProductType(productTypes);
}

function normalizeHardwareChannels(value: unknown): string[] | undefined {
  const allowed = new Set<string>(HARDWARE_SOURCING_CHANNELS);
  const fromList = (items: unknown[]): string[] =>
    items
      .map((item) => String(item ?? "").trim())
      .filter((item) => item && allowed.has(item));

  if (Array.isArray(value)) {
    const rows = fromList(value);
    return rows.length > 0 ? rows : undefined;
  }
  if (typeof value === "string") {
    const rows = fromList(value.split(","));
    return rows.length > 0 ? rows : undefined;
  }
  return undefined;
}

export function parseLeadSourcingChannels(
  dealType: string | null | undefined,
): LeadSourcingChannels {
  const raw = (dealType ?? "").trim();
  if (!raw) return {};
  if (raw.startsWith("{")) {
    try {
      const parsed = JSON.parse(raw) as Record<string, unknown>;
      return {
        hardware: normalizeHardwareChannels(parsed.hardware),
        service: typeof parsed.service === "string" ? parsed.service : undefined,
      };
    } catch {
      return {};
    }
  }
  // Legacy free-text deal_type values are not mapped into the new channels.
  return {};
}

export function formatLeadSourcingChannels(
  channels: LeadSourcingChannels,
  productTypes: readonly string[],
): string | null {
  const payload: Record<string, string | string[]> = {};
  if (hasHardwareProductType(productTypes) && channels.hardware && channels.hardware.length > 0) {
    payload.hardware = channels.hardware;
  }
  if (hasServiceProductType(productTypes) && channels.service?.trim()) {
    payload.service = channels.service.trim();
  }
  if (Object.keys(payload).length === 0) return null;
  return JSON.stringify(payload);
}

export function displayLeadSourcingChannels(
  dealType: string | null | undefined,
  productType: string | null | undefined,
): string {
  const types = (productType ?? "")
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
  const channels = parseLeadSourcingChannels(dealType);
  const parts: string[] = [];
  if (hasHardwareProductType(types) && channels.hardware && channels.hardware.length > 0) {
    parts.push(`Hardware: ${channels.hardware.join(", ")}`);
  }
  if (hasServiceProductType(types) && channels.service) {
    parts.push(`Service: ${channels.service}`);
  }
  if (parts.length > 0) return parts.join("; ");
  const legacy = (dealType ?? "").trim();
  if (legacy && !legacy.startsWith("{")) return legacy;
  return "-";
}
