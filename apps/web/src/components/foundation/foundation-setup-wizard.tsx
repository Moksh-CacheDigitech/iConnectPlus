"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Circle,
  CircleAlert,
  Loader2,
  SkipForward,
} from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { PlatformPillarsBanner } from "@/components/shared/platform-pillars-banner";
import { WorkspacePage } from "@/components/shared/workspace-ui";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import {
  FOUNDATION_SETUP_STEPS,
  FOUNDATION_SETUP_STORAGE_KEY,
  type FoundationSetupStep,
  type FoundationSetupStepId,
} from "@/config/foundation-setup";
import { listTotal } from "@/lib/resource-display";
import { cn } from "@/lib/utils";
import { ApiClientError, resourceService } from "@/services/api-client";

type CheckState = "idle" | "loading" | "ok" | "empty" | "error";

type CheckResult = {
  key: string;
  label: string;
  state: CheckState;
  detail?: string;
};

function readCompleted(): Set<FoundationSetupStepId> {
  if (typeof window === "undefined") return new Set();
  try {
    const raw = window.localStorage.getItem(FOUNDATION_SETUP_STORAGE_KEY);
    if (!raw) return new Set();
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return new Set();
    return new Set(parsed.filter((v): v is FoundationSetupStepId => typeof v === "string"));
  } catch {
    return new Set();
  }
}

function writeCompleted(ids: Set<FoundationSetupStepId>) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(FOUNDATION_SETUP_STORAGE_KEY, JSON.stringify([...ids]));
}

async function probeCheck(apiPath: string): Promise<CheckResult["state"]> {
  try {
    const res = await resourceService.list(apiPath, { page: 1, page_size: 1 });
    const total = listTotal(res.data);
    return total > 0 ? "ok" : "empty";
  } catch (err) {
    if (err instanceof ApiClientError && (err.status === 403 || err.status === 404)) {
      return "error";
    }
    return "error";
  }
}

