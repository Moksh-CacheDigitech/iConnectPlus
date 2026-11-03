"use client";

import { Fragment, useCallback, useEffect, useState } from "react";
import { Check, Link2, Loader2, MessageSquareWarning, RefreshCw, Upload, X } from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { MarketingSignedInProfile } from "@/components/marketing/marketing-signed-in-profile";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthUser } from "@/hooks/use-auth-user";
import { getAccessToken } from "@/lib/auth";
import { canViewAllModuleScreens } from "@/lib/module-access";
import { formatApiError } from "@/services/api-client";
import {
  addDeliverableAnnotation,
  listContentReviewQueue,
  reviewContentRequest,
  type MarketingContentReviewItem,
} from "@/services/marketing-service";
import { getApiUrl } from "@/utils/env";

function canReviewRole(
  moduleRoles: Record<string, string>,
  adminModuleKeys: string[],
  userType?: string,
): boolean {
  if (canViewAllModuleScreens("marketing", adminModuleKeys, userType, moduleRoles)) return true;
  const role = moduleRoles.marketing;
  return (
    role === "approval_head" ||
    role === "marketing_head" ||
    role === "marketing_associate" ||
    role === "content_creator"
  );
}

function canActOnRow(
  row: MarketingContentReviewItem,
  userId: string | undefined,
  roleOk: boolean,
): boolean {
  if (roleOk) return true;
  if (!userId) return false;
  return Boolean(row.approval_head_user_ids?.includes(userId));
}

