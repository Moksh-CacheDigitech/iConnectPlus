/** @vitest-environment jsdom */

import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { FileText, LayoutDashboard, Wallet } from "lucide-react";

import { ModuleSidebar, type ModuleNavGroup } from "@/components/layout/module-sidebar";

const GROUPS: ModuleNavGroup[] = [
  {
    label: "Workspace",
    items: [
      { title: "Overview", href: "/finance", icon: LayoutDashboard },
      {
        title: "Reports",
        href: "/finance/reports",
        icon: FileText,
        children: [{ title: "Trial Balance", href: "/finance/reports/trial-balance" }],
      },
      { title: "Approvals", href: "/finance/approvals", icon: FileText, badge: 4 },
    ],
  },
];

function renderSidebar(activeHref: string, onNavigate = vi.fn()) {
  render(
    <ModuleSidebar
      moduleKey="finance"
      title="Finance"
      subtitle="Ledger"
      icon={Wallet}
      groups={GROUPS}
      isActive={(item) => item.href === activeHref}
      searchPlaceholder="Search Finance…"
      showAccount={false}
      onItemNavigate={onNavigate}
      testId="finance-sidebar"
    />,
  );
  return { onNavigate };
}

afterEach(() => {
  cleanup();
});

describe("ModuleSidebar", () => {
  it("renders a left-docked rail and marks the active item", () => {
    renderSidebar("/finance");
    const rail = screen.getByTestId("finance-sidebar");
    expect(rail.tagName).toBe("ASIDE");
    expect(rail.className).toMatch(/left-0/);
    expect(rail.className).toMatch(/w-\[260px\]/);
    const nav = screen.getByTestId("finance-sidebar-nav");
    expect(within(nav).getByRole("link", { name: "Overview" })).toHaveAttribute("aria-current", "page");
  });

  it("auto-expands a parent when its child is active", () => {
    renderSidebar("/finance/reports/trial-balance");
    const nav = screen.getByTestId("finance-sidebar-nav");
    expect(within(nav).getByRole("link", { name: "Trial Balance" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("button", { name: "Collapse Reports" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
  });

  it("filters panes with search and exposes badge counts in the link name", async () => {
    const user = userEvent.setup();
    renderSidebar("/finance");
    expect(screen.getByRole("link", { name: "Approvals (4)" })).toBeInTheDocument();

    await user.type(screen.getByRole("searchbox", { name: "Search Finance panes" }), "trial");
    const nav = screen.getByTestId("finance-sidebar-nav");
    expect(within(nav).getByRole("link", { name: "Trial Balance" })).toBeInTheDocument();
    expect(within(nav).queryByRole("link", { name: "Overview" })).not.toBeInTheDocument();
  });

  it("collapses to the 72px icon rail without moving off the left edge", async () => {
    const user = userEvent.setup();
    renderSidebar("/finance");
    await user.click(screen.getByTestId("finance-sidebar-collapse"));
    const rail = screen.getByTestId("finance-sidebar");
    expect(rail.className).toMatch(/w-\[72px\]/);
    expect(rail.className).toMatch(/left-0/);
    expect(screen.queryByRole("searchbox")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Overview" })).toBeInTheDocument();
  });

  it("calls onItemNavigate when a link is clicked", async () => {
    const user = userEvent.setup();
    const { onNavigate } = renderSidebar("/finance");
    await user.click(screen.getByRole("link", { name: "Overview" }));
    expect(onNavigate).toHaveBeenCalledWith(expect.objectContaining({ href: "/finance" }));
  });
});
