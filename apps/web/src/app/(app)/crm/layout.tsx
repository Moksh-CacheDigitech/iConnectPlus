import type { ReactNode } from "react";

import { CrmApprovalInboxListener } from "@/components/crm/sales/crm-approval-inbox-listener";

export default function CrmLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid min-w-0 max-w-full grid-cols-1 gap-4 overflow-x-clip">
      <CrmApprovalInboxListener />
      <div className="min-w-0 max-w-full overflow-x-clip">{children}</div>
    </div>
  );
}
