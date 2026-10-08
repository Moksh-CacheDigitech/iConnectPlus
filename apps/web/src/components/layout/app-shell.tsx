"use client";

import type { ReactNode } from "react";
import { usePathname, useSearchParams } from "next/navigation";

import { ElevenLabsConvaiWidget } from "@/components/elevenlabs/convai-widget";
import { AppTopbar } from "@/components/layout/app-topbar";
import { ShellSidebar } from "@/components/layout/module-sidebar-registry";
import { isHrPath } from "@/config/hr-nav";
import { useStandaloneChrome } from "@/hooks/use-standalone-chrome";

interface AppShellProps {
  children: ReactNode;
}

/** Primary application chrome: left sidebar + topbar + content. */
export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const standalone = useStandaloneChrome();
  const hrMode = isHrPath(pathname);
  /** QR scan focus mode — full portal without the assets dock (better on phones). */
  const qrScanMode =
    searchParams.get("from") === "qr" && pathname.startsWith("/assets/information-portal/");
  return (
    <div className="flex min-h-dvh w-full max-w-[100dvw] overflow-x-clip bg-background">
      <ShellSidebar pathname={pathname} standalone={standalone} hideSidebar={qrScanMode} />
      <div id="erp-workspace-main" className="flex min-w-0 flex-1 flex-col overflow-x-clip">
        <AppTopbar />
        <main
          className={`min-w-0 flex-1 overflow-x-clip px-3 py-4 sm:px-6 sm:py-6 lg:px-8 ${qrScanMode ? "pb-[max(1.5rem,env(safe-area-inset-bottom))]" : ""
            }`}
        >
          <div className="mx-auto w-full min-w-0 max-w-[1400px] animate-in fade-in-50 slide-in-from-bottom-2 duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] motion-reduce:animate-none">
            {children}
          </div>
        </main>
        {hrMode ? (
          <footer className="border-t border-border/70 bg-card/40 px-4 py-3 text-[11px] text-muted-foreground sm:px-6">
            <div className="mx-auto flex max-w-[1400px] flex-wrap items-center justify-between gap-2">
              <span className="font-medium tracking-tight">HRMS workspace</span>
              <span>Workforce · Leave · Attendance · Talent · Hire · Pay</span>
            </div>
          </footer>
        ) : null}
      </div>
      <ElevenLabsConvaiWidget />
    </div>
  );
}