export function MarketingContentRequestsPage() {
  const { user, moduleRoles, adminModuleKeys, loading: authLoading } = useAuthUser();
  const reviewerRole = canReviewRole(moduleRoles, adminModuleKeys, user?.userType);

  const [rows, setRows] = useState<MarketingContentReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [commentById, setCommentById] = useState<Record<string, string>>({});
  const [actionError, setActionError] = useState<string | null>(null);
  const [annKindById, setAnnKindById] = useState<Record<string, string>>({});
  const [annBodyById, setAnnBodyById] = useState<Record<string, string>>({});
  const [annSecById, setAnnSecById] = useState<Record<string, string>>({});
  const [annXYById, setAnnXYById] = useState<Record<string, { x: string; y: string }>>({});

  async function openSubmittedContent(row: MarketingContentReviewItem) {
    const url = row.content_url?.trim() || "";
    if (/^https?:\/\//i.test(url)) {
      window.open(url, "_blank", "noopener,noreferrer");
      return;
    }
    const taskId = row.deliverable_task_id;
    if (taskId && (url.includes("/submission-file") || url.startsWith("/marketing/"))) {
      const token = getAccessToken();
      const res = await fetch(`${getApiUrl()}/marketing/tasks/${taskId}/submission-file`, {
        headers: {
          Accept: "*/*",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
      if (!res.ok) throw new Error("Could not download file");
      const blob = await res.blob();
      const objectUrl = URL.createObjectURL(blob);
      window.open(objectUrl, "_blank", "noopener,noreferrer");
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
      return;
    }
    throw new Error("No content attached yet");
  }

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRows(await listContentReviewQueue());
    } catch (err) {
      setRows([]);
      setError(formatApiError(err, "Failed to load content requests"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function onReview(
    id: string,
    action: "approve" | "reject" | "improve",
  ) {
    const comment = (commentById[id] || "").trim();
    if ((action === "reject" || action === "improve") && !comment) {
      setActionError("Add a comment for reject or improve.");
      return;
    }
    setBusyId(id);
    setActionError(null);
    try {
      await reviewContentRequest(id, { action, comment: comment || undefined });
      setCommentById((prev) => ({ ...prev, [id]: "" }));
      await load();
    } catch (err) {
      setActionError(formatApiError(err, "Review action failed"));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Content requests"
        description="Deliverable submissions awaiting approval. Approval heads can approve, reject, or request improvements with comments."
        actions={
          <div className="flex flex-wrap items-center justify-end gap-2">
            <MarketingSignedInProfile />
            <Button
              type="button"
              size="sm"
              variant="outline"
              className="h-9 cursor-pointer gap-1.5 transition-colors duration-200"
              disabled={loading}
              onClick={() => void load()}
            >
              <RefreshCw className={`size-3.5 ${loading ? "animate-spin" : ""}`} aria-hidden />
              Refresh
            </Button>
          </div>
        }
      />

      {error ? (
        <div className="rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      ) : null}
      {actionError ? (
        <p className="text-sm text-destructive" role="alert">
          {actionError}
        </p>
      ) : null}

      {!reviewerRole && !authLoading ? (
        <p className="text-[12px] text-muted-foreground">
          You can view submissions where you are maker or approval head. Approve / annotate when assigned.
        </p>
      ) : null}

      <section className="overflow-hidden rounded-xl border border-border/80 bg-card shadow-sm">
        <div className="erp-scroll overflow-x-auto">
          <table className="w-full min-w-[980px] text-left text-sm">
            <thead>
              <tr className="border-b border-border/80 bg-muted/40 text-[11px] font-semibold tracking-[0.08em] text-muted-foreground uppercase">
                <th className="px-4 py-2.5">Request</th>
                <th className="px-4 py-2.5">Content</th>
                <th className="px-4 py-2.5">Status</th>
                <th className="px-4 py-2.5">Due</th>
                <th className="px-4 py-2.5">Review</th>
              </tr>
            </thead>
            <tbody>
              {loading && rows.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center text-muted-foreground">
                    Loading requests…
                  </td>
                </tr>
              ) : rows.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center text-muted-foreground">
                    No deliverable submissions yet. Content providers submit from Tasks.
                  </td>
                </tr>
              ) : (
                rows.map((row) => {
                  const pending = row.content_status === "in_review";
                  const busy = busyId === row.id;
                  const canAct = canActOnRow(row, user?.id, reviewerRole);
                  const anns = row.review_annotations || [];
                  return (
                    <Fragment key={row.id}>
                      <tr className="border-b border-border/50 transition-colors duration-150 hover:bg-accent/30">
                        <td className="px-4 py-2.5">
                          <div className="font-medium text-foreground">{row.topic}</div>
                          <div className="mt-0.5 font-mono text-[11px] text-muted-foreground">
                            {row.request_code}
                          </div>
                          {row.improvement_comment ? (
                            <p className="mt-1 text-[12px] text-amber-700 dark:text-amber-400">
                              Last comment: {row.improvement_comment}
                            </p>
                          ) : null}
                          {anns.length > 0 ? (
                            <ul className="mt-2 space-y-1 text-[11px] text-muted-foreground">
                              {anns.slice(-5).map((a) => (
                                <li key={a.id}>
                                  <span className="font-medium text-foreground">{a.kind}</span>
                                  {a.at_seconds != null ? ` @ ${a.at_seconds}s` : ""}
                                  {a.x != null && a.y != null ? ` (${a.x}%, ${a.y}%)` : ""}
                                  {": "}
                                  {a.body}
                                </li>
                              ))}
                            </ul>
                          ) : null}
                        </td>
                        <td className="px-4 py-2.5 text-muted-foreground">
                          {row.content_url || row.document_name ? (
                            <button
                              type="button"
                              className="inline-flex cursor-pointer items-center gap-1 text-primary transition-colors duration-200 hover:underline"
                              onClick={() => {
                                void openSubmittedContent(row).catch((err) =>
                                  setError(formatApiError(err, "Could not open content")),
                                );
                              }}
                            >
                              {row.content_url?.includes("/submission-file") ? (
                                <Upload className="size-3.5" aria-hidden />
                              ) : (
                                <Link2 className="size-3.5" aria-hidden />
                              )}
                              {row.content_url?.includes("/submission-file")
                                ? row.document_name || "Download file"
                                : row.document_name || "Open link"}
                            </button>
                          ) : (
                            row.submission_notes || "-"
                          )}
                          {row.submission_notes && (row.content_url || row.document_name) ? (
                            <p className="mt-1 text-[12px]">{row.submission_notes}</p>
                          ) : null}
                        </td>
                        <td className="px-4 py-2.5">
                          <Badge variant="secondary" className="text-[10px] uppercase">
                            {row.content_status || row.status}
                          </Badge>
                          {row.self_checked ? (
                            <Badge variant="outline" className="ml-1 text-[10px]">
                              self-checked
                            </Badge>
                          ) : null}
                        </td>
                        <td className="px-4 py-2.5 tabular-nums text-muted-foreground">
                          {row.due_at ? String(row.due_at).slice(0, 10) : "-"}
                        </td>
                        <td className="px-4 py-2.5">
                          {pending && canAct ? (
                            <div className="space-y-2">
                              <Input
                                value={commentById[row.id] || ""}
                                onChange={(e) =>
                                  setCommentById((prev) => ({ ...prev, [row.id]: e.target.value }))
                                }
                                placeholder="Comment (required for reject / improve)"
                                className="h-9 max-w-sm"
                                disabled={busy}
                                aria-label="Review comment"
                              />
                              {row.deliverable_task_id ? (
                                <div className="space-y-1 rounded-md border border-border/60 bg-muted/20 p-2">
                                  <p className="text-[11px] font-medium text-foreground">
                                    Annotation (image mark / video timestamp)
                                  </p>
                                  <div className="flex flex-wrap gap-2">
                                    <select
                                      value={annKindById[row.id] || "text"}
                                      onChange={(e) =>
                                        setAnnKindById((p) => ({ ...p, [row.id]: e.target.value }))
                                      }
                                      className="h-8 cursor-pointer rounded-md border border-input bg-background px-2 text-[11px]"
                                    >
                                      <option value="text">Text note</option>
                                      <option value="image_mark">Image mark (x%, y%)</option>
                                      <option value="video_timestamp">Video timestamp</option>
                                    </select>
                                    {(annKindById[row.id] || "text") === "video_timestamp" ? (
                                      <Input
                                        value={annSecById[row.id] || ""}
                                        onChange={(e) =>
                                          setAnnSecById((p) => ({ ...p, [row.id]: e.target.value }))
                                        }
                                        placeholder="Seconds"
                                        className="h-8 w-24"
                                      />
                                    ) : null}
                                    {(annKindById[row.id] || "text") === "image_mark" ? (
                                      <>
                                        <Input
                                          value={annXYById[row.id]?.x || ""}
                                          onChange={(e) =>
                                            setAnnXYById((p) => ({
                                              ...p,
                                              [row.id]: {
                                                x: e.target.value,
                                                y: p[row.id]?.y || "",
                                              },
                                            }))
                                          }
                                          placeholder="X %"
                                          className="h-8 w-20"
                                        />
                                        <Input
                                          value={annXYById[row.id]?.y || ""}
                                          onChange={(e) =>
                                            setAnnXYById((p) => ({
                                              ...p,
                                              [row.id]: {
                                                x: p[row.id]?.x || "",
                                                y: e.target.value,
                                              },
                                            }))
                                          }
                                          placeholder="Y %"
                                          className="h-8 w-20"
                                        />
                                      </>
                                    ) : null}
                                  </div>
                                  <Input
                                    value={annBodyById[row.id] || ""}
                                    onChange={(e) =>
                                      setAnnBodyById((p) => ({ ...p, [row.id]: e.target.value }))
                                    }
                                    placeholder="What should change here…"
                                    className="h-8"
                                  />
                                  <Button
                                    type="button"
                                    size="sm"
                                    variant="outline"
                                    className="h-8 cursor-pointer transition-colors duration-200"
                                    disabled={busy}
                                    onClick={() => {
                                      void (async () => {
                                        const taskId = row.deliverable_task_id;
                                        if (!taskId) return;
                                        const kind = (annKindById[row.id] || "text") as
                                          | "text"
                                          | "image_mark"
                                          | "video_timestamp";
                                        const body = (annBodyById[row.id] || "").trim();
                                        if (!body) {
                                          setActionError("Annotation comment is required.");
                                          return;
                                        }
                                        setBusyId(row.id);
                                        setActionError(null);
                                        try {
                                          await addDeliverableAnnotation(taskId, {
                                            kind,
                                            body,
                                            at_seconds:
                                              kind === "video_timestamp"
                                                ? Number(annSecById[row.id] || 0)
                                                : undefined,
                                            x:
                                              kind === "image_mark"
                                                ? Number(annXYById[row.id]?.x || 0)
                                                : undefined,
                                            y:
                                              kind === "image_mark"
                                                ? Number(annXYById[row.id]?.y || 0)
                                                : undefined,
                                          });
                                          setAnnBodyById((p) => ({ ...p, [row.id]: "" }));
                                          await load();
                                        } catch (err) {
                                          setActionError(
                                            formatApiError(err, "Could not save annotation"),
                                          );
                                        } finally {
                                          setBusyId(null);
                                        }
                                      })();
                                    }}
                                  >
                                    Save annotation
                                  </Button>
                                </div>
                              ) : null}
                              <div className="flex flex-wrap gap-2">
                                <Button
                                  type="button"
                                  size="sm"
                                  className="h-8 cursor-pointer gap-1 transition-colors duration-200"
                                  disabled={busy}
                                  onClick={() => void onReview(row.id, "approve")}
                                >
                                  {busy ? (
                                    <Loader2 className="size-3.5 animate-spin" aria-hidden />
                                  ) : (
                                    <Check className="size-3.5" aria-hidden />
                                  )}
                                  Approve
                                </Button>
                                <Button
                                  type="button"
                                  size="sm"
                                  variant="outline"
                                  className="h-8 cursor-pointer gap-1 transition-colors duration-200"
                                  disabled={busy}
                                  onClick={() => void onReview(row.id, "improve")}
                                >
                                  <MessageSquareWarning className="size-3.5" aria-hidden />
                                  Improve
                                </Button>
                                <Button
                                  type="button"
                                  size="sm"
                                  variant="destructive"
                                  className="h-8 cursor-pointer gap-1 transition-colors duration-200"
                                  disabled={busy}
                                  onClick={() => void onReview(row.id, "reject")}
                                >
                                  <X className="size-3.5" aria-hidden />
                                  Reject
                                </Button>
                              </div>
                            </div>
                          ) : (
                            <span className="text-muted-foreground">
                              {pending ? "Awaiting approval head" : "Reviewed"}
                            </span>
                          )}
                        </td>
                      </tr>
                    </Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
