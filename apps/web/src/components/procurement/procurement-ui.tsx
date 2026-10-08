/**
 * Procurement names for the shared workspace kit (`components/shared`).
 * New code should import from `components/shared` directly.
 */
import { dataTableClasses } from "@/components/shared/table-classes";

/** Table + form class map; table entries come from the shared `dataTableClasses`. */
export const procurementUi = {
  page: "space-y-4",
  tableShell: dataTableClasses.shell,
  tableScroll: dataTableClasses.scroll,
  table: dataTableClasses.table,
  thead: dataTableClasses.thead,
  th: dataTableClasses.th,
  tr: dataTableClasses.tr,
  td: dataTableClasses.td,
  tdMuted: dataTableClasses.tdMuted,
  tdNumeric: dataTableClasses.tdNumeric,
  empty: dataTableClasses.empty,
  searchRow: "flex justify-end",
  searchInput:
    "h-8 w-full max-w-[220px] border-border/70 bg-background text-sm shadow-none transition-colors duration-200",
  rowActions: "flex flex-wrap items-center gap-1",
  actionBtn: "h-7 cursor-pointer gap-1 px-2 text-xs font-medium transition-colors duration-200",
  statusBadge: "text-[10px] font-medium uppercase tracking-wide",
  sectionCard: "space-y-3 rounded-xl border border-border/70 bg-card p-3 shadow-sm sm:p-4",
  sectionTitle: "text-xs font-semibold uppercase tracking-[0.06em] text-muted-foreground",
} as const;

export {
  CountBadge as ProcurementCountBadge,
  HeadlineBand as ProcurementHeadlineBand,
  HeadlineStat as ProcurementHeadlineStat,
  IconBadge as ProcurementIconBadge,
  InfoBanner as ProcurementInfoBanner,
  ListPanel as ProcurementListPanel,
  ViewAllLink as ProcurementViewAllLink,
  WarnBanner as ProcurementWarnBanner,
  WorkspacePage as ProcurementPage,
  WorkspaceSection as ProcurementSection,
} from "@/components/shared/workspace-ui";

export { KpiCard as ProcurementKpiCard } from "@/components/shared/kpi-card";
export { ErrorBanner as ProcurementErrorBanner } from "@/components/shared/error-banner";
