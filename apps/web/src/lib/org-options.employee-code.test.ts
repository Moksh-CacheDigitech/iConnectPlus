import { describe, expect, it } from "vitest";

import {
  findEmployeeByCode,
  indexEmployeesByCode,
  normalizeEmployeeCodeKey,
  type EmployeeDirectoryEntry,
} from "@/lib/org-options";

function emp(
  partial: Partial<EmployeeDirectoryEntry> & Pick<EmployeeDirectoryEntry, "id" | "employeeCode">,
): EmployeeDirectoryEntry {
  return {
    displayName: partial.displayName ?? "Kapil Budhlakoti",
    label: partial.label ?? "Kapil Budhlakoti",
    mobile: partial.mobile ?? null,
    companyId: partial.companyId ?? "company-1",
    branchId: partial.branchId ?? "branch-1",
    ...partial,
  };
}

describe("employee code matching", () => {
  it("normalizes separators", () => {
    expect(normalizeEmployeeCodeKey("CT-5352")).toBe("ct5352");
    expect(normalizeEmployeeCodeKey("CT 5352")).toBe("ct5352");
    expect(normalizeEmployeeCodeKey("CT5352")).toBe("ct5352");
  });

  it("finds employee when Excel omits hyphens from stored code", () => {
    const byCode = indexEmployeesByCode([
      emp({ id: "e1", employeeCode: "CT-5352", displayName: "Kapil Budhlakoti" }),
    ]);
    expect(findEmployeeByCode(byCode, "CT5352")?.id).toBe("e1");
    expect(findEmployeeByCode(byCode, "ct-5352")?.id).toBe("e1");
    expect(findEmployeeByCode(byCode, "CT 5352")?.id).toBe("e1");
  });

  it("finds employee when stored code has no separators", () => {
    const byCode = indexEmployeesByCode([
      emp({ id: "e1", employeeCode: "CT5352" }),
    ]);
    expect(findEmployeeByCode(byCode, "CT-5352")?.id).toBe("e1");
    expect(findEmployeeByCode(byCode, "CT5352")?.id).toBe("e1");
  });
});
