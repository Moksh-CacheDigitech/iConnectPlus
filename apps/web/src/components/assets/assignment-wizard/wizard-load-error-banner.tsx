"use client";

import { ErrorBanner } from "@/components/shared/error-banner";

export type WizardLoadErrorBannerProps = {
  message: string;
  onRetry?: () => void;
  retrying?: boolean;
};

export function WizardLoadErrorBanner({ message, onRetry, retrying }: WizardLoadErrorBannerProps) {
  return (
    <ErrorBanner onRetry={onRetry} retrying={retrying}>
      {message}
    </ErrorBanner>
  );
}
