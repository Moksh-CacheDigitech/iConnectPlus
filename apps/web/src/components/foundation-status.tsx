"use client";

import { Button } from "@/components/ui/button";
import { useHealthCheck } from "@/hooks/use-health-check";

export function FoundationStatus() {
  const { data, loading, error, refresh } = useHealthCheck();

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Platform Status</h2>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          Frontend foundation connected to the FastAPI backend via the shared API client.
          Business modules and authentication are out of scope for Sprint 0.
        </p>
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-sm">
        {loading ? <p className="text-sm text-muted-foreground">Checking API health…</p> : null}
        {error ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-destructive">API unreachable</p>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        ) : null}
        {data ? (
          <dl className="grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-muted-foreground">Application</dt>
              <dd className="font-medium">{data.status}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Environment</dt>
              <dd className="font-medium">{data.environment}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">API Version</dt>
              <dd className="font-medium">{data.version}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Database</dt>
              <dd className="font-medium">{data.database}</dd>
            </div>
          </dl>
        ) : null}
        <div className="mt-6">
          <Button variant="outline" onClick={() => void refresh()}>
            Refresh Status
          </Button>
        </div>
      </div>
    </section>
  );
}
