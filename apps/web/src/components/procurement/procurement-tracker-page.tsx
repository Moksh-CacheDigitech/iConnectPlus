"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { FileSpreadsheet, RefreshCw, Upload } from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatApiError } from "@/services/api-client";
import {
  getSheetTracker,
  listSheetTrackers,
  uploadSheetTracker,
  type SheetTrackerDetail,
  type SheetTrackerSummary,
} from "@/services/sheet-tracker-service";

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const value = String(reader.result ?? "");
      resolve(value.includes(",") ? value.split(",", 2)[1] : value);
    };
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

function formatWhen(value: string | null | undefined): string {
  if (!value) return "—";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleString();
}

function mergeSummary(detail: SheetTrackerDetail | null): string | null {
  const merge = detail?.last_merge;
  if (!merge) return null;
  const bits: string[] = [];
  if (merge.added_columns.length) {
    bits.push(
      `${merge.added_columns.length} column${merge.added_columns.length === 1 ? "" : "s"} (${merge.added_columns.join(", ")})`,
    );
  }
  if (merge.added_rows) {
    bits.push(`${merge.added_rows} new row${merge.added_rows === 1 ? "" : "s"}`);
  }
  if (merge.updated_rows) {
    bits.push(`${merge.updated_rows} row${merge.updated_rows === 1 ? "" : "s"} filled`);
  }
  if (!bits.length) return "No new rows or columns in the last file.";
  return `Last upload added ${bits.join(" · ")}.`;
}

/** Repeated Excel uploads merge into one extracted table (new columns and rows). */
export function ProcurementTrackerPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [summaries, setSummaries] = useState<SheetTrackerSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [detail, setDetail] = useState<SheetTrackerDetail | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadList = useCallback(async (preferId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const rows = await listSheetTrackers();
      setSummaries(rows);
      const nextId = preferId && rows.some((r) => r.id === preferId) ? preferId : (rows[0]?.id ?? "");
      setSelectedId(nextId);
      if (nextId) {
        setDetail(await getSheetTracker(nextId));
      } else {
        setDetail(null);
      }
    } catch (err) {
      setError(formatApiError(err, "Unable to load trackers"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => void loadList(), 0);
    return () => window.clearTimeout(timer);
  }, [loadList]);

  async function onSelect(id: string) {
    setSelectedId(id);
    if (!id) {
      setDetail(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setDetail(await getSheetTracker(id));
    } catch (err) {
      setError(formatApiError(err, "Unable to open tracker table"));
    } finally {
      setLoading(false);
    }
  }

  async function onUpload() {
    if (!file) {
      setError("Choose an Excel file (.xlsx).");
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const uploaded = await uploadSheetTracker({
        file_name: file.name,
        content_base64: await fileToBase64(file),
        content_type: file.type || undefined,
        tracker_id: selectedId || null,
      });
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      await loadList(uploaded.id);
    } catch (err) {
      setError(formatApiError(err, "Unable to upload tracker"));
    } finally {
      setUploading(false);
    }
  }

  const columns = detail?.columns ?? [];
  const rows = detail?.rows ?? [];
  const hint = mergeSummary(detail);

  return (
    <div className="space-y-4">
      <PageHeader
        title="Tracker upload"
        description="Upload Excel sheets as often as needed. New columns and rows are added to the extracted table; existing cells stay as they are."
        actions={
          <Button
            variant="outline"
            size="sm"
            className="cursor-pointer transition-colors duration-200"
            onClick={() => void loadList(selectedId)}
            disabled={loading || uploading}
          >
            <RefreshCw className="size-3.5" /> Refresh
          </Button>
        }
      />

      {error ? (
        <div className="rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive" role="alert">
          {error}
        </div>
      ) : null}

      <section className="rounded-xl border border-border/70 bg-card p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
          <div className="min-w-0 flex-1 space-y-1.5">
            <label htmlFor="proc-sheet-tracker" className="text-sm font-medium">
              Tracker table
            </label>
            <select
              id="proc-sheet-tracker"
              value={selectedId}
              onChange={(event) => void onSelect(event.target.value)}
              className="flex h-9 w-full cursor-pointer rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              disabled={uploading || loading}
            >
              <option value="">New table from this file</option>
              {summaries.map((row) => (
                <option key={row.id} value={row.id}>
                  {row.name} · {row.row_count} rows · {row.column_count} cols
                </option>
              ))}
            </select>
          </div>
          <div className="min-w-0 flex-1 space-y-1.5">
            <label htmlFor="proc-sheet-file" className="text-sm font-medium">
              Excel file
            </label>
            <Input
              ref={fileInputRef}
              id="proc-sheet-file"
              type="file"
              accept=".xlsx,.xlsm,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              className="h-9 cursor-pointer text-sm file:mr-3 file:cursor-pointer"
              disabled={uploading}
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </div>
          <Button
            size="sm"
            className="h-9 cursor-pointer transition-opacity duration-200 hover:opacity-90"
            disabled={uploading || !file}
            onClick={() => void onUpload()}
          >
            <Upload className="size-3.5" />
            {uploading ? "Uploading…" : selectedId ? "Merge into table" : "Create table"}
          </Button>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Matching uses the first column as the row key. New headers become columns; new keys become rows.
        </p>
      </section>

      {hint ? (
        <p className="flex items-start gap-2 rounded-lg border border-border/70 bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
          <FileSpreadsheet className="mt-0.5 size-3.5 shrink-0" aria-hidden />
          {hint}
        </p>
      ) : null}

      <section className="overflow-hidden rounded-xl border border-border/70 bg-card">
        <div className="border-b border-border/70 px-4 py-3">
          <h2 className="text-sm font-semibold">
            {detail ? detail.name : "Extracted table"}
          </h2>
          <p className="text-xs text-muted-foreground">
            {detail
              ? `${detail.row_count} rows · ${detail.column_count} columns · last file ${detail.last_file_name ?? "—"} · ${formatWhen(detail.last_upload_at)}`
              : "Upload a workbook to extract the first sheet."}
          </p>
        </div>
        <div className="erp-scroll max-h-[min(70vh,720px)] overflow-auto">
          {detail && columns.length ? (
            <table className="w-full min-w-max text-left text-[13px]">
              <thead className="sticky top-0 z-10 border-b border-border/70 bg-muted/80 text-[11px] text-muted-foreground backdrop-blur-sm">
                <tr>
                  {columns.map((col) => (
                    <th key={col.id} className="whitespace-nowrap px-3 py-2 font-semibold">
                      {col.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => (
                  <tr key={`${index}-${row[columns[0]?.id ?? ""] ?? ""}`} className="border-b border-border/40">
                    {columns.map((col) => (
                      <td key={col.id} className="max-w-56 truncate px-3 py-1.5 tabular-nums" title={row[col.id] ?? ""}>
                        {row[col.id] || "—"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="px-4 py-10 text-center text-sm text-muted-foreground">
              {loading ? "Loading tracker…" : "No extracted table yet. Create one from an Excel file."}
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
