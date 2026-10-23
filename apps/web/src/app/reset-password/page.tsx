"use client";

import { Suspense, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { KeyRound } from "lucide-react";

import { AuthCardShell, AuthFormError, AuthFormNotice } from "@/components/auth/auth-card-shell";
import { NewPasswordFields, passwordMeetsPolicy } from "@/components/auth/new-password-fields";
import { Button } from "@/components/ui/button";
import { ApiClientError, authService } from "@/services/api-client";

function ResetPasswordForm() {
  const router = useRouter();
  const token = useSearchParams().get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(
    token ? null : "This reset link is missing its token. Request a new one.",
  );

  const valid = passwordMeetsPolicy(password) && password === confirm;

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting || !valid || !token) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await authService.resetPassword(token, password);
      setDone(res.message || "Password updated.");
      setTimeout(() => router.replace("/login"), 1500);
    } catch (err) {
      setError(
        err instanceof ApiClientError && err.status !== 0
          ? err.message || "Could not reset password"
          : "Cannot reach the server. Try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthCardShell
      title="Set a new password"
      description="Choose a new password for your iConnect Plus account."
      footer={
        <Link
          href="/forgot-password"
          className="cursor-pointer font-medium text-primary underline-offset-2 transition-colors duration-200 hover:underline focus-visible:rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          Request a new link
        </Link>
      }
    >
      <form className="space-y-4" onSubmit={(e) => void onSubmit(e)} noValidate>
        <AuthFormError message={error} />
        <AuthFormNotice message={done} />
        <NewPasswordFields
          password={password}
          confirm={confirm}
          onPasswordChange={setPassword}
          onConfirmChange={setConfirm}
          disabled={submitting || Boolean(done) || !token}
        />
        <Button
          type="submit"
          className="h-10 w-full cursor-pointer gap-2 font-medium transition-colors duration-200"
          disabled={submitting || !valid || !token || Boolean(done)}
        >
          <KeyRound className="size-4" />
          {submitting ? "Saving…" : "Update password"}
        </Button>
      </form>
    </AuthCardShell>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-dvh items-center justify-center text-sm text-muted-foreground">
          Loading…
        </div>
      }
    >
      <ResetPasswordForm />
    </Suspense>
  );
}
