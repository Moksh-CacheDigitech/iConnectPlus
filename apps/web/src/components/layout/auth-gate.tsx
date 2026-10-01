"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { WelcomeSplash } from "@/components/auth/welcome-splash";
import { AuthSessionProvider } from "@/hooks/use-auth-user";
import { clearTokens, getAccessToken, isAuthenticated } from "@/lib/auth";
import {
  clearWelcomeSplash,
  peekWelcomeSplash,
  type WelcomeSplashPayload,
} from "@/lib/welcome-splash-session";
import { apiClient } from "@/services/api-client";

function AuthGatePlaceholder({ message }: { message: string }) {
  return (
    <div className="flex min-h-dvh w-full items-center justify-center text-sm text-muted-foreground">
      {message}
    </div>
  );
}

function safeNextPath(pathname: string | null, search: string): string | null {
  if (!pathname || pathname === "/") return null;
  const full = search ? `${pathname}?${search}` : pathname;
  if (!full.startsWith("/") || full.startsWith("//")) return null;
  return full;
}

/** Redirect unauthenticated visitors to login, then load a shared auth session. */
export function AuthGate({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [mounted, setMounted] = useState(false);
  const [checking, setChecking] = useState(true);
  const [authed, setAuthed] = useState(false);
  const [welcome, setWelcome] = useState<WelcomeSplashPayload | null>(null);

  useEffect(() => {
    let cancelled = false;
    setMounted(true);
    setWelcome(peekWelcomeSplash());

    async function resolveSession() {
      if (isAuthenticated() && getAccessToken()) {
        if (!cancelled) {
          setAuthed(true);
          setChecking(false);
        }
        return;
      }
      // HttpOnly cookie session survives reload — probe /auth/me with credentials.
      try {
        await apiClient("/auth/me", { auth: true });
        if (!cancelled) {
          setAuthed(true);
          setChecking(false);
        }
        return;
      } catch {
        // fall through to unauthenticated
      }
      if (!cancelled) {
        clearTokens();
        setAuthed(false);
        setChecking(false);
      }
    }

    void resolveSession();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!mounted || checking || authed) return;
    const nextPath = safeNextPath(pathname, searchParams.toString());
    const next = nextPath ? `?next=${encodeURIComponent(nextPath)}` : "";
    router.replace(`/login${next}`);
  }, [pathname, searchParams, router, mounted, checking, authed]);

  // If tokens are cleared mid-session (401), send user back to login.
  useEffect(() => {
    if (!mounted || !authed) return;
    function onFocus() {
      if (!getAccessToken()) {
        void apiClient("/auth/me", { auth: true })
          .then(() => undefined)
          .catch(() => {
            clearTokens();
            setAuthed(false);
          });
      }
    }
    window.addEventListener("focus", onFocus);
    return () => {
      window.removeEventListener("focus", onFocus);
    };
  }, [mounted, authed]);

  const finishWelcome = useCallback(() => {
    clearWelcomeSplash();
    setWelcome(null);
  }, []);

  if (!mounted || checking) {
    return <AuthGatePlaceholder message="Loading…" />;
  }

  if (!authed) {
    return <AuthGatePlaceholder message="Redirecting to sign-in…" />;
  }

  return (
    <AuthSessionProvider>
      {welcome ? (
        <WelcomeSplash userName={welcome.userName} onComplete={finishWelcome} />
      ) : null}
      {children}
    </AuthSessionProvider>
  );
}
