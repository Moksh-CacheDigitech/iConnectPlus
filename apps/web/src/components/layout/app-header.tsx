import { env } from "@/utils/env";

interface AppHeaderProps {
  subtitle?: string;
}

export function AppHeader({ subtitle }: AppHeaderProps) {
  return (
    <header className="border-b bg-card">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
        <div>
          <p className="text-sm font-medium text-muted-foreground">Sprint 0 Foundation</p>
          <h1 className="text-xl font-semibold tracking-tight">{env.appName}</h1>
          {subtitle ? <p className="text-sm text-muted-foreground">{subtitle}</p> : null}
        </div>
      </div>
    </header>
  );
}
