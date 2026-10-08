# App Shell Page Overrides

> **PROJECT:** iConnect Plus
> **Page Type:** Application shell (sidebar + topbar + workspace)

> Rules in this file **override** `MASTER.md`. Only deviations are listed here.

---

## Page-Specific Rules

### Layout Overrides

- **Structure:** Fixed/collapsible **left** vertical sidebar + sticky topbar + scrollable main content
- **Primary module navigation = left vertical sidebar** (current layout). Every module (CRM, Projects, Procurement, Assets, Service, Marketing, HR) and the global `AppSidebar` render on the left.
- **Topbar is global chrome only:** account, notifications, company context. It never carries module navigation.
- **Implementation:** `ModuleSidebar` (`apps/web/src/components/layout/module-sidebar.tsx`) + registry (`module-sidebar-registry.tsx`). One config per module; placement is fixed to the left and not configurable.
- **Max Width:** Full-width workspace; main content capped at ~1400px
- **Grid:** 12-column for dashboards; fluid for list/detail pages
- **Sidebar width:** 260px expanded / 72px collapsed icon rail
- **Header height:** ~56px

### Spacing Overrides

- **Content Density:** High - optimize for information display
- Page rhythm `space-y-4`; workspace gutter set once by `AppShell`
- Table row height ~36px; card padding ~12px; grid gap ~8px

### Typography Overrides

- Body/UI: 12-14px for dense tables and sidebars
- Page titles: clear hierarchy, not oversized display type
- No clamp(3rem-12rem) hero typography inside the app shell

### Color Overrides

- Neutral light shell (`--background` slate canvas, deep teal `--primary`)
- Left rail uses `--sidebar*` tokens only (black rail, light-teal active glyph); HR included
- Status colors for operational states: success green, warning amber, danger red
- Do **not** default to dark mode

### Component Overrides

- Prefer ShadCN primitives (Button, Input, Card, Badge, Separator, Table patterns)
- Shared workspace components from `apps/web/src/components/shared/` (see `MODULE_UI_PLAN.md`)
- Interactive surfaces only as cards when interaction requires a container
- Multi-select and bulk actions supported on resource lists (`DataTable`)
- Icons: Lucide only (no emoji icons)

### Avoid

- Do not relocate module nav to a top navbar, horizontal mega-menu, or top tabs as primary navigation
- Per-module sidebar components with their own colors or collapse behavior
- Marketing hero sections inside authenticated app routes
- AI purple/pink gradients (including the legacy HRMS purple rail)
- Playful / maximalist decoration
- Layout-shifting hover scales on dense tables

---

## Collapse Motion (Figma)

**File:** [iConnect Plus — Sidebar Collapse](https://www.figma.com/design/YYC06qVSLGCCbWTijOohO6)

| State | Width |
|-------|-------|
| Expanded | 260px |
| Collapsed | 72px (icon rail) |

### Sequence

1. Labels / account text fade (160ms) — never hard-cut mid-glyph
2. Search height collapses (220ms)
3. Rail width 260 ↔ 72 (320ms, `cubic-bezier(0.32, 0.72, 0, 1)`)
4. Icons stay left-aligned and visible in the 72px rail
5. Page layout spacer updates once at click so charts resize once, not per frame

`AppSidebar` and `ModuleSidebar` share this choreography through `useSidebarCollapse` (`apps/web/src/components/layout/sidebar-rail.tsx`). With `prefers-reduced-motion`, width and labels switch instantly.

### Collapsed icon rail

**Figma:** [Collapsed Icon Rail Spec](https://www.figma.com/design/YYC06qVSLGCCbWTijOohO6)

- Flat list (no section title gaps)
- **40×40** circular hit targets, **10px** equal gap (`gap-2.5`)
- Idle: `bg-white/8`; Active: sidebar accent + primary glyph
- Centered in 72px rail

### Avoid

- `clip-path` only “cut” (no fade / width choreography)
- Width-driven chart redraw every animation frame
- Uneven group margins when collapsed
