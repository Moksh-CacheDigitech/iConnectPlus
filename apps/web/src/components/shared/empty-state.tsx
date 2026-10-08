import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { Inbox, Search } from "lucide-react";

import { cn } from "@/lib/utils";

export type EmptyStatePreset = "no-records" | "no-results" | "no-queue";

const PRESETS: Record<EmptyStatePreset, { title: string; description: string; icon: LucideIcon }> = {
  "no-records": {
    title: "No records yet",
    description: "Records you create will appear here.",
    icon: Inbox,
  },
  "no-results": {
    title: "No results",
    description: "Try adjusting filters or search terms.",
    icon: Search,
  },
  "no-queue": {
    title: "Queue is empty",
    description: "Nothing to show in this queue right now.",
    icon: Inbox,
  },
};

export type EmptyStateProps = {
  preset?: EmptyStatePreset;
  icon?: LucideIcon;
  title?: string;
  /** Falls back to the preset copy when omitted; pass `null` to hide it. */
  description?: ReactNode;
  action?: ReactNode;
  compact?: boolean;
  /** Dashed panel border for standalone use (outside a table or card). */
  bordered?: boolean;
  className?: string;
};

export function EmptyState({
  preset = "no-results",
  icon,
  title,
  description,
  action,
  compact,
  bordered,
  className,
}: EmptyStateProps) {
  const fallback = PRESETS[preset];
  const Icon = icon ?? fallback.icon;
  const body = description === undefined ? fallback.description : description;
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center px-4 text-center",
        compact ? "py-6" : "py-12",
        bordered && "rounded-xl border border-dashed border-border/80 bg-muted/20",
        className,
      )}
      role="status"
    >
      <span
        className={cn(
          "mb-3 flex items-center justify-center rounded-full bg-muted text-muted-foreground",
          compact ? "size-8" : "size-10",
        )}
      >
        <Icon className={compact ? "size-4" : "size-5"} aria-hidden />
      </span>
      <p className={cn("font-medium text-foreground", compact ? "text-sm" : "text-[15px]")}>
        {title ?? fallback.title}
      </p>
      {body ? (
        <div className={cn("mt-1 max-w-sm text-muted-foreground", compact ? "text-xs" : "text-sm")}>
          {body}
        </div>
      ) : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
