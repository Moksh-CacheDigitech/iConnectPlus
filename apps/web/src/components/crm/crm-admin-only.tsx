"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";

import { useAuthUser } from "@/hooks/use-auth-user";
import { canManageModuleUsers } from "@/lib/module-access";

/** Gate CRM panes that only ERP / CRM module admins may open. */
export function CrmAdminOnly({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { user, adminModuleKeys, loading } = useAuthUser();
  const allowed = canManageModuleUsers("crm", adminModuleKeys, user?.userType);

  useEffect(() => {
    if (loading || allowed) return;
    router.replace("/crm");
  }, [allowed, loading, router]);

  if (loading || !allowed) {
    return (
      <div className="space-y-3 p-4">
        <div className="h-8 w-48 animate-pulse rounded bg-muted" />
        <div className="h-40 animate-pulse rounded-xl bg-muted/60" />
      </div>
    );
  }

  return <>{children}</>;
}
