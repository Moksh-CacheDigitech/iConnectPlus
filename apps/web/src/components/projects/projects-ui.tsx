/**
 * Projects names for the shared workspace kit (`components/shared`).
 * New code should import from `components/shared` directly.
 */

export {
  ActivityTile as ProjectsActivityTile,
  CountBadge as ProjectsCountBadge,
  DetailGrid as ProjectsDetailGrid,
  DetailItem as ProjectsDetailItem,
  HeadlineBand as ProjectsHeadlineBand,
  HeadlineStat as ProjectsHeadlineStat,
  IconBadge as ProjectsIconBadge,
  InfoBanner as ProjectsInfoBanner,
  ListPanel as ProjectsListPanel,
  Metric as ProjectsMetric,
  MetricStrip as ProjectsMetricStrip,
  ViewAllLink as ProjectsViewAllLink,
  WarnBanner as ProjectsWarnBanner,
  WorkspacePage as ProjectsPage,
  WorkspaceSection as ProjectsSection,
} from "@/components/shared/workspace-ui";

export { KpiCard as ProjectsKpiCard } from "@/components/shared/kpi-card";
export { ErrorBanner as ProjectsErrorBanner } from "@/components/shared/error-banner";
export { ListToolbar as ProjectsListToolbar } from "@/components/shared/list-toolbar";

export {
  CrmPipelineBarChart as ProjectsCountBarChart,
  CrmRevenueBarChart as ProjectsValueBarChart,
  CrmStageDonutChart as ProjectsDonutChart,
  CRM_CHART_COLORS as PROJECTS_CHART_COLORS,
} from "@/components/crm/crm-dashboard-charts";

export {
  SortableTh as ProjectsSortableTh,
  sortRows,
  useTableSort,
  type SortDir,
  type SortValue,
} from "@/components/shared/table-sort";
