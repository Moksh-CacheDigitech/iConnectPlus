"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  PROCUREMENT_APPROVALS_EVENT,
  readPoApprovals,
  setPoApprovalStatus,
  submitCreatePoInStockApproval,
  type PoApprovalRequest,
  type PoApprovalStatus,
} from "@/lib/procurement-approvals";
import { pushPoApprovalDecisionNotification } from "@/lib/procurement-approval-notifications";
import {
  finalizeScmOrder,
  listScmFinalizeApprovals,
  rejectScmFinalizeApproval,
  requestScmFinalizeApproval,
  type ScmFinalizeApproval,
} from "@/services/procurement-service";

function mapServerFinalize(row: ScmFinalizeApproval): PoApprovalRequest {
  return {
    id: row.id,
    kind: "finalize",
    orderId: row.order_id,
    documentNumber: row.document_number,
    companyPoNumber: row.company_po_number,
    customerName: row.customer_name,
    vendorId: String(row.vendor_id),
    vendorName: row.vendor_name,
    ovfId: row.ovf_id,
    ovfNo: row.ovf_no,
    reason: null,
    documents: [],
    requestedByRole: "user",
    status: row.status,
    createdAt: row.requested_at || new Date().toISOString(),
    decidedAt: row.decided_at,
  };
}

function mergeApprovalRows(
  serverFinalize: PoApprovalRequest[],
  localCreatePo: PoApprovalRequest[],
): PoApprovalRequest[] {
  const byId = new Map<string, PoApprovalRequest>();
  for (const row of [...serverFinalize, ...localCreatePo]) {
    byId.set(row.id, row);
  }
  return [...byId.values()].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
}

export function useProcurementApprovals() {
  const [rows, setRows] = useState<PoApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const [loadError, setLoadError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const localCreatePo = readPoApprovals().filter((row) => row.kind === "create_po_in_stock");
    try {
      const server = await listScmFinalizeApprovals();
      setLoadError(null);
      setRows(mergeApprovalRows(server.map(mapServerFinalize), localCreatePo));
    } catch (err) {
      // Keep IN STOCK Create-PO requests visible even if the shared inbox fails.
      setLoadError(err instanceof Error ? err.message : "Failed to load finalize approvals");
      setRows(mergeApprovalRows([], localCreatePo));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const onLocalChange = () => {
      void refresh();
    };
    window.addEventListener(PROCUREMENT_APPROVALS_EVENT, onLocalChange);
    window.addEventListener("storage", onLocalChange);
    return () => {
      window.removeEventListener(PROCUREMENT_APPROVALS_EVENT, onLocalChange);
      window.removeEventListener("storage", onLocalChange);
    };
  }, [refresh]);

  const pending = useMemo(
    () => rows.filter((row) => row.status === "pending"),
    [rows],
  );

  const submitFinalizeRequest = useCallback(
    async (orderId: string) => {
      const order = await requestScmFinalizeApproval(orderId);
      await refresh();
      return order;
    },
    [refresh],
  );

  const submitCreatePoInStockRequest = useCallback(
    (input: Parameters<typeof submitCreatePoInStockApproval>[0]) => {
      const row = submitCreatePoInStockApproval(input);
      void refresh();
      return row;
    },
    [refresh],
  );

  const decide = useCallback(
    async (row: PoApprovalRequest, status: Exclude<PoApprovalStatus, "pending">) => {
      if (row.kind === "finalize") {
        if (status === "accepted") {
          await finalizeScmOrder(row.orderId);
        } else {
          await rejectScmFinalizeApproval(row.orderId);
        }
      } else {
        setPoApprovalStatus(row.id, status);
      }
      pushPoApprovalDecisionNotification({
        approvalId: row.id,
        orderId: row.orderId,
        companyPoNumber: row.companyPoNumber,
        documentNumber: row.documentNumber,
        decision: status,
        kind: row.kind,
      });
      await refresh();
      return row;
    },
    [refresh],
  );

  return {
    rows,
    pending,
    pendingCount: pending.length,
    loading,
    loadError,
    submitFinalizeRequest,
    submitCreatePoInStockRequest,
    decide,
    refresh,
  };
}
