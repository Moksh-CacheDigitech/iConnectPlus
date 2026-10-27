import { apiClient } from "@/services/api-client";

type SmtpDiagnostics = {
  configured: boolean;
  missing: string[];
  present: string[];
  from_email: string | null;
  env_files_found: string[];
  hint: string | null;
};

export type EmailProviderStatus = {
  provider: string;
  configured: boolean;
  from_email: string | null;
  delivery_mode: string;
  host?: string | null;
  port?: number | null;
  use_tls?: boolean;
  auth?: boolean;
  diagnostics?: SmtpDiagnostics;
};

export type EmailDeliveryRow = {
  id: string;
  event_id: string;
  channel: string;
  attempt_no: number;
  status: string;
  provider_response: string | null;
  delivered_at: string | null;
  /** Attempt time: delivered_at, or event.created_at when delivery has no stamp yet. */
  occurred_at?: string | null;
  event_type: string | null;
  recipient_address: string | null;
  event_status: string | null;
  created_at: string | null;
  subject: string | null;
};

export type EmailEventRow = {
  id: string;
  template_id: string;
  event_type: string;
  recipient_address: string | null;
  recipient_user_id: string | null;
  status: string;
  created_at: string | null;
  payload_json: Record<string, unknown> | null;
};


export type EmailOverview = {
  provider: EmailProviderStatus;
  counts: {
    email_templates: number;
    events: number;
    deliveries: number;
    delivered: number;
    failed: number;
    queued: number;
  };
  recent_deliveries: EmailDeliveryRow[];
  recent_events: EmailEventRow[];
};

export type EmailComposePayload = {
  to_address: string;
  subject: string;
  body_html: string;
  event_type?: string;
  payload_json?: Record<string, unknown> | null;
};

export async function loadEmailOverview() {
  const res = await apiClient<EmailOverview>("/notifications/email/overview", { method: "GET" });
  return res.data;
}

export async function loadEmailStatus() {
  const res = await apiClient<EmailProviderStatus>("/notifications/email/status", { method: "GET" });
  return res.data;
}

export async function testEmailConnection() {
  const res = await apiClient<{
    ok: boolean;
    message: string;
    status_code: number;
    from_email: string | null;
    provider_response?: string | null;
    diagnostics?: SmtpDiagnostics;
    details?: {
      step: string;
      hint: string | null;
      missing: string[];
      present: string[];
      env_files_found: string[];
    };
  }>("/notifications/email/test", { method: "POST" });
  return res.data;
}

export async function sendEmailCompose(body: EmailComposePayload) {
  const res = await apiClient<{ id: string; status: string; recipient_address: string; event_type: string }>(
    "/notifications/email/send",
    { method: "POST", body },
  );
  return res.data;
}

export async function listEmailDeliveries(limit = 100) {
  // API Query(ge=1, le=200) — clamp so the UI never trips a 422 validation error.
  const capped = Math.min(Math.max(1, limit), 200);
  const res = await apiClient<EmailDeliveryRow[]>("/notifications/deliveries", {
    method: "GET",
    query: { limit: capped },
  });
  return (res.data ?? []).filter((d) => d.channel === "email");
}

export async function listEmailEvents(limit = 100) {
  const capped = Math.min(Math.max(1, limit), 200);
  const res = await apiClient<EmailEventRow[]>("/notifications/events", {
    method: "GET",
    query: { limit: capped },
  });
  return res.data ?? [];
}
