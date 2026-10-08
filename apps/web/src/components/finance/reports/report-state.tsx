"use client";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorBanner } from "@/components/shared/error-banner";
import { TableSkeleton } from "@/components/shared/table-skeleton";

type Props = {
  error: string | null;
  onRetry: () => void;
  authenticated?: boolean;
};

export function ReportErrorState({ error, onRetry, authenticated = true }: Props) {
  if (!error) return null;
  return (
    <ErrorBanner onRetry={onRetry} signInHref={authenticated ? undefined : "/login"}>
      {error}
    </ErrorBanner>
  );
}

export function ReportTableSkeleton({ rows = 8 }: { rows?: number }) {
  return <TableSkeleton rows={rows} columns={5} />;
}

export function ReportEmptyState({ message = "No data for the selected filters." }: { message?: string }) {
  return <EmptyState bordered preset="no-results" title="No data" description={message} />;
}