function StepRail({
  steps,
  activeId,
  completed,
  onSelect,
}: {
  steps: readonly FoundationSetupStep[];
  activeId: FoundationSetupStepId;
  completed: Set<FoundationSetupStepId>;
  onSelect: (id: FoundationSetupStepId) => void;
}) {
  return (
    <nav aria-label="Foundation setup steps" className="overflow-x-auto overscroll-x-contain">
      <ol className="flex min-w-max items-stretch gap-1 sm:gap-1.5">
        {steps.map((step, index) => {
          const active = step.id === activeId;
          const done = completed.has(step.id);
          const Icon = step.icon;
          return (
            <li key={step.id} className="flex items-center gap-1 sm:gap-1.5">
              <button
                type="button"
                onClick={() => onSelect(step.id)}
                aria-current={active ? "step" : undefined}
                className={cn(
                  "flex cursor-pointer items-center gap-2 rounded-lg border px-2.5 py-2 text-left transition-colors duration-200 motion-reduce:transition-none",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  active && "border-primary/50 bg-primary/5 text-foreground",
                  !active && done && "border-emerald-200/80 bg-emerald-50/60 text-foreground",
                  !active && !done && "border-border/70 bg-card text-muted-foreground hover:bg-muted/50",
                )}
              >
                <span
                  className={cn(
                    "flex size-7 shrink-0 items-center justify-center rounded-md text-[11px] font-semibold tabular-nums",
                    active && "bg-primary text-primary-foreground",
                    !active && done && "bg-emerald-600 text-white",
                    !active && !done && "bg-muted text-muted-foreground",
                  )}
                >
                  {done && !active ? <CheckCircle2 className="size-3.5" aria-hidden /> : index + 1}
                </span>
                <span className="hidden min-w-0 sm:block">
                  <span className="block text-[11px] font-medium tracking-tight">{step.shortLabel}</span>
                  <span className="mt-0.5 flex items-center gap-1 text-[10px] text-muted-foreground">
                    <Icon className="size-3" aria-hidden />
                    Step {index + 1}
                  </span>
                </span>
              </button>
              {index < steps.length - 1 ? (
                <span className="hidden h-px w-3 bg-border sm:block" aria-hidden />
              ) : null}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

function CheckList({ results }: { results: CheckResult[] }) {
  if (results.length === 0) return null;
  return (
    <ul className="space-y-2">
      {results.map((row) => (
        <li
          key={row.key}
          className="flex items-start gap-2.5 rounded-lg border border-border/60 bg-muted/30 px-3 py-2 text-sm"
        >
          {row.state === "loading" ? (
            <Loader2 className="mt-0.5 size-4 shrink-0 animate-spin text-muted-foreground" aria-hidden />
          ) : null}
          {row.state === "ok" ? (
            <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-600" aria-hidden />
          ) : null}
          {row.state === "empty" ? (
            <Circle className="mt-0.5 size-4 shrink-0 text-amber-600" aria-hidden />
          ) : null}
          {row.state === "error" ? (
            <CircleAlert className="mt-0.5 size-4 shrink-0 text-destructive" aria-hidden />
          ) : null}
          {row.state === "idle" ? (
            <Circle className="mt-0.5 size-4 shrink-0 text-muted-foreground" aria-hidden />
          ) : null}
          <div className="min-w-0 flex-1">
            <p className="font-medium text-foreground">{row.label}</p>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {row.state === "ok" && "Ready"}
              {row.state === "empty" && "No records yet — open admin and create the first one"}
              {row.state === "error" && (row.detail ?? "Could not verify (permission or API)")}
              {row.state === "loading" && "Checking…"}
            </p>
          </div>
          <Badge
            variant="secondary"
            className={cn(
              "shrink-0 text-[10px] uppercase tracking-wide",
              row.state === "ok" && "border-emerald-200 bg-emerald-50 text-emerald-800",
              row.state === "empty" && "border-amber-200 bg-amber-50 text-amber-900",
              row.state === "error" && "border-destructive/30 bg-destructive/10 text-destructive",
            )}
          >
            {row.state === "ok" ? "Done" : row.state === "empty" ? "Needed" : row.state === "error" ? "Blocked" : "…"}
          </Badge>
        </li>
      ))}
    </ul>
  );
}

/** Guided Foundation setup — FRD-01 sequence ending in Organization handoff. */
export function FoundationSetupWizard() {
  const steps = FOUNDATION_SETUP_STEPS;
  const [activeId, setActiveId] = useState<FoundationSetupStepId>("access");
  const [completed, setCompleted] = useState<Set<FoundationSetupStepId>>(() => new Set());
  const [checks, setChecks] = useState<CheckResult[]>([]);
  const [probing, setProbing] = useState(false);

  const activeIndex = useMemo(
    () => steps.findIndex((s) => s.id === activeId),
    [activeId, steps],
  );
  const active = steps[activeIndex] ?? steps[0];
  const isFirst = activeIndex <= 0;
  const isLast = activeIndex >= steps.length - 1;
  const doneCount = completed.size;
  const progressPct = Math.round((doneCount / Math.max(steps.length - 1, 1)) * 100);

  useEffect(() => {
    setCompleted(readCompleted());
  }, []);

  const runProbes = useCallback(async (step: FoundationSetupStep) => {
    if (step.checks.length === 0) {
      setChecks([]);
      return;
    }
    setProbing(true);
    setChecks(
      step.checks.map((c) => ({
        key: c.key,
        label: c.label,
        state: "loading" as const,
      })),
    );
    const next: CheckResult[] = [];
    for (const check of step.checks) {
      if (!check.apiPath) {
        next.push({ key: check.key, label: check.label, state: "ok" });
        continue;
      }
      const state = await probeCheck(check.apiPath);
      next.push({
        key: check.key,
        label: check.label,
        state,
        detail: state === "error" ? "Check permissions or API availability" : undefined,
      });
    }
    setChecks(next);
    setProbing(false);
  }, []);

  useEffect(() => {
    void runProbes(active);
  }, [active, runProbes]);

  const markComplete = (id: FoundationSetupStepId) => {
    setCompleted((prev) => {
      const next = new Set(prev);
      next.add(id);
      writeCompleted(next);
      return next;
    });
  };

  const goNext = () => {
    markComplete(active.id);
    if (!isLast) setActiveId(steps[activeIndex + 1]!.id);
  };

  const goBack = () => {
    if (!isFirst) setActiveId(steps[activeIndex - 1]!.id);
  };

  const skipStep = () => {
    if (!isLast) setActiveId(steps[activeIndex + 1]!.id);
  };

  const Icon = active.icon;

  return (
    <WorkspacePage>
      <PageHeader
        title="Foundation setup"
        description="Who can do what + how approvals, notifications, and audit work — then continue to Organization."
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="secondary" className="tabular-nums">
              Step {activeIndex + 1} of {steps.length}
            </Badge>
            <Badge variant="outline" className="tabular-nums">
              {doneCount}/{Math.max(steps.length - 1, 1)} marked done
            </Badge>
          </div>
        }
      />

      <PlatformPillarsBanner active="foundation" />

      <div
        className="h-1.5 overflow-hidden rounded-full bg-muted"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={progressPct}
        aria-label="Foundation setup progress"
      >
        <div
          className="h-full rounded-full bg-primary transition-[width] duration-300 ease-out motion-reduce:transition-none"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      <StepRail
        steps={steps}
        activeId={active.id}
        completed={completed}
        onSelect={setActiveId}
      />

      <section
        aria-labelledby={`foundation-step-${active.id}-title`}
        className="rounded-xl border border-border/80 bg-card p-4 shadow-sm sm:p-5"
      >
        <div className="flex flex-wrap items-start gap-3">
          <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Icon className="size-5" aria-hidden />
          </span>
          <div className="min-w-0 flex-1 space-y-1">
            <h2
              id={`foundation-step-${active.id}-title`}
              className="text-base font-semibold tracking-tight text-foreground"
            >
              {active.title}
            </h2>
            <p className="max-w-3xl text-sm leading-relaxed text-muted-foreground">
              {active.description}
            </p>
          </div>
          {completed.has(active.id) ? (
            <Badge className="border-emerald-200 bg-emerald-50 text-emerald-800">Completed</Badge>
          ) : null}
        </div>

        {active.checks.length > 0 ? (
          <div className="mt-5 space-y-2">
            <div className="flex items-center justify-between gap-2">
              <p className="text-xs font-semibold tracking-wide text-foreground uppercase">
                Readiness checks
              </p>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 cursor-pointer text-xs"
                disabled={probing}
                onClick={() => void runProbes(active)}
              >
                {probing ? "Checking…" : "Re-check"}
              </Button>
            </div>
            <CheckList results={checks} />
          </div>
        ) : null}

        <div className="mt-5 flex flex-wrap gap-2">
          {active.actions.map((action) => (
            <Link
              key={action.href}
              href={action.href}
              className={cn(buttonVariants({ variant: "outline", size: "sm" }), "cursor-pointer")}
            >
              {action.label}
            </Link>
          ))}
        </div>
      </section>

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border/70 pt-3">
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="cursor-pointer gap-1.5"
          disabled={isFirst}
          onClick={goBack}
        >
          <ArrowLeft className="size-3.5" aria-hidden />
          Back
        </Button>
        <div className="flex flex-wrap items-center gap-2">
          {!isLast ? (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="cursor-pointer gap-1.5 text-muted-foreground"
              onClick={skipStep}
            >
              <SkipForward className="size-3.5" aria-hidden />
              Skip
            </Button>
          ) : null}
          {isLast ? (
            <Link
              href="/organization"
              className={cn(buttonVariants({ size: "sm" }), "cursor-pointer gap-1.5")}
              onClick={() => markComplete("handoff")}
            >
              Continue to Organization
              <ArrowRight className="size-3.5" aria-hidden />
            </Link>
          ) : (
            <Button type="button" size="sm" className="cursor-pointer gap-1.5" onClick={goNext}>
              Mark done & continue
              <ArrowRight className="size-3.5" aria-hidden />
            </Button>
          )}
        </div>
      </div>
    </WorkspacePage>
  );
}
