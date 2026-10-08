"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { AlertCircle, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type ErrorBannerProps = {
  /** Error message. */
  children?: ReactNode;
  title?: string;
  onRetry?: () => void;
  retryLabel?: string;
  /** Disables the retry button and spins its icon while a retry is in flight. */
  retrying?: boolean;
  /** Show a sign-in link (e.g. after a 401). */
  signInHref?: string;
  className?: string;
};

export function ErrorBanner({
  children,
  title,
  onRetry,
  retryLabel = "Retry",
  retrying = false,
  signInHref,
  className,
}: ErrorBannerProps) {
  const hasActions = Boolean(onRetry || signInHref);
  return (
    <div
      role="alert"
      className={cn(
        "flex flex-wrap items-start justify-between gap-3 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive",
        className,
      )}
    >
      <div className="flex min-w-0 flex-1 items-start gap-2">
        {title ? <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden /> : null}
        <div className="min-w-0 space-y-0.5">
          {title ? <p className="font-medium">{title}</p> : null}
          {children ? (
            <div className={cn("break-words", title && "text-foreground/80")}>{children}</div>
          ) : null}
        </div>
      </div>
      {hasActions ? (
        <div className="flex shrink-0 items-center gap-2">
          {signInHref ? (
            <Link
              href={signInHref}
              className="inline-flex h-8 cursor-pointer items-center rounded-lg bg-primary px-3 text-sm font-medium text-primary-foreground transition-opacity duration-200 hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
            >
              Sign in
            </Link>
          ) : null}
          {onRetry ? (
            <Button
              type="button"
              size="sm"
              variant="outline"
              className="h-8 cursor-pointer gap-1.5 bg-card"
              onClick={onRetry}
              disabled={retrying}
            >
              <RefreshCw
                className={cn("size-3.5", retrying && "animate-spin motion-reduce:animate-none")}
                aria-hidden
              />
              {retryLabel}
            </Button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
