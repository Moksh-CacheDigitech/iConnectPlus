import type { ReactNode } from "react";

import { AppLogo } from "@/components/brand/app-logo";
import { env } from "@/utils/env";

/** Centered card used by sign-in, forgot / reset / change password screens. */
export function AuthCardShell({
  title,
  description,
  children,
  footer,
}: {
  title?: string;
  description: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <div className="relative flex min-h-dvh items-center justify-center overflow-hidden px-4 py-12 sm:py-16">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_oklch(0.93_0.025_200)_0%,_oklch(0.985_0.004_220)_50%,_oklch(0.96_0.012_235)_100%)]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/25 to-transparent"
      />

      <div className="relative w-full max-w-[420px] animate-in fade-in-0 zoom-in-95 duration-300 motion-reduce:animate-none">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex justify-center">
            <AppLogo size={52} priority className="rounded-2xl shadow-sm ring-1 ring-border/60" />
          </div>
          <h1 className="font-heading text-2xl font-semibold tracking-tight text-foreground">
            {title ?? env.appName}
          </h1>
          <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-muted-foreground">
            {description}
          </p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card p-7 shadow-sm ring-1 ring-black/[0.02]">
          {children}
        </div>
        {footer ? (
          <div className="mt-5 text-center text-sm text-muted-foreground">{footer}</div>
        ) : null}
      </div>
    </div>
  );
}

export function AuthFormError({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <p
      role="alert"
      className="rounded-lg border border-destructive/25 bg-destructive/5 px-3 py-2.5 text-sm text-destructive"
    >
      {message}
    </p>
  );
}

export function AuthFormNotice({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <p
      role="status"
      className="rounded-lg border border-emerald-200/80 bg-emerald-50 px-3 py-2.5 text-sm text-emerald-800"
    >
      {message}
    </p>
  );
}
