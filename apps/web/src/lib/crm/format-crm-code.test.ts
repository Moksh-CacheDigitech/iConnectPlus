import { describe, expect, it } from "vitest";

import { formatCrmCode } from "@/lib/crm/format-crm-code";

describe("formatCrmCode", () => {
  it("drops zero padding on the sequence", () => {
    expect(formatCrmCode("LEAD-2026-000014")).toBe("LEAD-2026-14");
  });

  it("keeps deal-scoped quote and OVF suffixes", () => {
    expect(formatCrmCode("DR-2026-0012/Q2")).toBe("DR-2026-12/Q2");
    expect(formatCrmCode("DR-2026-12/OVF1")).toBe("DR-2026-12/OVF1");
  });

  it("leaves other codes untouched", () => {
    expect(formatCrmCode("COMP-07")).toBe("COMP-07");
    expect(formatCrmCode(null)).toBe("");
  });
});
