/** Escape text interpolated into HTML generated for print/export windows. */
export function escapeHtml(value: unknown): string {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** Same-origin app paths only - blocks javascript: and protocol-relative hrefs. */
export function safeAppHref(href: string): string {
  const trimmed = href.trim();
  if (!trimmed.startsWith("/") || trimmed.startsWith("//") || trimmed.includes("\\")) {
    return "#";
  }
  // Block embedded active schemes even inside relative paths (defense in depth).
  if (/javascript:|vbscript:|data\s*:/i.test(trimmed)) {
    return "#";
  }
  return trimmed;
}

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

/** Build a same-origin detail href from a validated UUID segment. */
export function safeEntityHref(basePath: string, id: string): string {
  const base = basePath.startsWith("/") ? basePath.replace(/\/$/, "") : `/${basePath.replace(/\/$/, "")}`;
  if (!UUID_RE.test(id)) {
    return "#";
  }
  return safeAppHref(`${base}/${id}`);
}

/** Open a print preview via blob URL (no document.write / injected script tags). */
export function openPrintDocument(html: string, width = 1200, height = 800): void {
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const win = window.open(url, "_blank", `noopener,noreferrer,width=${width},height=${height}`);
  if (!win) {
    URL.revokeObjectURL(url);
    return;
  }
  let printed = false;
  const print = () => {
    if (printed) return;
    printed = true;
    try {
      win.focus();
      win.print();
    } catch {
      /* popup blockers / closed window */
    } finally {
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    }
  };
  win.addEventListener("load", print, { once: true });
  // Fallback if load already fired before listener attached.
  if (win.document.readyState === "complete") {
    print();
  }
}
