"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Send } from "lucide-react";

import { EmailWorkspaceNav } from "@/components/email/email-workspace-nav";
import { FinanceField, FinanceTextarea } from "@/components/finance/journals/finance-form-field";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { sendEmailCompose } from "@/services/email-notification-service";
import { ApiClientError } from "@/services/api-client";

export function EmailComposePage() {
  const router = useRouter();
  const [toAddress, setToAddress] = useState("");
  const [subject, setSubject] = useState("");
  const [bodyHtml, setBodyHtml] = useState("<p>Hello,</p><p></p><p>Regards,<br/>ERP Notifications</p>");
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSending(true);
    setMessage(null);
    setError(null);
    try {
      const result = await sendEmailCompose({
        to_address: toAddress.trim(),
        subject: subject.trim(),
        body_html: bodyHtml,
        event_type: "email.compose",
      });
      if (!result) {
        setError("Send failed - no response from server");
        return;
      }
      setMessage(`Email ${result.status} → ${result.recipient_address}`);
      router.push("/email/deliveries");
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Send failed");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="space-y-5">
      <EmailWorkspaceNav />
      <PageHeader
        title="Compose email"
        description="Send via SMTP through the Notification Engine."
      />

      {message ? (
        <p className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
          {message}
        </p>
      ) : null}
      {error ? (
        <p className="rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      ) : null}

      <form
        onSubmit={(e) => void onSubmit(e)}
        className="max-w-3xl space-y-4 rounded-xl border border-border/80 bg-card p-4 shadow-sm"
      >
        <FinanceField label="To" htmlFor="to">
          <Input
            id="to"
            type="email"
            required
            value={toAddress}
            onChange={(e) => setToAddress(e.target.value)}
            placeholder="recipient@company.com"
          />
        </FinanceField>
        <FinanceField label="Subject" htmlFor="subject">
          <Input
            id="subject"
            required
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="Subject line"
          />
        </FinanceField>
        <FinanceField label="Body (HTML)" htmlFor="body">
          <FinanceTextarea
            id="body"
            required
            rows={12}
            value={bodyHtml}
            onChange={(e) => setBodyHtml(e.target.value)}
            className="font-mono text-xs"
          />
        </FinanceField>
        <div className="flex flex-wrap gap-2">
          <Button type="submit" disabled={sending} className="cursor-pointer transition-opacity duration-200">
            <Send className="size-3.5" />
            {sending ? "Sending…" : "Send email"}
          </Button>
        </div>
      </form>
    </div>
  );
}
