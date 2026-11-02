"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";

import { useProcurementRole } from "@/hooks/use-procurement-role";

/** Gate procurement Insight panes for ERP / procurement module admins only. */
export function ProcurementAdminOnly({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { isAdmin, ready } = useProcurementRole();

  useEffect(() => {
    if (!ready || isAdmin) return;
    router.replace("/procurement");
  }, [isAdmin, ready, router]);

  if (!ready || !isAdmin) {
    return (
      <div className="space-y-3 p-4">
        <div className="h-8 w-48 animate-pulse rounded bg-muted" />
        <div className="h-40 animate-pulse rounded-xl bg-muted/60" />
      </div>
    );
  }

  return <>{children}</>;
}
