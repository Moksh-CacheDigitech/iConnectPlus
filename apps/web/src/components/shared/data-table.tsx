"use client";

import type { LucideIcon } from "lucide-react";
import { useMemo, useState, type KeyboardEvent, type ReactNode } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorBanner } from "@/components/shared/error-banner";
import { ListToolbar } from "@/components/shared/list-toolbar";
import { dataTableClasses } from "@/components/shared/table-classes";
import { TableSkeletonRows } from "@/components/shared/table-skeleton";
import {
  SortableTh,
  compareSortValues,
  type SortDir,
  type SortValue,
} from "@/components/shared/table-sort";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type DataTableColumn<T> = {
  key: string;
  header: string;
  cell: (row: T, index: number) => ReactNode;
  /** Enables sorting on this column. */
  sortValue?: (row: T) => SortValue;
  /** Text matched by the toolbar search; falls back to `sortValue`. */
  searchValue?: (row: T) => string;
  align?: "left" | "right" | "center";
  className?: string;
  headerClassName?: string;
};

export type DataTableProps<T> = {
  columns: readonly DataTableColumn<T>[];
  rows: readonly T[];
  getRowId: (row: T, index: number) => string;
  /** Toolbar title; the row count badge is shown next to it. */
  title?: string;
  icon?: LucideIcon;
  actions?: ReactNode;
  filters?: ReactNode;
  /** Shows the toolbar search when set. */
  searchPlaceholder?: string;
  defaultSort?: { key: string; dir?: SortDir };
  /** Rows per page; `0` disables pagination. */
  pageSize?: number;
  selectable?: boolean;
  bulkActions?: (selected: T[], clearSelection: () => void) => ReactNode;
  onRowClick?: (row: T) => void;
  /** Prepend a `#` serial column. */
  rowSerial?: boolean;
  loading?: boolean;
  error?: ReactNode;
  onRetry?: () => void;
  /** Rendered when there are no rows (after loading, without error). */
  empty?: ReactNode;
  minWidth?: number;
  className?: string;
  "aria-label"?: string;
};

const ALIGN_CLASS = {
  left: "text-left",
  right: "text-right",
  center: "text-center",
} as const;

function columnSearchText<T>(column: DataTableColumn<T>, row: T): string {
  if (column.searchValue) return column.searchValue(row);
  if (column.sortValue) {
    const v = column.sortValue(row);
    return v == null ? "" : String(v);
  }
  return "";
}

