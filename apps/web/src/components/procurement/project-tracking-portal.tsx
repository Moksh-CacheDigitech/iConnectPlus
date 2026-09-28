"use client";

import { useEffect, useMemo, useState } from "react";
import { MapPinned, TriangleAlert } from "lucide-react";

import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import { getPublicTracker, type PublicTracker, type PublicTrackerSite } from "@/services/service-projects-service";

function dateOrDash(value: string | null): string {
  if (!value) return "-";
  const d = new Date(`${value.slice(0, 10)}T00:00:00`);
  return Number.isNaN(d.getTime())
    ? value
    : d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

function SiteProgress({ site }: { site: PublicTrackerSite }) {
  return (
    <div className="flex items-center gap-1" aria-label={`Step ${site.milestone_step} of ${site.milestone_steps}`}>
      {Array.from({ length: site.milestone_steps }, (_, i) => (
        <span
          key={i}
          className={`h-1.5 w-4 rounded-full ${i < site.milestone_step ? "bg-emerald-600" : "bg-slate-200"}`}
        />
      ))}
    </div>
  );
}

/** Customer view of a multi-site rollout: milestones, dates and AWB per site. */
export function ProjectTrackingPortal({ token }: { token: string }) {
  const [data, setData] = useState<PublicTracker | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [circle, setCircle] = useState("");

  useEffect(() => {
    let cancelled = false;
    getPublicTracker(token)
      .then((row) => {
        if (!cancelled) setData(row);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof ApiClientError && err.status === 404
              ? "This tracking link is not valid any more. Please ask your account manager for a new one."
              : "Could not load the tracker. Please try again in a moment.",
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  const sites = useMemo(() => {
    const q = query.trim().toLowerCase();
    return (data?.sites ?? []).filter(
      (s) =>
        (!circle || (s.circle ?? "") === circle) &&
        (!q || `${s.site_code ?? ""} ${s.site_name} ${s.customer_po_number ?? ""}`.toLowerCase().includes(q)),
    );
  }, [data, query, circle]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 px-4 py-12 sm:px-6">
      <header className="space-y-2">
        <div className="flex items-center gap-2.5">
          <span className="flex size-9 items-center justify-center rounded-lg bg-slate-900 text-white">
            <MapPinned className="size-4.5" aria-hidden />
          </span>
          <h1 className="text-xl font-extrabold tracking-tight">{data?.name ?? "Delivery tracker"}</h1>
        </div>
        {data ? (
          <p className="text-sm text-slate-600">
            {data.customer_name ? `${data.customer_name} · ` : ""}
            {data.project_code}
          </p>
        ) : null}
      </header>

      {loading ? <div className="h-24 animate-pulse rounded-xl bg-slate-100 motion-reduce:animate-none" /> : null}
      {error ? (
        <p className="flex items-center gap-1.5 text-sm font-medium text-red-600">
          <TriangleAlert className="size-4" aria-hidden /> {error}
        </p>
      ) : null}

      {data ? (
        <>
          <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              ["Sites", data.site_count],
              ["Delivered", data.delivered_count + data.installed_count],
              ["Installed", data.installed_count],
              ["Running late", data.delayed_count],
            ].map(([label, value]) => (
              <div key={label} className="rounded-xl border border-slate-200 bg-white px-4 py-3">
                <dt className="text-[11px] font-medium tracking-wide text-slate-500 uppercase">{label}</dt>
                <dd className="mt-1 text-xl font-bold tabular-nums">{value}</dd>
              </div>
            ))}
          </dl>

          <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
            <div className="flex flex-wrap items-center gap-2.5 border-b border-slate-200 px-4 py-3">
              <Input
                aria-label="Search sites"
                placeholder="Search site or PO"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="h-9 w-56 text-sm"
              />
              {data.circles.length > 1 ? (
                <select
                  aria-label="Filter by circle"
                  className="h-9 cursor-pointer rounded-lg border border-slate-300 bg-white px-2.5 text-sm transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:outline-none"
                  value={circle}
                  onChange={(e) => setCircle(e.target.value)}
                >
                  <option value="">All circles</option>
                  {data.circles.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              ) : null}
              <span className="text-xs text-slate-500">{sites.length} sites</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="bg-slate-50 text-[11px] font-semibold tracking-wide text-slate-500 uppercase">
                  <tr>
                    <th className="px-4 py-2.5">Site</th>
                    <th className="px-4 py-2.5">PO</th>
                    <th className="px-4 py-2.5">Stage</th>
                    <th className="px-4 py-2.5">Expected</th>
                    <th className="px-4 py-2.5">Delivered</th>
                    <th className="px-4 py-2.5">AWB</th>
                  </tr>
                </thead>
                <tbody>
                  {sites.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                        No sites to show.
                      </td>
                    </tr>
                  ) : (
                    sites.map((s, i) => (
                      <tr key={`${s.site_code ?? ""}-${s.site_name}-${i}`} className="border-t border-slate-100 align-top">
                        <td className="px-4 py-2.5">
                          <span className="font-medium text-slate-900">{s.site_name}</span>
                          <span className="block text-[11px] text-slate-500">
                            {[s.circle, s.site_code].filter(Boolean).join(" · ") || "\u00a0"}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 font-mono text-xs">{s.customer_po_number ?? "-"}</td>
                        <td className="px-4 py-2.5">
                          <p className="text-sm font-semibold text-slate-800">
                            {s.status === "on_hold" ? "On hold" : s.milestone_label}
                          </p>
                          <SiteProgress site={s} />
                        </td>
                        <td className="px-4 py-2.5 text-xs tabular-nums">
                          <span className={s.delayed ? "inline-flex items-center gap-1 font-semibold text-red-600" : ""}>
                            {s.delayed ? <TriangleAlert className="size-3.5" aria-hidden /> : null}
                            {dateOrDash(s.expected_delivery_date)}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-xs tabular-nums">{dateOrDash(s.actual_delivery_date)}</td>
                        <td className="px-4 py-2.5 font-mono text-xs">{s.awb_number ?? "-"}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : null}
    </main>
  );
}
