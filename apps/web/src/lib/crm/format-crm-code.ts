/**
 * Display CRM document codes without zero padding on the sequence part.
 * Stored codes are unchanged (e.g. LEAD-2026-000014 stays in the database).
 * Deal-scoped codes keep their suffix: DR-2026-0012/Q2 → DR-2026-12/Q2.
 */
export function formatCrmCode(code: string | null | undefined): string {
  if (!code) return "";
  const trimmed = code.trim();
  // PREFIX-YYYY-000014 → PREFIX-YYYY-14, with an optional /Q1 or /OVF1 suffix
  const yearSeq = trimmed.match(/^([A-Za-z]+-\d{4}-)0*([1-9]\d*|0)(\/[A-Za-z]+\d+)?$/);
  if (yearSeq) {
    return `${yearSeq[1]}${yearSeq[2]}${yearSeq[3] ?? ""}`;
  }
  return trimmed;
}
