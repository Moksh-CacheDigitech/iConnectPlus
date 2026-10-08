/**
 * Display helpers for generic API resource rows (column picking, labels, cell formatting).
 * Shared by `ResourceListView` and `ModuleHub`.
 */

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

const REF_KEYS = new Set([
  "document_number",
  "entry_number",
  "register_number",
  "message_number",
  "retry_number",
  "dlq_number",
  "journal_number",
  "request_number",
  "channel_number",
  "policy_number",
  "risk_number",
  "capa_number",
  "assessment_number",
  "framework_code",
  "requirement_code",
  "audit_number",
  "incident_number",
  "exception_number",
  "control_number",
]);

export function normalizeRows(data: unknown): Record<string, unknown>[] {
  if (Array.isArray(data)) {
    return data.filter((row): row is Record<string, unknown> => !!row && typeof row === "object");
  }
  if (data && typeof data === "object") {
    const obj = data as Record<string, unknown>;
    for (const key of ["items", "results", "records", "data", "nodes", "tree"]) {
      if (Array.isArray(obj[key])) {
        return normalizeRows(obj[key]);
      }
    }
    return [obj];
  }
  return [];
}

export function isUuidLike(value: unknown): boolean {
  return typeof value === "string" && UUID_RE.test(value);
}

export function isHiddenKey(key: string): boolean {
  const k = key.toLowerCase();
  if (k === "id" || k === "version" || k === "tenant_id") return true;
  if (k.endsWith("_id") || k.endsWith("_ids")) return true;
  if (k.includes("password") || k.includes("secret") || k.includes("token")) return true;
  if (k.endsWith("_json") || k === "metadata" || k === "config_json" || k === "score_breakdown")
    return true;
  return false;
}

export function scoreColumn(key: string, sample: unknown): number {
  const k = key.toLowerCase();
  if (isHiddenKey(k)) return -100;
  if (isUuidLike(sample)) return -50;

  let score = 0;
  if (/(^|_)(name|title|subject|label)$/.test(k)) score += 100;
  else if (k.includes("name") || k.includes("title") || k.includes("subject")) score += 90;
  else if (REF_KEYS.has(k) || /(^|_)(code|number)$/.test(k) || k.endsWith("_code") || k.endsWith("_number"))
    score += 95;
  else if (k.includes("email") || k.includes("mobile") || k.includes("phone")) score += 70;
  else if (k === "status" || k.endsWith("_status") || k === "priority" || k === "type" || k === "level")
    score += 60;
  else if (
    k.includes("amount") ||
    k.includes("salary") ||
    k.includes("gross") ||
    k.includes("net") ||
    k.includes("qty") ||
    k.includes("quantity") ||
    k.includes("cost") ||
    k.includes("total")
  )
    score += 55;
  else if (k.includes("date") || k.includes("message")) score += 40;
  else if (typeof sample === "string" && sample.length > 0 && sample.length < 80) score += 25;
  else if (typeof sample === "number" || typeof sample === "boolean") score += 10;
  else score += 1;

  return score;
}

export function humanizeHeader(key: string): string {
  const k = key.toLowerCase();
  if (REF_KEYS.has(k)) return "Ref";
  if (k.endsWith("_code") || k === "code") return "Code";
  return key
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .replace(/\bId\b/g, "ID");
}

export function pickColumns(rows: Record<string, unknown>[]): string[] {
  if (rows.length === 0) return [];
  const keys = Object.keys(rows[0]);
  const ranked = keys
    .map((key) => ({ key, score: scoreColumn(key, rows[0][key]) }))
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score || a.key.localeCompare(b.key));

  const selected = ranked.slice(0, 7).map((x) => x.key);
  if (selected.length >= 2) return selected;

  return keys
    .filter((k) => {
      const v = rows[0][k];
      if (v != null && typeof v === "object") return false;
      if (isHiddenKey(k) || isUuidLike(v)) return false;
      return true;
    })
    .slice(0, 6);
}

export function formatMoney(value: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatCell(key: string, value: unknown): string {
  if (value == null || value === "") return "-";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") {
    const k = key.toLowerCase();
    if (
      k.includes("amount") ||
      k.includes("salary") ||
      k.includes("gross") ||
      k.includes("net") ||
      k.includes("deduction") ||
      k.includes("cost") ||
      (k.includes("total") && !k.includes("count"))
    ) {
      return formatMoney(value);
    }
    if (k.includes("qty") || k.includes("quantity") || k.includes("rate")) {
      return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(value);
    }
    return Number.isFinite(value) ? String(value) : "-";
  }
  if (typeof value === "object") {
    if (Array.isArray(value)) return `${value.length} items`;
    return "-";
  }
  const s = String(value);
  if (UUID_RE.test(s)) return "-";
  if (/^\d{4}-\d{2}-\d{2}T/.test(s)) {
    const d = new Date(s);
    if (!Number.isNaN(d.getTime())) return d.toLocaleString("en-IN");
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
  if (s.length > 48) return `${s.slice(0, 45)}…`;
  return s;
}

export function displayLabel(row: Record<string, unknown>): string {
  const candidates = [
    "full_name",
    "employee_name",
    "customer_name",
    "vendor_name",
    "product_name",
    "project_name",
    "asset_name",
    "account_name",
    "dashboard_name",
    "store_name",
    "policy_name",
    "folder_name",
    "display_name",
    "first_name",
    "name",
    "title",
    "subject",
    "document_number",
    "entry_number",
    "register_number",
    "code",
  ];
  for (const key of candidates) {
    const v = row[key];
    if (typeof v === "string" && v.trim() && !UUID_RE.test(v)) {
      if (key === "first_name" && typeof row.last_name === "string") {
        return `${v} ${row.last_name}`.trim();
      }
      return v;
    }
  }
  if (typeof row.first_name === "string" && typeof row.last_name === "string") {
    const n = `${row.first_name} ${row.last_name}`.trim();
    if (n) return n;
  }
  return "";
}


/** Adds a `name` column when the row only has a derived display label. */
export function enrichRows(rows: Record<string, unknown>[]): Record<string, unknown>[] {
  return rows.map((row) => {
    const label = displayLabel(row);
    if (!label) return row;
    if (!("name" in row) && !("full_name" in row) && !("title" in row) && !("subject" in row)) {
      return { name: label, ...row };
    }
    return row;
  });
}

/** Total record count from a list payload (`total` when paginated, else row count). */
export function listTotal(data: unknown): number {
  if (data && typeof data === "object" && !Array.isArray(data)) {
    const total = (data as Record<string, unknown>).total;
    if (typeof total === "number" && Number.isFinite(total)) return total;
  }
  return normalizeRows(data).length;
}
