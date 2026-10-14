import { describe, expect, it } from "vitest";

import {
  filterInboxForModule,
  mapInboxHref,
  resolveNotificationModuleScope,
  type InboxNotification,
} from "@/lib/notification-inbox";

function item(partial: Partial<InboxNotification> & Pick<InboxNotification, "id" | "kind">): InboxNotification {
  return {
    title: "t",
    body: "b",
    unread: true,
    created_at: "2026-01-01T00:00:00Z",
    href: null,
    read_at: null,
    ...partial,
  };
}

describe("notification-inbox module scope", () => {
  it("resolves module scopes from pathname", () => {
    expect(resolveNotificationModuleScope("/home")).toBe("all");
    expect(resolveNotificationModuleScope("/hr/leave")).toBe("hr");
    expect(resolveNotificationModuleScope("/finance/journals")).toBe("finance");
    expect(resolveNotificationModuleScope("/procurement/orders")).toBe("procurement");
  });

  it("filters finance notifications by href/kind", () => {
    const rows = [
      item({ id: "1", kind: "domain.finance.journal_posted", href: "/finance/journals/1" }),
      item({ id: "2", kind: "leave", href: "/hr/ess-inbox" }),
    ];
    const filtered = filterInboxForModule(rows, "finance");
    expect(filtered.map((r) => r.id)).toEqual(["1"]);
  });

  it("maps unknown kinds to home instead of HR", () => {
    expect(mapInboxHref(null, "info")).toBe("/home");
    expect(mapInboxHref("/finance/ar", "x")).toBe("/finance/ar");
  });
});
