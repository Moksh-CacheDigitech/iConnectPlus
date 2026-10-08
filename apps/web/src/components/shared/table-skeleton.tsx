import { cn } from "@/lib/utils";

const BAR_WIDTHS = ["w-3/4", "w-1/2", "w-2/3", "w-2/5", "w-1/3"] as const;

function SkeletonBar({ index }: { index: number }) {
  return (
    <div
      className={cn(
        "h-3 animate-pulse rounded bg-muted motion-reduce:animate-none",
        BAR_WIDTHS[index % BAR_WIDTHS.length],
      )}
    />
  );
}

/** Placeholder `<tr>` rows for use inside an existing `<tbody>`. */
export function TableSkeletonRows({ rows = 8, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <>
      {Array.from({ length: rows }).map((_, r) => (
        <tr key={r} className="h-9 border-b border-border/50 last:border-0" aria-hidden>
          {Array.from({ length: columns }).map((__, c) => (
            <td key={c} className="px-3 py-2">
              <SkeletonBar index={r + c} />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

/** Standalone loading block shaped like a dense table (~36px rows). */
export function TableSkeleton({
  rows = 8,
  columns = 4,
  className,
}: {
  rows?: number;
  columns?: number;
  className?: string;
}) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn("overflow-hidden rounded-xl border border-border/70 bg-card shadow-sm", className)}
    >
      <div className="h-9 border-b border-border/80 bg-muted/60" />
      {Array.from({ length: rows }).map((_, r) => (
        <div
          key={r}
          className="grid h-9 items-center gap-4 border-b border-border/50 px-3 last:border-0"
          style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
        >
          {Array.from({ length: columns }).map((__, c) => (
            <SkeletonBar key={c} index={r + c} />
          ))}
        </div>
      ))}
    </div>
  );
}
