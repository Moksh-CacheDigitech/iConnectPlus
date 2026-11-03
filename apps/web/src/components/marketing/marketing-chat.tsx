"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  CircleDollarSign,
  Download,
  FileText,
  ImagePlus,
  Loader2,
  MessageSquare,
  Paperclip,
  Plus,
  SendHorizontal,
  Settings,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import {
  loadChatSettings,
  MarketingChatSettingsDialog,
  saveChatSettings,
  type MarketingChatSettings,
} from "@/components/marketing/marketing-chat-settings";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import {
  createMarketingChatSession,
  deleteMarketingChatSession,
  listMarketingChatMessages,
  listMarketingChatSessions,
  loadMarketingChatProviders,
  loadMarketingChatUsage,
  marketingChatAttachmentFilePath,
  sendMarketingChatMessage,
  uploadMarketingChatAttachment,
  type ChatSpendSummary,
  type MarketingChatAttachment,
  type MarketingChatMessage,
  type MarketingChatSession,
} from "@/services/marketing-service";
import { useSearchParams } from "next/navigation";

/** Fallback if usage API has not returned Frankfurter FX yet. */
const FALLBACK_USD_TO_INR = 95;

function formatUsd(value: number | null | undefined): string {
  const n = Number(value ?? 0);
  if (!Number.isFinite(n) || n <= 0) return "$0.00";
  if (n < 0.01) return `$${n.toFixed(4)}`;
  return `$${n.toFixed(2)}`;
}

function formatInrFromUsd(
  value: number | null | undefined,
  usdToInr: number = FALLBACK_USD_TO_INR,
): string {
  const usd = Number(value ?? 0);
  const rate = Number.isFinite(usdToInr) && usdToInr > 0 ? usdToInr : FALLBACK_USD_TO_INR;
  const n = Number.isFinite(usd) ? usd * rate : 0;
  if (!Number.isFinite(n) || n <= 0) return "₹0.00";
  if (n < 1) return `₹${n.toFixed(2)}`;
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(n);
}

type UiAttachment = MarketingChatAttachment & {
  previewUrl?: string;
};

type UiMessage = {
  id: string;
  role: "user" | "assistant" | "system" | string;
  content: string;
  createdAt: string;
  attachments: UiAttachment[];
};

type UiThread = {
  id: string;
  title: string;
  updatedAt: string;
  messages: UiMessage[];
  messagesLoaded: boolean;
};

type PendingFile = {
  localId: string;
  file?: File;
  label?: string;
  previewUrl?: string;
  uploading?: boolean;
  uploaded?: MarketingChatAttachment;
  error?: string;
};

const IMPORT_KEY = "erp.marketing.chat.import.v1";

const STARTERS = [
  "Draft a LinkedIn post for our AI governance webinar",
  "Suggest 5 Instagram carousel ideas for Cache Digitech",
  "Rewrite this CTA to sound more confident and concise",
  "Generate an image of a Diwali B2B campaign banner",
] as const;

const ACTIVE_KEY = "erp.marketing.chat.activeSession.v1";
const ACCEPT =
  "image/png,image/jpeg,image/webp,image/gif,application/pdf,text/plain,text/markdown,text/csv,application/json,.docx,.xlsx,.md,.txt,.csv,.pdf";

function sessionToThread(row: MarketingChatSession): UiThread {
  return {
    id: row.id,
    title: row.title || "New chat",
    updatedAt: row.last_message_at || row.updated_at || row.created_at || new Date().toISOString(),
    messages: [],
    messagesLoaded: false,
  };
}

function mapApiMessage(row: MarketingChatMessage): UiMessage {
  return {
    id: row.id,
    role: row.role,
    content: row.content,
    createdAt: row.created_at || new Date().toISOString(),
    attachments: Array.isArray(row.attachments) ? row.attachments : [],
  };
}

function errMessage(err: unknown): string {
  if (err instanceof Error && err.message) return err.message;
  return "Something went wrong talking to ChatGPT.";
}