export function DataTable<T>({
  columns,
  rows,
  getRowId,
  title,
  icon,
  actions,
  filters,
  searchPlaceholder,
  defaultSort,
  pageSize = 25,
  selectable = false,
  bulkActions,
  onRowClick,
  rowSerial = false,
  loading = false,
  error,
  onRetry,
  empty,
  minWidth = 640,
  className,
  "aria-label": ariaLabel,
}: DataTableProps<T>) {
  const [query, setQuery] = useState("");
  const [sortKey, setSortKey] = useState<string>(defaultSort?.key ?? "");
  const [sortDir, setSortDir] = useState<SortDir>(defaultSort?.dir ?? "asc");
  const [page, setPage] = useState(0);
  const [selectedIds, setSelectedIds] = useState<ReadonlySet<string>>(() => new Set());

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((row) =>
      columns.some((column) => columnSearchText(column, row).toLowerCase().includes(q)),
    );
  }, [columns, query, rows]);

  const sorted = useMemo(() => {
    const column = columns.find((c) => c.key === sortKey);
    const getValue = column?.sortValue;
    if (!getValue) return filtered;
    return [...filtered].sort((a, b) => compareSortValues(getValue(a), getValue(b), sortDir));
  }, [columns, filtered, sortDir, sortKey]);

  const paginated = pageSize > 0;
  const pageCount = paginated ? Math.max(1, Math.ceil(sorted.length / pageSize)) : 1;
  const safePage = Math.min(page, pageCount - 1);
  const pageStart = paginated ? safePage * pageSize : 0;
  const visible = paginated ? sorted.slice(pageStart, pageStart + pageSize) : sorted;

  const selectedRows = useMemo(
    () => (selectable ? rows.filter((row, i) => selectedIds.has(getRowId(row, i))) : []),
    [getRowId, rows, selectable, selectedIds],
  );
  const visibleIds = visible.map((row) => getRowId(row, rows.indexOf(row)));
  const allVisibleSelected =
    visibleIds.length > 0 && visibleIds.every((id) => selectedIds.has(id));

  const clearSelection = () => setSelectedIds(new Set());

  const toggleRow = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleVisible = () => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (allVisibleSelected) visibleIds.forEach((id) => next.delete(id));
      else visibleIds.forEach((id) => next.add(id));
      return next;
    });
  };

  const onSort = (key: string) => {
    if (key === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
    setPage(0);
  };

  const onRowKeyDown = (event: KeyboardEvent<HTMLTableRowElement>, row: T) => {
    if (!onRowClick) return;
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onRowClick(row);
    }
  };

  const colSpan = columns.length + (selectable ? 1 : 0) + (rowSerial ? 1 : 0);
  const showToolbar = Boolean(title || actions || filters || searchPlaceholder);
  const showError = !loading && Boolean(error);
  const showEmpty = !loading && !error && sorted.length === 0;

  return (
    <div className={cn(dataTableClasses.shell, className)}>
      {showToolbar ? (
        <ListToolbar
          title={title}
          count={loading ? undefined : sorted.length}
          icon={icon}
          actions={actions}
          filters={filters}
          search={
            searchPlaceholder
              ? {
                  value: query,
                  onChange: (value) => {
                    setQuery(value);
                    setPage(0);
                  },
                  placeholder: searchPlaceholder,
                }
              : undefined
          }
        />
      ) : null}

      {selectable && selectedRows.length > 0 ? (
        <div className="flex flex-wrap items-center gap-2 border-b border-border/70 bg-primary/5 px-3 py-2 text-sm sm:px-4">
          <span className="font-medium text-foreground tabular-nums">
            {selectedRows.length} selected
          </span>
          <div className="flex flex-wrap items-center gap-2">
            {bulkActions?.(selectedRows, clearSelection)}
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="ml-auto h-7 cursor-pointer text-xs"
            onClick={clearSelection}
          >
            Clear selection
          </Button>
        </div>
      ) : null}

      {showError ? (
        <div className="p-3 sm:p-4">
          <ErrorBanner onRetry={onRetry}>{error}</ErrorBanner>
        </div>
      ) : (
        <div className={dataTableClasses.scroll}>
          <table
            className={dataTableClasses.table}
            style={{ minWidth }}
            aria-label={ariaLabel ?? title}
            aria-busy={loading || undefined}
          >
            <thead>
              <tr className={dataTableClasses.thead}>
                {selectable ? (
                  <th className="w-10 px-3 py-2" scope="col">
                    <input
                      type="checkbox"
                      className="size-4 cursor-pointer rounded border-border accent-primary"
                      checked={allVisibleSelected}
                      onChange={toggleVisible}
                      aria-label="Select all rows on this page"
                      disabled={loading || visible.length === 0}
                    />
                  </th>
                ) : null}
                {rowSerial ? (
                  <th className="w-10 px-3 py-2 text-center tabular-nums" scope="col">
                    #
                  </th>
                ) : null}
                {columns.map((column) =>
                  column.sortValue ? (
                    <SortableTh
                      key={column.key}
                      label={column.header}
                      sortKey={column.key}
                      activeKey={sortKey}
                      dir={sortDir}
                      onSort={onSort}
                      align={column.align === "right" ? "right" : "left"}
                      className={cn(
                        dataTableClasses.th,
                        ALIGN_CLASS[column.align ?? "left"],
                        column.headerClassName,
                      )}
                    />
                  ) : (
                    <th
                      key={column.key}
                      scope="col"
                      className={cn(
                        dataTableClasses.th,
                        ALIGN_CLASS[column.align ?? "left"],
                        column.headerClassName,
                      )}
                    >
                      {column.header}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {loading ? <TableSkeletonRows rows={6} columns={colSpan} /> : null}
              {showEmpty ? (
                <tr>
                  <td colSpan={colSpan}>
                    {empty ?? (
                      <EmptyState
                        compact
                        preset={query.trim() ? "no-results" : "no-records"}
                      />
                    )}
                  </td>
                </tr>
              ) : null}
              {!loading && !error
                ? visible.map((row, i) => {
                    const id = getRowId(row, rows.indexOf(row));
                    const selected = selectedIds.has(id);
                    return (
                      <tr
                        key={id}
                        className={cn(
                          dataTableClasses.tr,
                          selected && "bg-primary/5",
                          onRowClick &&
                            "cursor-pointer focus-visible:bg-muted/40 focus-visible:outline-none",
                        )}
                        onClick={onRowClick ? () => onRowClick(row) : undefined}
                        onKeyDown={onRowClick ? (e) => onRowKeyDown(e, row) : undefined}
                        tabIndex={onRowClick ? 0 : undefined}
                        aria-selected={selectable ? selected : undefined}
                      >
                        {selectable ? (
                          <td className="w-10 px-3 py-2" onClick={(e) => e.stopPropagation()}>
                            <input
                              type="checkbox"
                              className="size-4 cursor-pointer rounded border-border accent-primary"
                              checked={selected}
                              onChange={() => toggleRow(id)}
                              aria-label={`Select row ${pageStart + i + 1}`}
                            />
                          </td>
                        ) : null}
                        {rowSerial ? (
                          <td className="w-10 px-3 py-2 text-center text-xs text-muted-foreground tabular-nums">
                            {pageStart + i + 1}
                          </td>
                        ) : null}
                        {columns.map((column) => (
                          <td
                            key={column.key}
                            className={cn(
                              dataTableClasses.td,
                              ALIGN_CLASS[column.align ?? "left"],
                              column.align === "right" && "tabular-nums",
                              column.className,
                            )}
                          >
                            {column.cell(row, pageStart + i)}
                          </td>
                        ))}
                      </tr>
                    );
                  })
                : null}
            </tbody>
          </table>
        </div>
      )}

      {paginated && !loading && !error && pageCount > 1 ? (
        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border/70 px-3 py-2 text-xs text-muted-foreground sm:px-4">
          <span className="tabular-nums">
            {pageStart + 1}–{Math.min(pageStart + pageSize, sorted.length)} of {sorted.length}
          </span>
          <div className="flex items-center gap-1">
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-7 cursor-pointer px-2"
              onClick={() => setPage(safePage - 1)}
              disabled={safePage === 0}
              aria-label="Previous page"
            >
              <ChevronLeft className="size-3.5" aria-hidden />
            </Button>
            <span className="px-2 tabular-nums">
              Page {safePage + 1} of {pageCount}
            </span>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-7 cursor-pointer px-2"
              onClick={() => setPage(safePage + 1)}
              disabled={safePage >= pageCount - 1}
              aria-label="Next page"
            >
              <ChevronRight className="size-3.5" aria-hidden />
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
