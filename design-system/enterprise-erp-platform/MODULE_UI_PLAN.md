# iConnect Plus: Module UI Contract

> Every authenticated module (CRM, Finance, Assets, HR, Procurement, Projects, Service,
> Marketing, GRC, Documents, and the platform modules) builds its UI against this file.
>
> Read order: `MASTER.md` (tokens) → this file (shell, templates, components) →
> `pages/app-shell.md` (sidebar motion) → `pages/[module].md` (domain content only).

---

## 1. Tokens

`apps/web/src/app/globals.css` is the single source of truth. `MASTER.md` mirrors it.

- Slate canvas + deep teal primary (`oklch(0.42 0.08 210)`), dark greenish-slate left rail (v1.19 / Sep 2026 theme)
- Plus Jakarta Sans, `html { font-size: 90% }` density
- Semantic Tailwind classes only (`bg-card`, `text-muted-foreground`, `border-border`, `bg-sidebar`, …)
- HR uses the same light canvas + dark rail tokens. HRMS purple is scoped to the `.hrms-theme` candidate portal.

`apps/web/design-system/` is retired; it only points back here.

---

## 2. Shell and Navigation

**Primary module navigation is a left vertical sidebar (current layout). The topbar is global chrome only.**

```text
┌──────────────┬──────────────────────────────────────┐
│ Left sidebar │ AppTopbar (account, alerts, company) │
│ 260 ↔ 72px   ├──────────────────────────────────────┤
│ module nav   │ Main content (max ~1400px)           │
│              │   PageHeader                         │
│              │   Toolbar / filters                  │
│              │   Content                            │
└──────────────┴──────────────────────────────────────┘
```

| Piece | Component | Rule |
|-------|-----------|------|
| Shell | `components/layout/app-shell.tsx` | Flex row: left sidebar, then a column of topbar and main |
| Module sidebar | `components/layout/module-sidebar.tsx` (`ModuleSidebar`) | Left rail only. Config-driven groups, items, badges, nested children, optional search |
| Config-only sidebars | `config/workspace-sidebars.ts` + `components/layout/workspace-module-sidebar.tsx` | Finance, GRC, Documents, Analytics, Sales, Inventory, Manufacturing, Quality, Payroll, Recruitment, Helpdesk, Integration, Ecommerce, Portal |
| Custom sidebars | `ModuleSidebar` wrappers in each module | CRM, Projects, Procurement (badges, prefetch), Assets (domain switcher), Service (role filtering), Marketing, HR |
| Sidebar registry | `components/layout/module-sidebar-registry.tsx` (`ShellSidebar`) | Maps a pathname to the module's left rail; `AppShell` has no per-module `if` chain |
| Global sidebar | `components/layout/app-sidebar.tsx` (`AppSidebar`) | Left rail for platform, organization, and master-data routes |
| Topbar | `components/layout/app-topbar.tsx` | Account, notifications, company context. Never module navigation |
| Page title | `components/layout/page-header.tsx` (`PageHeader`) | The only page-title component. No `*PageHeader` wrappers |

Rules:

- Never move module links into the topbar, a horizontal mega-menu, or top tabs as primary navigation.
- In-page secondary controls (report tabs, detail sub-tabs, filters) are allowed inside main content. They never replace the left rail.
- Adding a module sidebar means adding an entry to `WORKSPACE_SIDEBARS` (title, icon, items). Only modules with special nav logic get a `ModuleSidebar` wrapper plus a registry entry. Never a new sidebar component.
- Module layouts (`app/(app)/[module]/layout.tsx`) do not render navigation. No `*WorkspaceNav` tab strips above page content.
- Collapse motion and the collapsed icon rail follow `pages/app-shell.md` (Figma spec). `ModuleSidebar` and `AppSidebar` share the same choreography.

### `ModuleSidebar` API

```tsx
<ModuleSidebar
  moduleKey="crm"
  title="Sales CRM"
  subtitle="21 workspace panes"
  icon={Handshake}
  groups={[{ label: "Workspace", items: CRM_NAV }]}
  isActive={(item) => isCrmNavActive(pathname, item.href)}
  searchPlaceholder="Search CRM…"        // omit to hide search
  onItemNavigate={(item) => {}}          // optional click hook
  onItemWarm={(item) => {}}              // optional prefetch hook
/>
```

`ModuleNavItem` = `{ title, href, icon?, badge?, children? }`. Items without an icon render initials in the collapsed rail.

---

## 3. Page Templates

