"use client";

import { useEffect, useState } from "react";
import { CalendarClock, Mail, MailCheck, Send, TriangleAlert } from "lucide-react";

import { DeliveryCorrespondencePanel } from "@/components/procurement/delivery-correspondence-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import {
  dummySendScmDeliveryAcknowledgement,
  getScmDeliveryContact,
  runScmDeliveryNotifications,
  updateScmExpectedDeliveryDate,
  type ProcOrder,
} from "@/services/procurement-service";

function dateOnly(value: string | null | undefined): string {
  return value ? value.slice(0, 10) : "";
}

type Props = {
  order: ProcOrder;
  /** Admins can trigger the scheduled correspondence pass by hand. */
  isAdmin: boolean;
  /** True once any receipt/GRN qty has been recorded on this PO. */
  grnStarted?: boolean;
  /** When true, Record GRN stays locked until acknowledgement is sent. */
  lockGrnUntilAck?: boolean;
  onSaved: () => void;
};

/**
 * Expected delivery date and customer acknowledgement.
 * SMTP will replace the dummy send later; until then Send marks acknowledgement
 * and unlocks Record GRN (once, before the first GRN).
 */
export function DeliveryTrackingCard({
  order,
  isAdmin,
  grnStarted = false,
  lockGrnUntilAck = false,
  onSaved,
}: Props) {
  const [etd, setEtd] = useState(dateOnly(order.expected_delivery_date));
  const [notifyCustomer, setNotifyCustomer] = useState(true);
  const [email, setEmail] = useState("");
  const [crmEmail, setCrmEmail] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [correspondenceKey, setCorrespondenceKey] = useState(0);

  const ackSent = Boolean(order.customer_ack_sent_at);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const contact = await getScmDeliveryContact(order.id);
        if (cancelled) return;
        const fromCrm = (contact.crm_email || contact.email || "").trim();
        setCrmEmail(fromCrm || null);
        setEmail(fromCrm);
      } catch {
        if (!cancelled) {
          setCrmEmail(null);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [order.id]);

  async function saveEtd() {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const row = await updateScmExpectedDeliveryDate(order.id, {
        expected_delivery_date: etd || null,
        notify_customer: notifyCustomer,
      });
      setNotice(
        row.customer_notified
          ? "Delivery date saved and shared with the customer."
          : "Delivery date saved.",
      );
      setCorrespondenceKey((k) => k + 1);
      onSaved();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to save delivery date");
    } finally {
      setBusy(false);
    }
  }

  async function sendDummyAck() {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const row = await dummySendScmDeliveryAcknowledgement(order.id, {
        email: email.trim() || null,
      });
      setNotice(row.message);
      setCorrespondenceKey((k) => k + 1);
      onSaved();
    } catch (err) {
      setError(
        err instanceof ApiClientError
          ? err.message
          : "Failed to send acknowledgement",
      );
    } finally {
      setBusy(false);
    }
  }

  async function runNow() {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const counts = await runScmDeliveryNotifications();
      setNotice(
        `Sent ${counts.acknowledged} order acknowledgement(s), ${counts.etd_chased} ETD ` +
          `reminder(s), ${counts.delivery_dates_shared} delivery update(s).`,
      );
      setCorrespondenceKey((k) => k + 1);
      onSaved();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to run notifications");
    } finally {
      setBusy(false);
    }
  }

  const awaitingEtd = !order.expected_delivery_date;

  return (
    <section className="rounded-xl border border-border/70 bg-card p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-foreground">
            <CalendarClock className="size-4" aria-hidden />
          </span>
          <div>
            <h2 className="text-base font-extrabold tracking-tight">Delivery Tracking</h2>
            <p className="text-xs text-muted-foreground">
              {lockGrnUntilAck
                ? "Send acknowledgement once to unlock Record GRN. SMTP will be wired later — Send is a dummy for now."
                : ackSent || grnStarted
                  ? "Acknowledgement is only required once before the first GRN. Further receipts stay unlocked."
                  : "Expected delivery date and customer correspondence."}
            </p>
          </div>
        </div>
        {ackSent ? (
          <Badge className="rounded-full border-transparent bg-emerald-100 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200">
            Acknowledgement sent
          </Badge>
        ) : grnStarted ? (
          <Badge className="rounded-full border-transparent bg-emerald-100 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200">
            GRN started — ack not required again
          </Badge>
        ) : awaitingEtd ? (
          <Badge className="rounded-full border-transparent bg-amber-100 px-2.5 py-0.5 text-[11px] font-semibold text-amber-900 dark:bg-amber-900/50 dark:text-amber-100">
            Awaiting ETD from distributor
          </Badge>
        ) : (
          <Badge className="rounded-full border-transparent bg-emerald-100 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200">
            ETD confirmed
          </Badge>
        )}
      </div>

      {error ? (
        <p className="mt-3 flex items-center gap-1.5 text-xs font-medium text-red-600">
          <TriangleAlert className="size-3.5" /> {error}
        </p>
      ) : null}
      {notice ? (
        <p className="mt-3 flex items-center gap-1.5 text-xs font-medium text-emerald-700 dark:text-emerald-400">
          <MailCheck className="size-3.5" /> {notice}
        </p>
      ) : null}

      <dl className="mt-4 grid grid-cols-2 gap-3 text-xs lg:grid-cols-3">
        <div>
          <dt className="text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
            Customer Acknowledged
          </dt>
          <dd className="mt-0.5 font-semibold">{dateOnly(order.customer_ack_sent_at) || "-"}</dd>
        </div>
        <div>
          <dt className="text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
            Last ETD Reminder
          </dt>
          <dd className="mt-0.5 font-semibold">
            {dateOnly(order.etd_reminder_last_sent_at) || "-"}
          </dd>
        </div>
        <div>
          <dt className="text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
            ETD Confirmed On
          </dt>
          <dd className="mt-0.5 font-semibold">{dateOnly(order.etd_confirmed_at) || "-"}</dd>
        </div>
      </dl>

      <div className="mt-4 space-y-3 rounded-lg border border-border/60 bg-muted/20 p-3">
        <div className="flex flex-wrap items-end gap-3">
          <label className="min-w-[220px] flex-1 space-y-1.5">
            <span className="inline-flex items-center gap-1.5 text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
              <Mail className="size-3.5" aria-hidden />
              Customer email
            </span>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="customer@company.com"
              disabled={busy || ackSent}
              className="h-9 cursor-text text-[13px] transition-colors duration-200"
              aria-label="Customer email for acknowledgement"
            />
            <p className="text-[11px] text-muted-foreground">
              {crmEmail
                ? `CRM company email: ${crmEmail}. You can change it before sending.`
                : "No email on the CRM company — enter one to send."}
            </p>
          </label>
          <Button
            type="button"
            size="sm"
            disabled={busy || ackSent || !email.trim()}
            className="mb-1 cursor-pointer transition-colors duration-200"
            onClick={() => void sendDummyAck()}
          >
            <Send className="mr-1.5 size-3.5" />
            {ackSent ? "Sent" : "Send acknowledgement"}
          </Button>
        </div>
        {lockGrnUntilAck ? (
          <p className="text-[11px] text-amber-800">
            Record GRN stays locked until acknowledgement is sent once (dummy send for now).
          </p>
        ) : null}
      </div>

      <div className="mt-4 flex flex-wrap items-end gap-3">
        <label className="space-y-1.5">
          <span className="text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
            Expected delivery date
          </span>
          <Input
            type="date"
            value={etd}
            onChange={(e) => setEtd(e.target.value)}
            className="h-9 w-44 cursor-pointer text-[13px]"
          />
        </label>
        <label className="flex cursor-pointer items-center gap-2 pb-2 text-xs">
          <input
            type="checkbox"
            checked={notifyCustomer}
            onChange={(e) => setNotifyCustomer(e.target.checked)}
            className="size-3.5 cursor-pointer"
          />
          Email the customer this date
        </label>
        <Button
          type="button"
          size="sm"
          disabled={busy}
          className="mb-1 cursor-pointer transition-colors duration-200"
          onClick={() => void saveEtd()}
        >
          Save delivery date
        </Button>
        {isAdmin ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={busy}
            className="mb-1 cursor-pointer transition-colors duration-200"
            onClick={() => void runNow()}
          >
            <Send className="mr-1.5 size-3.5" />
            Run correspondence now
          </Button>
        ) : null}
      </div>

      <DeliveryCorrespondencePanel
        orderId={order.id}
        customerName={order.customer_name}
        refreshKey={correspondenceKey}
        canEditTemplates={isAdmin}
      />
    </section>
  );
}
