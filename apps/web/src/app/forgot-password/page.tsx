"use client";

import { Suspense, useState, type FormEvent } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowLeft, Mail } from "lucide-react";

import { AuthCardShell, AuthFormError, AuthFormNotice } from "@/components/auth/auth-card-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiClientError, authService } from "@/services/api-client";

function ForgotPasswordForm() {
  const searchParams = useSearchParams();
  const [userId, setUserId] = useState(searchParams.get("user") ?? "");
  const [submitting, setSubmitting] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting || !userId.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await authService.forgotPassword(userId.trim());
      setNotice(res.message || "If an account matches, a reset link has been sent.");
    } catch (err) {
      setError(
        err instanceof ApiClientError && err.status !== 0
          ? err.message || "Could not start password reset"
          : "Cannot reach the server. Try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthCardShell
      title="Forgot password"
      description="Enter your user id. We will email a reset link to the address on your account."
      footer={
        <Link
          href="/login"
          className="inline-flex cursor-pointer items-center gap-1.5 font-medium text-primary underline-offset-2 transition-colors duration-200 hover:underline focus-visible:rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <ArrowLeft className="size-3.5" />
          Back to sign in
        </Link>
      }
    >
      <form className="space-y-4" onSubmit={(e) => void onSubmit(e)} noValidate>
        <AuthFormError message={error} />
        <AuthFormNotice message={notice} />
        <div>
          <Label htmlFor="forgot-user-id" className="text-sm font-medium">
            Email ID or Employee Code
          </Label>
          <Input
            id="forgot-user-id"
            autoComplete="username"
            autoFocus
            required
            value={userId}
            disabled={submitting}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Email ID or Employee Code"
            className="h-11 transition-colors duration-200"
          />
        </div>
        <Button
          type="submit"
          className="h-10 w-full cursor-pointer gap-2 font-medium transition-colors duration-200"
          disabled={submitting || !userId.trim()}
        >
          <Mail className="size-4" />
          {submitting ? "Sending…" : "Send reset link"}
        </Button>
      </form>
    </AuthCardShell>
  );
}

export default function ForgotPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-dvh items-center justify-center text-sm text-muted-foreground">
          Loading…
        </div>
      }
    >
      <ForgotPasswordForm />
    </Suspense>
  );
}
