import type { ReactNode } from "react";

import { AppFooter } from "@/components/layout/app-footer";
import { AppHeader } from "@/components/layout/app-header";

interface AppShellProps {
  children: ReactNode;
  subtitle?: string;
}

export function AppShell({ children, subtitle }: AppShellProps) {
  return (
    <div className="flex min-h-full flex-col bg-background">
      <AppHeader subtitle={subtitle} />
      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-6 py-8">
        {children}
      </main>
      <AppFooter />
    </div>
  );
}
