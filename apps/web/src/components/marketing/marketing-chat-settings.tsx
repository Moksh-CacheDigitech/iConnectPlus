"use client";

import { useEffect, useState } from "react";
import { BookOpen, BrainCircuit, Palette, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

export const CHAT_SETTINGS_KEY = "erp.marketing.chat.settings.v1";

export type MarketingChatSettings = {
  /** Model */
  provider: "openai" | "azure_openai" | "custom";
  model: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  /** RAG */
  ragEnabled: boolean;
  ragSource: "opensearch" | "documents" | "brand_docs" | "custom";
  ragTopK: number;
  ragMinScore: number;
  ragIndexHint: string;
  /** Brand kit */
  brandKitEnabled: boolean;
  brandKitIncludeVoice: boolean;
  brandKitIncludeColors: boolean;
  brandKitIncludeLogoRules: boolean;
  brandKitVoiceId: string;
};

export const DEFAULT_CHAT_SETTINGS: MarketingChatSettings = {
  provider: "openai",
  model: "gpt-4o-mini",
  temperature: 0.7,
  maxTokens: 2048,
  systemPrompt:
    "You are the iConnect Plus marketing assistant. Prefer brand-safe, B2B-ready copy. Ask clarifying questions when the brief is thin.",
  ragEnabled: false,
  ragSource: "documents",
  ragTopK: 6,
  ragMinScore: 0.25,
  ragIndexHint: "",
  brandKitEnabled: true,
  brandKitIncludeVoice: true,
  brandKitIncludeColors: true,
  brandKitIncludeLogoRules: true,
  brandKitVoiceId: "",
};

export function loadChatSettings(): MarketingChatSettings {
  if (typeof window === "undefined") return DEFAULT_CHAT_SETTINGS;
  try {
    const raw = window.localStorage.getItem(CHAT_SETTINGS_KEY);
    if (!raw) return DEFAULT_CHAT_SETTINGS;
    const parsed = JSON.parse(raw) as Partial<MarketingChatSettings>;
    return { ...DEFAULT_CHAT_SETTINGS, ...parsed };
  } catch {
    return DEFAULT_CHAT_SETTINGS;
  }
}

export function saveChatSettings(settings: MarketingChatSettings) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(CHAT_SETTINGS_KEY, JSON.stringify(settings));
  } catch {
    // ignore
  }
}

type MarketingChatSettingsDialogProps = {
  open: boolean;
  value: MarketingChatSettings;
  onClose: () => void;
  onSave: (next: MarketingChatSettings) => void;
};

function ToggleRow({
  id,
  label,
  description,
  checked,
  onChange,
}: {
  id: string;
  label: string;
  description: string;
  checked: boolean;
  onChange: (next: boolean) => void;
}) {
  return (
    <label
      htmlFor={id}
      className="flex cursor-pointer items-start gap-3 rounded-md border border-border/60 bg-background px-3 py-2.5 transition-colors duration-200 hover:bg-muted/30"
    >
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-0.5 size-4 cursor-pointer accent-primary"
      />
      <span className="min-w-0 flex-1">
        <span className="block text-sm font-medium text-foreground">{label}</span>
        <span className="mt-0.5 block text-xs text-muted-foreground">{description}</span>
      </span>
    </label>
  );
}

function SectionTitle({
  icon: Icon,
  title,
  subtitle,
}: {
  icon: typeof BrainCircuit;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="flex items-start gap-2.5">
      <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
        <Icon className="size-4" aria-hidden />
      </div>
      <div>
        <h3 className="text-sm font-semibold tracking-tight">{title}</h3>
        <p className="text-xs text-muted-foreground">{subtitle}</p>
      </div>
    </div>
  );
}

