/**
 * Dense table class map (~36px rows). `DataTable` uses it internally; hand-built
 * tables that cannot move to `DataTable` yet use it so density stays identical.
 */
export const dataTableClasses = {
  shell: "overflow-hidden rounded-xl border border-border/70 bg-card shadow-sm",
  scroll: "erp-scroll overflow-x-auto",
  table: "w-full text-left text-[13px] leading-5",
  thead:
    "border-b border-border/80 bg-muted/60 text-xs font-semibold tracking-wide text-foreground uppercase",
  th: "px-3 py-2 font-semibold whitespace-nowrap",
  tr: "border-b border-border/50 transition-colors duration-150 last:border-0 hover:bg-muted/40 motion-reduce:transition-none",
  td: "px-3 py-2 align-middle",
  tdMuted: "px-3 py-2 align-middle text-muted-foreground",
  tdNumeric: "px-3 py-2 align-middle tabular-nums",
  empty: "px-3 py-12 text-center text-sm text-muted-foreground",
} as const;