function isImageAttachment(att: { kind?: string; content_type?: string }): boolean {
  return (
    att.kind === "image" ||
    att.kind === "generated_image" ||
    Boolean(att.content_type?.startsWith("image/"))
  );
}

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

export function MarketingChat() {
  const searchParams = useSearchParams();
  const [threads, setThreads] = useState<UiThread[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState<PendingFile[]>([]);
  const [sending, setSending] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settings, setSettings] = useState<MarketingChatSettings | null>(null);
  const [openaiReady, setOpenaiReady] = useState<boolean | null>(null);
  const [imageReady, setImageReady] = useState<boolean | null>(null);
  const [spend, setSpend] = useState<ChatSpendSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const composerRef = useRef<HTMLTextAreaElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const creatingRef = useRef(false);
  const importHandledRef = useRef(false);

  const upsertThread = useCallback((next: UiThread) => {
    setThreads((prev) => {
      const rest = prev.filter((t) => t.id !== next.id);
      return [next, ...rest].sort(
        (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
      );
    });
  }, []);

  const ensureSession = useCallback(
    async (preferredSettings?: MarketingChatSettings | null): Promise<UiThread> => {
      const existing = threads.find((t) => t.id === activeId);
      if (existing) return existing;
      if (creatingRef.current) {
        await new Promise((r) => window.setTimeout(r, 250));
        const again = threads.find((t) => t.id === activeId);
        if (again) return again;
      }
      creatingRef.current = true;
      try {
        const cfg = preferredSettings ?? settings ?? loadChatSettings();
        const row = await createMarketingChatSession({
          title: "New chat",
          settings: cfg,
        });
        const thread = sessionToThread(row);
        thread.messagesLoaded = true;
        upsertThread(thread);
        setActiveId(thread.id);
        try {
          window.localStorage.setItem(ACTIVE_KEY, thread.id);
        } catch {
          // ignore
        }
        return thread;
      } finally {
        creatingRef.current = false;
      }
    },
    [activeId, settings, threads, upsertThread],
  );

  useEffect(() => {
    // Lock the workspace main scroller so header + composer stay fixed; only panes scroll.
    const main = document.querySelector<HTMLElement>("#erp-workspace-main main");
    if (!main) return;
    const prevOverflow = main.style.overflowY;
    main.style.overflowY = "hidden";
    return () => {
      main.style.overflowY = prevOverflow;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setSettings(loadChatSettings());
      try {
        const [providers, sessions, usage] = await Promise.all([
          loadMarketingChatProviders(),
          listMarketingChatSessions(),
          loadMarketingChatUsage().catch(() => null),
        ]);
        if (cancelled) return;
        setOpenaiReady(providers.openai_configured);
        setImageReady(Boolean(providers.image_generation_configured));
        if (usage) setSpend(usage);
        const mapped = sessions.map(sessionToThread);
        setThreads(mapped);

        let importSession: string | null = searchParams.get("session");
        let importAttach: MarketingChatAttachment | null = null;
        let suggested: string | null = searchParams.get("prompt");
        if (!importHandledRef.current) {
          try {
            const raw = window.sessionStorage.getItem(IMPORT_KEY);
            if (raw) {
              window.sessionStorage.removeItem(IMPORT_KEY);
              const parsed = JSON.parse(raw) as {
                session?: MarketingChatSession;
                attachment?: MarketingChatAttachment;
                suggested_prompt?: string | null;
              };
              if (parsed.session?.id) {
                importSession = parsed.session.id;
                const thread = sessionToThread(parsed.session);
                thread.messagesLoaded = true;
                setThreads((prev) => {
                  const rest = prev.filter((t) => t.id !== thread.id);
                  return [thread, ...rest];
                });
              }
              if (parsed.attachment?.id) importAttach = parsed.attachment;
              if (parsed.suggested_prompt) suggested = parsed.suggested_prompt;
            }
          } catch {
            // ignore
          }
          importHandledRef.current = true;
        }

        let preferred: string | null = importSession;
        if (!preferred) {
          try {
            preferred = window.localStorage.getItem(ACTIVE_KEY);
          } catch {
            preferred = null;
          }
        }
        const pick = mapped.find((t) => t.id === preferred)?.id ?? preferred ?? mapped[0]?.id ?? null;
        setActiveId(pick);
        if (importAttach) {
          setPending([
            {
              localId: `import_${importAttach.id}`,
              label: importAttach.filename,
              previewUrl: isImageAttachment(importAttach)
                ? marketingChatAttachmentFilePath(importAttach.id)
                : undefined,
              uploaded: importAttach,
            },
          ]);
        }
        if (suggested?.trim()) setDraft(suggested.trim());
      } catch (err) {
        if (!cancelled) {
          setError(errMessage(err));
          setOpenaiReady(false);
          setThreads([]);
          setActiveId(null);
        }
      } finally {
        if (!cancelled) setHydrated(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [searchParams]);

  useEffect(() => {
    if (!activeId || !hydrated) return;
    try {
      window.localStorage.setItem(ACTIVE_KEY, activeId);
    } catch {
      // ignore
    }
    const thread = threads.find((t) => t.id === activeId);
    if (!thread || thread.messagesLoaded) return;

    let cancelled = false;
    setLoadingMessages(true);
    (async () => {
      try {
        const rows = await listMarketingChatMessages(activeId);
        if (cancelled) return;
        setThreads((prev) =>
          prev.map((t) =>
            t.id === activeId
              ? {
                  ...t,
                  messages: rows.map(mapApiMessage),
                  messagesLoaded: true,
                }
              : t,
          ),
        );
      } catch (err) {
        if (!cancelled) setError(errMessage(err));
      } finally {
        if (!cancelled) setLoadingMessages(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [activeId, hydrated, threads]);

  useEffect(() => {
    return () => {
      pending.forEach((p) => {
        if (p.previewUrl) URL.revokeObjectURL(p.previewUrl);
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- cleanup on unmount only
  }, []);

  const active = useMemo(
    () => threads.find((t) => t.id === activeId) ?? null,
    [threads, activeId],
  );

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [active?.messages.length, sending, loadingMessages, pending.length]);

  const startNewChat = useCallback(async () => {
    setError(null);
    setSending(false);
    setDraft("");
    setPending((prev) => {
      prev.forEach((p) => p.previewUrl && URL.revokeObjectURL(p.previewUrl));
      return [];
    });
    try {
      const cfg = settings ?? loadChatSettings();
      const row = await createMarketingChatSession({
        title: "New chat",
        settings: cfg,
      });
      const thread = sessionToThread(row);
      thread.messagesLoaded = true;
      upsertThread(thread);
      setActiveId(thread.id);
      window.requestAnimationFrame(() => composerRef.current?.focus());
    } catch (err) {
      setError(errMessage(err));
    }
  }, [settings, upsertThread]);

  const deleteThread = useCallback(
    async (id: string) => {
      setError(null);
      try {
        await deleteMarketingChatSession(id);
      } catch (err) {
        setError(errMessage(err));
        return;
      }
      setThreads((prev) => {
        const next = prev.filter((t) => t.id !== id);
        if (activeId === id) setActiveId(next[0]?.id ?? null);
        return next;
      });
    },
    [activeId],
  );

  const addFiles = useCallback((files: FileList | File[]) => {
    const list = Array.from(files);
    if (list.length === 0) return;
    setPending((prev) => {
      const room = Math.max(0, 5 - prev.length);
      const next = list.slice(0, room).map((file) => {
        const localId = `local_${Math.random().toString(36).slice(2)}_${Date.now()}`;
        const previewUrl = file.type.startsWith("image/")
          ? URL.createObjectURL(file)
          : undefined;
        return { localId, file, label: file.name, previewUrl } satisfies PendingFile;
      });
      return [...prev, ...next];
    });
  }, []);

  const removePending = useCallback((localId: string) => {
    setPending((prev) => {
      const target = prev.find((p) => p.localId === localId);
      if (target?.previewUrl) URL.revokeObjectURL(target.previewUrl);
      return prev.filter((p) => p.localId !== localId);
    });
  }, []);

  const sendMessage = useCallback(
    async (text: string, opts?: { generateImage?: boolean }) => {
      const content = text.trim();
      if ((!content && pending.length === 0) || sending) return;
      setError(null);
      setSending(true);

      try {
        let thread = active;
        if (!thread) {
          thread = await ensureSession(settings);
        }

        const attachmentIds: string[] = [];
        const uploadedLocal: UiAttachment[] = [];
        for (const item of pending) {
          if (item.uploaded?.id) {
            attachmentIds.push(item.uploaded.id);
            uploadedLocal.push({
              ...item.uploaded,
              previewUrl: item.previewUrl,
            });
            continue;
          }
          if (!item.file) continue;
          setPending((prev) =>
            prev.map((p) => (p.localId === item.localId ? { ...p, uploading: true } : p)),
          );
          const uploaded = await uploadMarketingChatAttachment(thread.id, item.file);
          attachmentIds.push(uploaded.id);
          uploadedLocal.push({
            ...uploaded,
            previewUrl: item.previewUrl,
          });
        }

        const optimisticUser: UiMessage = {
          id: `local_${Date.now()}`,
          role: "user",
          content: content || (uploadedLocal.length ? `Shared ${uploadedLocal.length} file(s)` : ""),
          createdAt: new Date().toISOString(),
          attachments: uploadedLocal,
        };
        const withUser: UiThread = {
          ...thread,
          title:
            thread.messages.length === 0
              ? (content || uploadedLocal[0]?.filename || "New chat").slice(0, 42)
              : thread.title,
          updatedAt: new Date().toISOString(),
          messages: [...thread.messages, optimisticUser],
          messagesLoaded: true,
        };
        upsertThread(withUser);
        setActiveId(withUser.id);
        setDraft("");
        setPending((prev) => {
          prev.forEach((p) => {
            // Keep object URLs alive on optimistic bubbles that reused them.
            if (!uploadedLocal.some((u) => u.previewUrl === p.previewUrl) && p.previewUrl) {
              URL.revokeObjectURL(p.previewUrl);
            }
          });
          return [];
        });

        const cfg = settings ?? loadChatSettings();
        const wantsImage =
          opts?.generateImage ||
          /\b(generate|create|make|draw|design)\b.*\b(image|picture|logo|banner|poster|visual)\b/i.test(
            content,
          ) ||
          /\b(image|picture|logo|banner)\b.*\b(generate|create|make|draw|design)\b/i.test(content);

        const result = await sendMarketingChatMessage(withUser.id, {
          content,
          settings: cfg,
          attachment_ids: attachmentIds,
          generate_image: wantsImage || undefined,
        });

        const next: UiThread = {
          id: result.session.id,
          title: result.session.title || withUser.title,
          updatedAt:
            result.session.last_message_at ||
            result.session.updated_at ||
            new Date().toISOString(),
          messagesLoaded: true,
          messages: [
            ...thread.messages,
            mapApiMessage(result.user_message),
            mapApiMessage(result.assistant_message),
          ],
        };
        upsertThread(next);
        setActiveId(next.id);
        void loadMarketingChatUsage()
          .then((usage) => setSpend(usage))
          .catch(() => undefined);
      } catch (err) {
        setError(errMessage(err));
      } finally {
        setSending(false);
        window.requestAnimationFrame(() => composerRef.current?.focus());
      }
    },
    [active, ensureSession, pending, sending, settings, upsertThread],
  );

  function onComposerKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void sendMessage(draft);
    }
  }

  const canSend = hydrated && !sending && (Boolean(draft.trim()) || pending.length > 0);
  const showEmpty =
    hydrated && (!active || active.messages.length === 0) && !loadingMessages && pending.length === 0;

  const settingsSummary = settings
    ? [
        settings.model,
        settings.ragEnabled ? "RAG on" : "RAG off",
        settings.brandKitEnabled ? "Brand kit on" : "Brand kit off",
      ].join(" · ")
    : null;

  const usdInr =
    typeof spend?.fx?.usd_inr === "number" && spend.fx.usd_inr > 0
      ? spend.fx.usd_inr
      : FALLBACK_USD_TO_INR;
  const fxLabel =
    spend?.fx?.source === "frankfurter" && spend.fx.as_of
      ? `Frankfurter · ${spend.fx.as_of}`
      : spend?.fx?.source === "fallback"
        ? "fallback rate"
        : "Frankfurter";

  return (
    <div className="flex h-[calc(100dvh-8.5rem)] max-h-[calc(100dvh-8.5rem)] flex-col gap-3 overflow-hidden lg:h-[calc(100dvh-7rem)] lg:max-h-[calc(100dvh-7rem)]">
      <div className="shrink-0 space-y-3">
        <PageHeader
          title="Chat"
          description="ChatGPT-backed assistant with files, images, and saved sessions."
          actions={
            <div className="flex flex-col items-end gap-1">
              <Button
                type="button"
                size="icon"
                variant="outline"
                className="size-9 cursor-pointer transition-colors duration-200"
                aria-label="Chatbot settings"
                title="Chatbot settings"
                onClick={() => setSettingsOpen(true)}
              >
                <Settings className="size-4" />
              </Button>
              {settingsSummary ? (
                <span className="max-w-[14rem] truncate text-[10px] text-muted-foreground">
                  {settingsSummary}
                </span>
              ) : null}
              {openaiReady === false ? (
                <span className="text-[10px] text-amber-700">OpenAI key missing on API</span>
              ) : null}
            </div>
          }
        />

        <nav
          aria-label="OpenAI chat spend"
          className="flex flex-wrap items-stretch gap-2 rounded-md border border-border/70 bg-card px-3 py-2"
        >
          <div className="flex min-w-[8.5rem] flex-col justify-center gap-0.5 pr-2 text-xs font-medium text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <CircleDollarSign className="size-3.5 text-primary" aria-hidden />
              Chat spend
            </span>
            <span className="pl-5 font-mono text-sm font-semibold tabular-nums text-foreground">
              ₹{usdInr.toFixed(2)} / $1
            </span>
            <span className="pl-5 text-[10px] font-normal text-muted-foreground/80">
              Today · {fxLabel}
            </span>
          </div>
          <div className="flex min-w-[8.5rem] flex-1 flex-col justify-center rounded border border-border/60 bg-muted/30 px-2.5 py-1.5 transition-colors duration-200 hover:bg-muted/50">
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground">Today</span>
            <span className="font-mono text-sm font-semibold tabular-nums text-foreground">
              {formatUsd(spend?.today.usd)}
            </span>
            <span className="font-mono text-[11px] tabular-nums text-muted-foreground">
              {formatInrFromUsd(spend?.today.usd, usdInr)}
            </span>
            <span className="text-[10px] text-muted-foreground">
              {spend?.today.message_count ?? 0} replies ·{" "}
              {(spend?.today.tokens ?? 0).toLocaleString()} tok
            </span>
          </div>
          <div className="flex min-w-[8.5rem] flex-1 flex-col justify-center rounded border border-border/60 bg-muted/30 px-2.5 py-1.5 transition-colors duration-200 hover:bg-muted/50">
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground">7 days</span>
            <span className="font-mono text-sm font-semibold tabular-nums text-foreground">
              {formatUsd(spend?.last_7_days.usd)}
            </span>
            <span className="font-mono text-[11px] tabular-nums text-muted-foreground">
              {formatInrFromUsd(spend?.last_7_days.usd, usdInr)}
            </span>
            <span className="text-[10px] text-muted-foreground">
              {spend?.last_7_days.message_count ?? 0} replies ·{" "}
              {(spend?.last_7_days.tokens ?? 0).toLocaleString()} tok
            </span>
          </div>
          <div className="flex min-w-[9.5rem] flex-1 flex-col justify-center rounded border border-border/60 bg-accent/40 px-2.5 py-1.5 transition-colors duration-200 hover:bg-accent/60">
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground">
              Last reply
            </span>
            <span className="font-mono text-sm font-semibold tabular-nums text-foreground">
              {formatUsd(spend?.last_reply.usd)}
            </span>
            <span className="font-mono text-[11px] tabular-nums text-muted-foreground">
              {formatInrFromUsd(spend?.last_reply.usd, usdInr)}
            </span>
            <span className="truncate text-[10px] text-muted-foreground">
              {(spend?.last_reply.tokens ?? 0).toLocaleString()} tok
              {spend?.last_reply.kind ? ` · ${spend.last_reply.kind}` : ""}
              {spend?.last_reply.model ? ` · ${spend.last_reply.model}` : ""}
            </span>
          </div>
        </nav>
      </div>

      {settings ? (
        <MarketingChatSettingsDialog
          open={settingsOpen}
          value={settings}
          onClose={() => setSettingsOpen(false)}
          onSave={(next) => {
            setSettings(next);
            saveChatSettings(next);
          }}
        />
      ) : null}

      {error ? (
        <div
          role="alert"
          className="shrink-0 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs text-destructive"
        >
          {error}
        </div>
      ) : null}

      <div className="grid min-h-0 flex-1 grid-rows-[minmax(0,11rem)_minmax(0,1fr)] overflow-hidden rounded-md border border-border/70 bg-card lg:grid-cols-[15rem_minmax(0,1fr)] lg:grid-rows-none">
        <aside className="flex min-h-0 flex-col overflow-hidden border-b border-border/70 lg:border-b-0 lg:border-r">
          <div className="flex shrink-0 items-center gap-2 border-b border-border/60 p-2.5">
            <Button
              type="button"
              size="sm"
              className="w-full cursor-pointer justify-start gap-2 transition-colors duration-200"
              onClick={() => void startNewChat()}
              disabled={!hydrated || sending}
            >
              <Plus className="size-3.5" aria-hidden />
              New chat
            </Button>
          </div>
          <div className="erp-scroll min-h-0 flex-1 overflow-y-auto overscroll-contain p-2">
            {!hydrated ? (
              <p className="px-2 py-3 text-xs text-muted-foreground">Loading sessions…</p>
            ) : threads.length === 0 ? (
              <p className="px-2 py-3 text-xs text-muted-foreground">
                No saved chats yet. Send a message or start a new chat.
              </p>
            ) : (
              <ul className="space-y-1" aria-label="Chat history">
                {threads.map((thread) => {
                  const selected = thread.id === activeId;
                  return (
                    <li key={thread.id} className="group relative">
                      <button
                        type="button"
                        onClick={() => setActiveId(thread.id)}
                        className={cn(
                          "flex w-full cursor-pointer items-start gap-2 rounded-md px-2.5 py-2 text-left text-xs transition-colors duration-200",
                          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                          selected
                            ? "bg-accent text-foreground"
                            : "text-muted-foreground hover:bg-muted/50 hover:text-foreground",
                        )}
                      >
                        <MessageSquare className="mt-0.5 size-3.5 shrink-0 opacity-70" aria-hidden />
                        <span className="min-w-0 flex-1">
                          <span className="line-clamp-2 font-medium leading-snug">
                            {thread.title}
                          </span>
                          <span className="mt-0.5 block text-[10px] tabular-nums opacity-70">
                            {new Date(thread.updatedAt).toLocaleString()}
                          </span>
                        </span>
                      </button>
                      <Button
                        type="button"
                        size="icon"
                        variant="ghost"
                        className="absolute right-1 top-1 size-7 cursor-pointer opacity-0 transition-opacity duration-200 group-hover:opacity-100 focus-visible:opacity-100"
                        aria-label={`Delete ${thread.title}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          void deleteThread(thread.id);
                        }}
                      >
                        <Trash2 className="size-3.5" />
                      </Button>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </aside>

        <section className="flex min-h-0 min-w-0 flex-col overflow-hidden" aria-label="Conversation">
          <div className="erp-scroll min-h-0 flex-1 overflow-y-auto overscroll-contain px-3 py-4 sm:px-5">
            {showEmpty ? (
              <div className="mx-auto flex max-w-2xl flex-col items-center justify-center gap-5 py-10 text-center sm:py-16">
                <div className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <Sparkles className="size-5" aria-hidden />
                </div>
                <div className="space-y-1.5">
                  <h2 className="text-base font-semibold tracking-tight">
                    How can I help with marketing today?
                  </h2>
                  <p className="text-xs text-muted-foreground">
                    Attach images or docs, ask for copy, or generate creatives. Enter to send,
                    Shift+Enter for a new line.
                  </p>
                </div>
                <div className="grid w-full gap-2 sm:grid-cols-2">
                  {STARTERS.map((starter) => (
                    <button
                      key={starter}
                      type="button"
                      onClick={() => void sendMessage(starter)}
                      className="cursor-pointer rounded-md border border-border/70 bg-background px-3 py-2.5 text-left text-xs leading-snug text-foreground transition-colors duration-200 hover:border-primary/40 hover:bg-accent/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      {starter}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="mx-auto flex max-w-3xl flex-col gap-4">
                {loadingMessages ? (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Loader2 className="size-3.5 animate-spin" aria-hidden />
                    Loading history…
                  </div>
                ) : null}
                {(active?.messages ?? []).map((msg) => (
                  <article
                    key={msg.id}
                    className={cn(
                      "flex gap-2.5",
                      msg.role === "user" ? "justify-end" : "justify-start",
                    )}
                  >
                    {msg.role === "assistant" ? (
                      <div
                        className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary"
                        aria-hidden
                      >
                        <Sparkles className="size-3.5" />
                      </div>
                    ) : null}
                    <div
                      className={cn(
                        "max-w-[min(100%,42rem)] space-y-2 rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed",
                        msg.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "border border-border/70 bg-muted/40 text-foreground",
                      )}
                    >
                      {msg.attachments.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {msg.attachments.map((att) => {
                            const href = marketingChatAttachmentFilePath(att.id);
                            if (isImageAttachment(att)) {
                              return (
                                <a
                                  key={att.id}
                                  href={href}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="block max-w-full cursor-pointer overflow-hidden rounded-lg border border-border/40 transition-opacity duration-200 hover:opacity-90"
                                >
                                  {/* eslint-disable-next-line @next/next/no-img-element */}
                                  <img
                                    src={att.previewUrl || href}
                                    alt={att.filename}
                                    className="max-h-64 max-w-full object-contain"
                                  />
                                </a>
                              );
                            }
                            return (
                              <a
                                key={att.id}
                                href={href}
                                target="_blank"
                                rel="noreferrer"
                                className={cn(
                                  "inline-flex max-w-full cursor-pointer items-center gap-2 rounded-md border px-2.5 py-1.5 text-xs transition-colors duration-200",
                                  msg.role === "user"
                                    ? "border-primary-foreground/30 bg-primary-foreground/10 hover:bg-primary-foreground/15"
                                    : "border-border/60 bg-background hover:bg-muted/60",
                                )}
                              >
                                <FileText className="size-3.5 shrink-0" aria-hidden />
                                <span className="min-w-0 truncate">{att.filename}</span>
                                <Download className="size-3 shrink-0 opacity-70" aria-hidden />
                              </a>
                            );
                          })}
                        </div>
                      ) : null}
                      {msg.content ? (
                        <div className="whitespace-pre-wrap">{msg.content}</div>
                      ) : null}
                    </div>
                  </article>
                ))}
                {sending ? (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Loader2 className="size-3.5 animate-spin" aria-hidden />
                    Thinking…
                  </div>
                ) : null}
                <div ref={bottomRef} />
              </div>
            )}
          </div>

          <div className="shrink-0 border-t border-border/70 bg-card p-3 sm:p-4">
            {pending.length > 0 ? (
              <div className="mx-auto mb-2 flex max-w-3xl flex-wrap gap-2">
                {pending.map((item) => (
                  <div
                    key={item.localId}
                    className="relative flex items-center gap-2 rounded-md border border-border/70 bg-muted/30 px-2 py-1.5 text-xs"
                  >
                    {item.previewUrl ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={item.previewUrl}
                        alt=""
                        className="size-10 rounded object-cover"
                      />
                    ) : (
                      <FileText className="size-4 text-muted-foreground" aria-hidden />
                    )}
                    <div className="min-w-0">
                      <p className="max-w-[10rem] truncate font-medium">
                        {item.label || item.file?.name || item.uploaded?.filename || "Attachment"}
                      </p>
                      <p className="text-[10px] text-muted-foreground">
                        {item.uploading
                          ? "Uploading…"
                          : item.uploaded
                            ? "Ready from Content Studio"
                            : item.file
                              ? formatBytes(item.file.size)
                              : "Ready"}
                      </p>
                    </div>
                    <button
                      type="button"
                      className="cursor-pointer rounded p-0.5 text-muted-foreground transition-colors duration-200 hover:bg-muted hover:text-foreground"
                      aria-label={`Remove ${item.label || item.file?.name || "attachment"}`}
                      onClick={() => removePending(item.localId)}
                      disabled={sending}
                    >
                      <X className="size-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            ) : null}

            <form
              className="mx-auto flex max-w-3xl items-end gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                void sendMessage(draft);
              }}
              onDragOver={(e) => {
                e.preventDefault();
              }}
              onDrop={(e) => {
                e.preventDefault();
                if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPT}
                multiple
                className="hidden"
                onChange={(e) => {
                  if (e.target.files?.length) addFiles(e.target.files);
                  e.target.value = "";
                }}
              />
              <Button
                type="button"
                size="icon"
                variant="outline"
                className="size-10 shrink-0 cursor-pointer rounded-xl transition-colors duration-200"
                aria-label="Attach files"
                title="Attach images or documents"
                disabled={sending || !hydrated || pending.length >= 5}
                onClick={() => fileInputRef.current?.click()}
              >
                <Paperclip className="size-4" />
              </Button>
              <Button
                type="button"
                size="icon"
                variant="outline"
                className="size-10 shrink-0 cursor-pointer rounded-xl transition-colors duration-200"
                aria-label="Generate image"
                title={
                  imageReady === false
                    ? "Image generation unavailable"
                    : "Ask ChatGPT to generate an image from your prompt"
                }
                disabled={sending || !hydrated || !draft.trim() || imageReady === false}
                onClick={() => void sendMessage(draft, { generateImage: true })}
              >
                <ImagePlus className="size-4" />
              </Button>
              <label htmlFor="mkt-chat-composer" className="sr-only">
                Message
              </label>
              <Textarea
                id="mkt-chat-composer"
                ref={composerRef}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={onComposerKeyDown}
                placeholder="Message Marketing Chat… (attach files or ask to generate an image)"
                rows={2}
                className="min-h-[2.75rem] max-h-40 flex-1 resize-none rounded-xl py-2.5"
                disabled={sending || !hydrated}
              />
              <Button
                type="submit"
                size="icon"
                className="size-10 shrink-0 cursor-pointer rounded-xl transition-colors duration-200"
                disabled={!canSend}
                aria-label="Send message"
              >
                {sending ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  <SendHorizontal className="size-4" />
                )}
              </Button>
            </form>
            <p className="mx-auto mt-2 max-w-3xl text-center text-[10px] text-muted-foreground">
              Images & docs in · generated images out · history saved to your account. Max 5 files
              per message.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