export function MarketingChatSettingsDialog({
  open,
  value,
  onClose,
  onSave,
}: MarketingChatSettingsDialogProps) {
  const [draft, setDraft] = useState<MarketingChatSettings>(value);

  useEffect(() => {
    if (open) setDraft(value);
  }, [open, value]);

  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  function patch<K extends keyof MarketingChatSettings>(key: K, next: MarketingChatSettings[K]) {
    setDraft((prev) => ({ ...prev, [key]: next }));
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-stretch justify-end bg-slate-900/40 backdrop-blur-[2px] motion-safe:animate-in motion-safe:fade-in-0 motion-safe:duration-200"
      role="presentation"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="mkt-chat-settings-title"
        className={cn(
          "flex h-full w-full max-w-lg flex-col border-l border-border bg-card shadow-xl",
          "motion-safe:animate-in motion-safe:slide-in-from-right-4 motion-safe:duration-200",
        )}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-start justify-between gap-3 border-b border-border/70 px-4 py-3.5">
          <div>
            <h2 id="mkt-chat-settings-title" className="text-base font-semibold tracking-tight">
              Chatbot configuration
            </h2>
            <p className="mt-0.5 text-xs text-muted-foreground">
              Model, RAG, and brand kit controls for Marketing Chat.
            </p>
          </div>
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="size-8 shrink-0 cursor-pointer"
            aria-label="Close settings"
            onClick={onClose}
          >
            <X className="size-4" />
          </Button>
        </header>

        <div className="erp-scroll min-h-0 flex-1 space-y-6 overflow-y-auto px-4 py-4">
          {/* Model */}
          <section className="space-y-3">
            <SectionTitle
              icon={BrainCircuit}
              title="Model configuration"
              subtitle="Provider, model id, sampling, and system prompt."
            />
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <Label htmlFor="mkt-chat-provider">Provider</Label>
                <select
                  id="mkt-chat-provider"
                  value={draft.provider}
                  onChange={(e) =>
                    patch("provider", e.target.value as MarketingChatSettings["provider"])
                  }
                  className="flex h-9 w-full cursor-pointer rounded-md border border-input bg-background px-3 text-sm transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="openai">OpenAI</option>
                  <option value="azure_openai">Azure OpenAI</option>
                  <option value="custom">Custom endpoint</option>
                </select>
              </div>
              <div>
                <Label htmlFor="mkt-chat-model">Model</Label>
                <Input
                  id="mkt-chat-model"
                  value={draft.model}
                  onChange={(e) => patch("model", e.target.value)}
                  placeholder="gpt-5.4"
                  className="transition-colors duration-200"
                />
              </div>
              <div>
                <Label htmlFor="mkt-chat-temp">Temperature ({draft.temperature.toFixed(1)})</Label>
                <input
                  id="mkt-chat-temp"
                  type="range"
                  min={0}
                  max={1.5}
                  step={0.1}
                  value={draft.temperature}
                  onChange={(e) => patch("temperature", Number(e.target.value))}
                  className="mt-2 w-full cursor-pointer accent-primary"
                />
              </div>
              <div>
                <Label htmlFor="mkt-chat-tokens">Max tokens</Label>
                <Input
                  id="mkt-chat-tokens"
                  type="number"
                  min={256}
                  max={128000}
                  value={draft.maxTokens}
                  onChange={(e) => patch("maxTokens", Number(e.target.value) || 2048)}
                  className="transition-colors duration-200"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="mkt-chat-system">System prompt</Label>
              <Textarea
                id="mkt-chat-system"
                rows={4}
                value={draft.systemPrompt}
                onChange={(e) => patch("systemPrompt", e.target.value)}
                className="resize-y transition-colors duration-200"
              />
            </div>
          </section>

          {/* RAG */}
          <section className="space-y-3">
            <SectionTitle
              icon={BookOpen}
              title="RAG integration"
              subtitle="Retrieve marketing docs / knowledge before answering."
            />
            <ToggleRow
              id="mkt-chat-rag"
              label="Enable RAG"
              description="Inject retrieved snippets into the model context for grounded answers."
              checked={draft.ragEnabled}
              onChange={(next) => patch("ragEnabled", next)}
            />
            <div
              className={cn(
                "grid gap-3 sm:grid-cols-2",
                !draft.ragEnabled && "pointer-events-none opacity-50",
              )}
            >
              <div>
                <Label htmlFor="mkt-chat-rag-source">Knowledge source</Label>
                <select
                  id="mkt-chat-rag-source"
                  value={draft.ragSource}
                  onChange={(e) =>
                    patch("ragSource", e.target.value as MarketingChatSettings["ragSource"])
                  }
                  disabled={!draft.ragEnabled}
                  className="flex h-9 w-full cursor-pointer rounded-md border border-input bg-background px-3 text-sm transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed"
                >
                  <option value="documents">Document Management</option>
                  <option value="opensearch">OpenSearch index</option>
                  <option value="brand_docs">Brand / marketing docs</option>
                  <option value="custom">Custom collection</option>
                </select>
              </div>
              <div>
                <Label htmlFor="mkt-chat-rag-index">Index / collection hint</Label>
                <Input
                  id="mkt-chat-rag-index"
                  value={draft.ragIndexHint}
                  onChange={(e) => patch("ragIndexHint", e.target.value)}
                  disabled={!draft.ragEnabled}
                  placeholder="e.g. marketing-knowledge"
                  className="transition-colors duration-200"
                />
              </div>
              <div>
                <Label htmlFor="mkt-chat-rag-topk">Top K</Label>
                <Input
                  id="mkt-chat-rag-topk"
                  type="number"
                  min={1}
                  max={20}
                  value={draft.ragTopK}
                  onChange={(e) => patch("ragTopK", Number(e.target.value) || 6)}
                  disabled={!draft.ragEnabled}
                  className="transition-colors duration-200"
                />
              </div>
              <div>
                <Label htmlFor="mkt-chat-rag-score">
                  Min score ({draft.ragMinScore.toFixed(2)})
                </Label>
                <input
                  id="mkt-chat-rag-score"
                  type="range"
                  min={0}
                  max={1}
                  step={0.05}
                  value={draft.ragMinScore}
                  disabled={!draft.ragEnabled}
                  onChange={(e) => patch("ragMinScore", Number(e.target.value))}
                  className="mt-2 w-full cursor-pointer accent-primary disabled:cursor-not-allowed"
                />
              </div>
            </div>
          </section>

          {/* Brand kit */}
          <section className="space-y-3">
            <SectionTitle
              icon={Palette}
              title="Brand kit integration"
              subtitle="Pull voice, colors, and logo rules into every reply."
            />
            <ToggleRow
              id="mkt-chat-brand"
              label="Use brand kit"
              description="Prefers active Marketing → Brand kit voice and visual rules."
              checked={draft.brandKitEnabled}
              onChange={(next) => patch("brandKitEnabled", next)}
            />
            <div
              className={cn(
                "space-y-2",
                !draft.brandKitEnabled && "pointer-events-none opacity-50",
              )}
            >
              <div>
                <Label htmlFor="mkt-chat-brand-voice">Brand voice id (optional)</Label>
                <Input
                  id="mkt-chat-brand-voice"
                  value={draft.brandKitVoiceId}
                  onChange={(e) => patch("brandKitVoiceId", e.target.value)}
                  disabled={!draft.brandKitEnabled}
                  placeholder="Leave blank to use company default"
                  className="transition-colors duration-200"
                />
              </div>
              <ToggleRow
                id="mkt-chat-brand-voice-toggle"
                label="Include brand voice"
                description="Tone, vocabulary, and messaging do’s/don’ts."
                checked={draft.brandKitIncludeVoice}
                onChange={(next) => patch("brandKitIncludeVoice", next)}
              />
              <ToggleRow
                id="mkt-chat-brand-colors"
                label="Include color palette"
                description="Primary / accent guidance for creative directions."
                checked={draft.brandKitIncludeColors}
                onChange={(next) => patch("brandKitIncludeColors", next)}
              />
              <ToggleRow
                id="mkt-chat-brand-logo"
                label="Include logo rules"
                description="Clear-space and placement constraints for image briefs."
                checked={draft.brandKitIncludeLogoRules}
                onChange={(next) => patch("brandKitIncludeLogoRules", next)}
              />
            </div>
          </section>
        </div>

        <footer className="flex flex-wrap items-center justify-end gap-2 border-t border-border/70 px-4 py-3">
          <Button
            type="button"
            variant="outline"
            className="cursor-pointer transition-colors duration-200"
            onClick={() => setDraft(DEFAULT_CHAT_SETTINGS)}
          >
            Reset defaults
          </Button>
          <Button
            type="button"
            variant="ghost"
            className="cursor-pointer transition-colors duration-200"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button
            type="button"
            className="cursor-pointer transition-colors duration-200"
            onClick={() => {
              onSave(draft);
              onClose();
            }}
          >
            Save configuration
          </Button>
        </footer>
      </div>
    </div>
  );
}
