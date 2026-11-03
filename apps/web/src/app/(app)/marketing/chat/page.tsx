import { Suspense } from "react";

import { MarketingChat } from "@/components/marketing/marketing-chat";

export default function MarketingChatPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[40vh] items-center justify-center text-sm text-muted-foreground">
          Loading chat…
        </div>
      }
    >
      <MarketingChat />
    </Suspense>
  );
}
