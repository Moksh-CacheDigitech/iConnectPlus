/** OVF Rule #7 — finance cost from payment-term gap (matches margin_engine). */

export const FINANCE_COST_PCT_PER_15_DAYS = 0.5;

/**
 * Excel: IF(Customer_Terms>Vendor_Terms, 0.5%/15*(Customer_Terms-Vendor_Terms), 0)
 * Stored as percent points (e.g. 0.50), rounded to 2 d.p.
 */
export function computeFinanceCostPct(
  vendorPaymentDays: number,
  customerPaymentDays: number,
): number {
  const vendor = Math.max(0, Math.trunc(Number(vendorPaymentDays) || 0));
  const customer = Math.max(0, Math.trunc(Number(customerPaymentDays) || 0));
  if (customer <= vendor) return 0;
  return Number(((FINANCE_COST_PCT_PER_15_DAYS / 15) * (customer - vendor)).toFixed(2));
}
