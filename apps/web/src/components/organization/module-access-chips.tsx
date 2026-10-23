"use client";

import { X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { moduleTitle } from "@/lib/module-access";
import { cn } from "@/lib/utils";

type Props = {
  moduleKeys: string[];
  variant: "admin" | "member";
  /** Collapse a full admin grant into one "All modules" chip. */
  allModules?: boolean;
  canEdit: boolean;
  busyKey?: string | null;
  onRemove?: (moduleKey: string | "*") => void;
};

/** One chip per module; ERP admins can remove access inline. */
export function ModuleAccessChips({
  moduleKeys,
  variant,
  allModules = false,
  canEdit,
  busyKey,
  onRemove,
}: Props) {
  const keys = allModules ? ["*"] : moduleKeys;
  if (keys.length === 0) {
    return <span className="text-xs text-muted-foreground">None</span>;
  }
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {keys.map((key) => {
        const label = key === "*" ? "All modules" : moduleTitle(key);
        const busy = busyKey === key;
        return (
          <Badge
            key={key}
            variant={variant === "admin" ? "outline" : "secondary"}
            className={cn("gap-1 pr-1 font-normal", busy && "opacity-60")}
          >
            {label}
            {canEdit && onRemove ? (
              <button
                type="button"
                disabled={busy}
                onClick={() => onRemove(key)}
                aria-label={`Remove ${variant === "admin" ? "admin" : "user"} access to ${label}`}
                className="inline-flex size-4 cursor-pointer items-center justify-center rounded-sm text-muted-foreground transition-colors duration-150 hover:bg-destructive/10 hover:text-destructive focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed"
              >
                <X className="size-3" />
              </button>
            ) : null}
          </Badge>
        );
      })}
    </div>
  );
}
