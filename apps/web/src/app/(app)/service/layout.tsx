"use client";

import type { ReactNode } from "react";
import { Suspense } from "react";

import { ServiceFieldEngineerLayoutGuard } from "@/components/service/service-field-engineer-layout-guard";

export default function ServiceLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense
      fallback={<div className="min-w-0 max-w-full overflow-x-clip">{children}</div>}
    >
      <ServiceFieldEngineerLayoutGuard>
        <div className="min-w-0 max-w-full overflow-x-clip">{children}</div>
      </ServiceFieldEngineerLayoutGuard>
    </Suspense>
  );
}
