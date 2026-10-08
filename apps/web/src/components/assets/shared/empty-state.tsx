import { Inbox, PackageOpen, Search } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { EmptyState as SharedEmptyState } from "@/components/shared/empty-state";

export type EmptyStateVariant = "no-assets" | "no-results" | "no-queue";

const COPY: Record<EmptyStateVariant, { title: string; description: string; icon: LucideIcon }> = {
  "no-assets": {
    title: "No assets yet",
    description: "Register your first asset to start tracking inventory.",
    icon: PackageOpen,
  },
  "no-results": {
    title: "No results",
    description: "Try adjusting filters or search terms.",
    icon: Search,
  },
  "no-queue": {
    title: "Queue is empty",
    description: "Nothing to show in this queue right now.",
    icon: Inbox,
  },
};

export type EmptyStateProps = {
  variant?: EmptyStateVariant;
  title?: string;
  description?: string;
  compact?: boolean;
  className?: string;
};

/** Asset-specific copy over the shared `EmptyState`. */
export function EmptyState({
  variant = "no-results",
  title,
  description,
  compact,
  className,
}: EmptyStateProps) {
  const preset = COPY[variant];
  return (
    <SharedEmptyState
      icon={preset.icon}
      title={title ?? preset.title}
      description={description ?? preset.description}
      compact={compact}
      className={className}
    />
  );
}
