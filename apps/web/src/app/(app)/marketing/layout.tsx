import type { ReactNode } from "react";

export default function MarketingLayout({ children }: { children: ReactNode }) {
  return <div className="min-w-0 max-w-full overflow-x-clip">{children}</div>;
}
