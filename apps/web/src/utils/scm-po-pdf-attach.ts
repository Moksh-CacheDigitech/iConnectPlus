import {
  getPurchaseOrder,
  listVendorOptions,
  type VendorOption,
} from "@/services/procurement-service";
import { buildOrderPdfBase64 } from "@/utils/purchase-order-pdf";

function resolveVendor(
  vendors: VendorOption[],
  vendorId: string | null | undefined,
  fallbackName?: string | null,
): { name: string; address: string } {
  const option = vendorId
    ? vendors.find((v) => String(v.id) === String(vendorId))
    : undefined;
  return {
    name: option?.label || fallbackName?.trim() || "Vendor",
    address: option?.address || "",
  };
}

/** Build PO print PDF for Accept PO / Management approval emails. */
export async function buildScmPoPrintPdfAttachment(
  orderId: string,
): Promise<{ filename: string; base64: string } | null> {
  try {
    const [order, vendors] = await Promise.all([
      getPurchaseOrder(orderId),
      listVendorOptions().catch(() => [] as VendorOption[]),
    ]);
    const vendor = resolveVendor(vendors, order.vendor_id);
    const draft = (order.status || "").toLowerCase() === "draft";
    return await buildOrderPdfBase64(order, vendor, { watermark: draft });
  } catch {
    return null;
  }
}
