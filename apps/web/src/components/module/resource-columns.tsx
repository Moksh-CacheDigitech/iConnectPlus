import type { DataTableColumn } from "@/components/shared/data-table";
import type { SortValue } from "@/components/shared/table-sort";
import { formatCell, humanizeHeader, pickColumns } from "@/lib/resource-display";
import { cn } from "@/lib/utils";

type ResourceRow = Record<string, unknown>;

/** `DataTable` columns for a generic API resource, picked from the first row's fields. */
export function buildResourceColumns(
  rows: ResourceRow[],
  maxColumns?: number,
): DataTableColumn<ResourceRow>[] {
  const keys = pickColumns(rows);
  return keys.slice(0, maxColumns ?? keys.length).map((key, colIdx) => ({
    key,
    header: humanizeHeader(key),
    cell: (row) => (
      <span
        className={cn(
          "block max-w-[260px] truncate",
          colIdx === 0 ? "font-medium text-foreground" : "text-muted-foreground",
        )}
        title={formatCell(key, row[key])}
      >
        {formatCell(key, row[key])}
      </span>
    ),
    sortValue: (row) => {
      const v = row[key];
      return typeof v === "object" ? undefined : (v as SortValue);
    },
    searchValue: (row) => formatCell(key, row[key]),
  }));
}
