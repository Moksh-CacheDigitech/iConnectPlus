import { AppShell } from "@/components/layout/app-shell";
import { FoundationStatus } from "@/components/foundation-status";

export default function HomePage() {
  return (
    <AppShell subtitle="Enterprise platform foundation — no business modules in Sprint 0">
      <FoundationStatus />
    </AppShell>
  );
}
