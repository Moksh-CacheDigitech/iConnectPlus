"use client";

import Link from "next/link";

import {
  PLATFORM_PILLARS,
  type PlatformPillarKey,
} from "@/config/platform-pillars";
import { cn } from "@/lib/utils";

type PlatformPillarsBannerProps = {
  active: PlatformPillarKey;
  className?: string;
};

/** Reminds admins of the Foundation / Organization / Master Data split. */
export function PlatformPillarsBanner({ active, className }: PlatformPillarsBannerProps) {
  return (
    <section
      aria-label="Platform setup pillars"
      className={cn(
        "rounded-xl border border-border/80 bg-card p-3 shadow-sm sm:p-3.5",
        className,
      )}
    >
      <p className="mb-2.5 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">
        Platform sequence
      </p>
      <ol className="grid gap-2 sm:grid-cols-3">
        {PLATFORM_PILLARS.map((pillar, index) => {
          const isActive = pillar.key === active;
          return (
            <li key={pillar.key}>
              <Link
                href={pillar.href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "flex h-full cursor-pointer flex-col gap-1 rounded-lg border px-3 py-2.5 transition-colors duration-200 motion-reduce:transition-none",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  isActive
                    ? "border-primary/40 bg-primary/5 text-foreground"
                    : "border-border/70 bg-muted/20 text-muted-foreground hover:bg-muted/50 hover:text-foreground",
                )}
              >
                <span className="flex items-center gap-2 text-xs font-semibold tracking-tight text-foreground">
                  <span
                    className={cn(
                      "flex size-5 items-center justify-center rounded-md text-[10px] font-semibold tabular-nums",
                      isActive ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground",
                    )}
                  >
                    {index + 1}
                  </span>
                  {pillar.title}
                </span>
                <span className="text-[11px] leading-snug">{pillar.rule}</span>
              </Link>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
