import { describe, expect, it } from "vitest";

import {
  filterShellHits,
  modulePaneCatalog,
  resolveShellSearchScope,
} from "@/lib/shell-search";

describe("shell-search", () => {
  it("routes CRM and Projects to dedicated search modes", () => {
    expect(resolveShellSearchScope("/crm/leads")).toEqual({ mode: "crm" });
    expect(resolveShellSearchScope("/projects/my-jobs")).toEqual({ mode: "projects" });
  });

  it("exposes finance panes for module search", () => {
    const scope = resolveShellSearchScope("/finance/journals");
    expect(scope.mode).toBe("panes");
    if (scope.mode !== "panes") return;
    expect(scope.placeholder).toBe("Search Finance…");
    expect(scope.panes.some((p) => p.href === "/finance/journals")).toBe(true);
  });

  it("falls back to home module search outside workspaces", () => {
    expect(resolveShellSearchScope("/home")).toEqual({
      mode: "home",
      placeholder: "Search modules…",
    });
  });

  it("filters pane hits by title", () => {
    const catalog = modulePaneCatalog("/marketing");
    expect(catalog).not.toBeNull();
    const hits = filterShellHits(catalog!.panes, "camp");
    expect(hits.some((h) => h.title === "Campaigns")).toBe(true);
  });
});
