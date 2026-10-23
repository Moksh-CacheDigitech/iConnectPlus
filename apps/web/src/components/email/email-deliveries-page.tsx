"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { RefreshCw } from "lucide-react";

import { EmailWorkspaceNav } from "@/components/email/email-workspace-nav";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  listEmailDeliveries,
  type EmailDeliveryRow,
} from "@/services/email-notification-service";
import { ApiClientError } from "@/services/api-client";
import { cn } from "@/lib/utils";

function rowTime(row: EmailDeliveryRow): string | null {
  return row.occurred_at || row.delivered_at || row.created_at || null;
}

function formatWhen(iso: string | null): string {
  if (!iso) return "-";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function statusBadgeClass(status: string): string {
  const s = status.toLowerCase();
  if (s === "delivered" || s === "sent") {
    return "border-emerald-300 bg-emerald-50 text-emerald-800";
  }
  if (s === "failed") {
    return "border-red-300 bg-red-50 text-red-800";
  }
  if (s === "pending" || s === "queued" || s === "retrying") {
    return "border-amber-300 bg-amber-50 text-amber-900";
  }
  return "";
}

export function EmailDeliveriesPage() {
  const [rows, setRows] = useState<EmailDeliveryRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRows(await listEmailDeliveries(200));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to load deliveries");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const sorted = useMemo(() => {
    // Sent + failed first by time; pending included but still time-sorted.
    const list = [...rows].filter((r) => {
      const s = (r.status || "").toLowerCase();
      return s === "delivered" || s === "failed" || s === "pending" || s === "retrying";
    });
    list.sort((a, b) => {
      const ta = Date.parse(rowTime(a) || "") || 0;
      const tb = Date.parse(rowTime(b) || "") || 0;
      return tb - ta;
    });
    return list;
  }, [rows]);

  const counts = useMemo(() => {
    let delivered = 0;
    let failed = 0;
    for (const row of sorted) {
      const s = row.status.toLowerCase();
      if (s === "delivered") delivered += 1;
      else if (s === "failed") failed += 1;
    }
    return { delivered, failed, total: sorted.length };
  }, [sorted]);

  return (
    <div className="space-y-5">
      <EmailWorkspaceNav />
      <PageHeader
        title="Email deliveries"
        description="Sent and failed SMTP attempts, newest first."
        actions={
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="cursor-pointer"
            onClick={() => void load()}
            disabled={loading}
          >
            <RefreshCw className={`size-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        }
      />

      {error ? (
        <p className="rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      ) : null}

      <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
        <span className="rounded-md border border-border/70 bg-muted/40 px-2.5 py-1">
          Total {counts.total}
        </span>
        <span className="rounded-md border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-emerald-800">
          Sent {counts.delivered}
        </span>
        <span className="rounded-md border border-red-200 bg-red-50 px-2.5 py-1 text-red-800">
          Failed {counts.failed}
        </span>
      </div>

      <div className="overflow-x-auto rounded-xl border border-border/80 bg-card shadow-sm">
        <table className="w-full min-w-[960px] text-left text-sm">
          <thead className="border-b border-border/70 bg-muted/40 text-[11px] tracking-wide text-muted-foreground uppercase">
            <tr>
              <th className="px-3 py-2.5 font-medium">Time</th>
              <th className="px-3 py-2.5 font-medium">Status</th>
              <th className="px-3 py-2.5 font-medium">Recipient</th>
              <th className="px-3 py-2.5 font-medium">Subject</th>
              <th className="px-3 py-2.5 font-medium">Event</th>
              <th className="px-3 py-2.5 font-medium">Provider</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((row) => (
              <tr key={row.id} className="border-b border-border/50 align-top last:border-0">
                <td className="whitespace-nowrap px-3 py-2.5 font-mono text-xs text-muted-foreground">
                  {formatWhen(rowTime(row))}
                </td>
                <td className="px-3 py-2.5">
                  <Badge
                    variant="outline"
                    className={cn("capitalize", statusBadgeClass(row.status))}
                  >
                    {row.status === "delivered" ? "sent" : row.status}
                  </Badge>
                </td>
                <td className="px-3 py-2.5 font-mono text-xs">{row.recipient_address ?? "-"}</td>
                <td className="max-w-[240px] truncate px-3 py-2.5" title={row.subject ?? undefined}>
                  {row.subject ?? "-"}
                </td>
                <td className="px-3 py-2.5 text-muted-foreground">{row.event_type ?? "-"}</td>
                <td
                  className="max-w-[280px] truncate px-3 py-2.5 font-mono text-[11px] text-muted-foreground"
                  title={row.provider_response ?? undefined}
                >
                  {row.provider_response ?? "-"}
                </td>
              </tr>
            ))}
            {!loading && sorted.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-3 py-8 text-center text-muted-foreground">
                  No sent or failed email deliveries yet.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