Every authenticated page is one of these four. Vertical rhythm is `space-y-4` (`WorkspacePage`).

### A. Module hub (landing)

1. `PageHeader` + primary actions
2. KPI strip: up to 4 `KpiCard`s — default `hero` surface (CRM-rail teal/slate gradient). Use `variant="panel"` only for dense report toolbars that need a light card. Never Email-Intelligence blue→cyan.
3. Attention / recent work (`DataTable` or `WorkspaceSection` list)
4. Links into sub-areas (grouped, no API paths)

Raw `/api/v1` paths are never shown as product UX. `components/module/module-hub.tsx` implements this template for config-only modules.

### B. Resource list

1. `PageHeader` + create / export actions
2. `ListToolbar` (title, count, filters, search) — built into `DataTable`
3. `DataTable` with sort, pagination, and optional bulk actions
4. `EmptyState` / `ErrorBanner` / `TableSkeleton` for the empty, error, and loading cases

### C. Record detail / form

1. `PageHeader` with back link, status badge, primary actions
2. `WorkspaceSection` cards and `DetailGrid` / `DetailItem` fields, or a form grid
3. Side panels only when the interaction needs them

### D. Report / ledger

1. `PageHeader` + period and filter controls
2. Sticky-header dense table (`DataTable` or `dataTableClasses`)
3. `EmptyState` / `ErrorBanner` / `TableSkeleton`

---

## 4. Shared Components

All live in `apps/web/src/components/shared/`. Module kits (`crm-ui`, `projects-ui`, `service-ui`, `procurement-ui`) are thin re-exports kept for import compatibility; new code imports from `components/shared` directly.

| Component | File | Purpose |
|-----------|------|---------|
| `WorkspacePage`, `WorkspaceSection`, `ListPanel`, `IconBadge`, `InfoBanner`, `WarnBanner`, `HeadlineBand`, `HeadlineStat`, `DetailGrid`, `DetailItem`, `MetricStrip`, `Metric`, `ActivityTile`, `ViewAllLink`, `CountBadge` | `workspace-ui.tsx` | Page rhythm, section cards, list shells, detail fields |
| `KpiCard`, `KpiStrip` | `kpi-card.tsx` | Compact metric tiles (12px padding, tone bar, tabular numbers) |
| `DataTable` | `data-table.tsx` | Columns, search filter, sort, pagination, row selection, bulk actions, built-in states |
| `dataTableClasses` | `table-classes.ts` | Class map for hand-built tables that cannot use `DataTable` yet |
| `SortableTh`, `useTableSort`, `sortRows`, `compareSortValues` | `table-sort.tsx` | Sorting for hand-built tables |
| `ListToolbar`, `ListSearch` | `list-toolbar.tsx` | Dense single-row toolbar above lists |
| `EmptyState` | `empty-state.tsx` | Icon, title, description, optional action; `bordered` and `compact` variants |
| `ErrorBanner` | `error-banner.tsx` | Message, optional retry and sign-in actions |
| `TableSkeleton` | `table-skeleton.tsx` | 36px placeholder rows matching table density |

Do not create new module-prefixed copies of these. If a module needs a variant, add a prop to the shared component.

---

## 5. Density and Interaction

Baked into the shared components; pages inherit them.

- Table rows about 36px; heads `text-xs` uppercase; body 12–13px; `tabular-nums` for numbers
- KPI and compact card padding 12px (`p-3`); section bodies 16px
- Toolbar and filter gaps 8px (`gap-2`)
- `cursor-pointer` on every clickable element
- Transitions 150–300ms; `motion-reduce:` fallbacks on every animation
- Visible `focus-visible:ring` on links, buttons, and sortable headers
- Text contrast at least 4.5:1 (`text-muted-foreground` is the lightest allowed body text)
- Table rows hover with color only, never `scale` or `translate`
- Hub link cards may lift subtly; tables and KPI tiles do not
- Check 375 / 768 / 1024 / 1440 widths; wide tables scroll inside their panel, not the page

---

## 6. Forbidden

- Replacing left module sidebars with a top navbar or top primary module nav
- Dark-mode-by-default authenticated UI
- AI purple/pink gradients; purple in the main shell (HR exception: `.hrms-theme` portal only)
- Marketing heroes or oversized display type inside app routes
- Emoji icons
- New module-specific `*-page-header.tsx` or `*-ui.tsx` class maps duplicating `components/shared`
- Layout-shifting table row hovers
- A second design-system Master with a conflicting palette
