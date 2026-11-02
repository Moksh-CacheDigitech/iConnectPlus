"use client";

import { useCallback, useEffect, useState } from "react";
import { ClipboardList, Plus, X } from "lucide-react";

import { TaskAssignmentFormDialog } from "@/components/crm/sales/task-assignment-form-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ApiClientError } from "@/services/api-client";
import {
  listTasks,
  type Company,
  type CrmTask,
  type Opportunity,
} from "@/services/sales-crm-service";

function formatDue(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso.slice(0, 10);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function statusTone(status: string): string {
  switch (status) {
    case "completed":
      return "border-emerald-200 bg-emerald-50 text-emerald-800";
    case "in_progress":
      return "border-sky-200 bg-sky-50 text-sky-800";
    case "cancelled":
      return "border-border bg-muted text-muted-foreground";
    default:
      return "border-amber-200 bg-amber-50 text-amber-900";
  }
}

export function OpportunityTasksPanel({
  opportunityId,
  companyAccountId,
  opportunity,
  company,
  open,
  onClose,
  onChanged,
}: {
  opportunityId: string;
  companyAccountId?: string | null;
  opportunity?: Opportunity | null;
  company?: Company | null;
  open: boolean;
  onClose: () => void;
  onChanged?: () => void;
}) {
  const [rows, setRows] = useState<CrmTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listTasks({ opportunity_id: opportunityId });
      setRows(
        [...data].sort((a, b) => {
          const aDue = a.due_at ? new Date(a.due_at).getTime() : 0;
          const bDue = b.due_at ? new Date(b.due_at).getTime() : 0;
          return aDue - bDue;
        }),
      );
    } catch (err) {
      setRows([]);
      setError(err instanceof ApiClientError ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }, [opportunityId]);

  useEffect(() => {
    if (!open) return;
    void load();
  }, [open, load]);

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/20" aria-hidden onClick={onClose} />
      <aside
        className="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col border-l border-border/80 bg-card shadow-xl"
        role="dialog"
        aria-label="Task assignment"
      >
        <div className="flex items-start justify-between gap-3 border-b border-border/70 px-4 py-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <ClipboardList className="size-4 text-primary" aria-hidden />
              <h2 className="text-sm font-semibold text-foreground">Task assignment</h2>
            </div>
            <p className="mt-0.5 truncate text-xs text-muted-foreground">
              {opportunity?.opportunity_name || "Opportunity"} · {rows.length} task
              {rows.length === 1 ? "" : "s"}
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-1.5">
            <Button
              type="button"
              size="sm"
              className="h-8 cursor-pointer gap-1"
              onClick={() => setCreateOpen(true)}
            >
              <Plus className="size-3.5" aria-hidden />
              Assign
            </Button>
            <Button
              type="button"
              size="icon"
              variant="ghost"
              className="size-8 cursor-pointer"
              onClick={onClose}
              aria-label="Close"
            >
              <X className="size-4" />
            </Button>
          </div>
        </div>

        {error ? (
          <div className="mx-4 mt-3 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
            {error}
          </div>
        ) : null}

        <div className="erp-scroll min-h-0 flex-1 overflow-y-auto px-4 py-3">
          {loading ? (
            <p className="py-10 text-center text-sm text-muted-foreground">Loading tasks…</p>
          ) : rows.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-border/80 bg-muted/20 px-4 py-12 text-center">
              <ClipboardList className="size-8 text-muted-foreground/50" aria-hidden />
              <p className="text-sm font-medium text-foreground">No tasks assigned yet</p>
              <p className="text-xs text-muted-foreground">
                Assign a follow-up so it shows here for this opportunity.
              </p>
              <Button
                type="button"
                size="sm"
                variant="outline"
                className="mt-2 cursor-pointer gap-1"
                onClick={() => setCreateOpen(true)}
              >
                <Plus className="size-3.5" aria-hidden />
                Assign task
              </Button>
            </div>
          ) : (
            <ul className="space-y-2.5">
              {rows.map((task) => (
                <li
                  key={task.id}
                  className="rounded-xl border border-border/70 bg-background px-3 py-2.5 shadow-sm"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <p className="min-w-0 flex-1 text-sm font-medium text-foreground">{task.title}</p>
                    <Badge
                      variant="outline"
                      className={cn("capitalize", statusTone(task.status))}
                    >
                      {task.status.replaceAll("_", " ")}
                    </Badge>
                  </div>
                  <div className="mt-1.5 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-muted-foreground">
                    <span className="capitalize">Priority: {task.priority}</span>
                    <span>Due: {formatDue(task.due_at)}</span>
                    <span className="tabular-nums">{task.task_code}</span>
                  </div>
                  {task.description ? (
                    <p className="mt-1.5 line-clamp-2 text-xs text-muted-foreground">
                      {task.description}
                    </p>
                  ) : null}
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>

      <TaskAssignmentFormDialog
        open={createOpen}
        opportunityId={opportunityId}
        companyAccountId={companyAccountId}
        opportunity={opportunity ?? null}
        company={company}
        onClose={() => setCreateOpen(false)}
        onSaved={() => {
          setCreateOpen(false);
          void load();
          onChanged?.();
        }}
      />
    </>
  );
}
