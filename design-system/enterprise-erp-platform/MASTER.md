# Design System Master File

> **LOGIC:** When building a specific page, first check `design-system/enterprise-erp-platform/pages/[page-name].md`.
> If that file exists, its rules **override** this Master file for domain content only
> (KPI names, status colors, section order). Page files never override shell chrome,
> fonts, or the primary palette.
>
> **Cross-module contract:** [`MODULE_UI_PLAN.md`](./MODULE_UI_PLAN.md) defines the shell,
> page templates, and shared components every module must use. Read it before any UI work.

---

**Project:** iConnect Plus
**Category:** B2B SaaS Admin (ERP)
**Style:** Data-dense dashboard + Swiss minimalism
**Stack:** Next.js + TypeScript + Tailwind v4 + ShadCN UI
**Canonical tokens:** `apps/web/src/app/globals.css` (this file mirrors it; if they disagree, `globals.css` wins and this file must be updated)

---

## Global Rules

### Color Palette (light, default)

Use the semantic Tailwind classes (`bg-primary`, `text-muted-foreground`, …), never raw hex in module UI.

| Role | CSS Variable | Value | Usage |
|------|--------------|-------|-------|
| Background | `--background` | `oklch(0.985 0.004 220)` | Slate canvas behind workspace |
| Foreground | `--foreground` | `oklch(0.22 0.02 240)` | Body text |
| Card | `--card` | `oklch(0.995 0.002 220)` | Panels, tables, sections |
| Primary | `--primary` | `oklch(0.42 0.08 210)` | Deep teal: primary actions, active states, links |
| On Primary | `--primary-foreground` | `oklch(0.99 0.005 210)` | Text on primary |
| Secondary | `--secondary` | `oklch(0.95 0.01 220)` | Secondary buttons, chips |
| Muted | `--muted` | `oklch(0.955 0.008 220)` | Table heads, subtle fills |
| Muted text | `--muted-foreground` | `oklch(0.5 0.02 240)` | Hints, metadata (meets 4.5:1 on card) |
| Accent | `--accent` | `oklch(0.94 0.02 200)` | Hover fills, soft highlights |
| Destructive | `--destructive` | `oklch(0.55 0.2 25)` | Errors, destructive actions |
| Border / Input | `--border`, `--input` | `oklch(0.9 0.01 220)` | Hairlines, inputs |
| Ring | `--ring` | `oklch(0.55 0.08 210)` | Focus rings |
| Charts | `--chart-1` … `--chart-5` | teal, green, slate-blue, amber, red-orange | Data series |

**Sidebar (left rail) tokens:** `--sidebar` (`#000000`), `--sidebar-foreground`, `--sidebar-primary` (light teal), `--sidebar-accent`, `--sidebar-border`, `--sidebar-ring`. Every left sidebar uses these; no module may hardcode its own rail colors.

**Status semantics (all modules):** success = emerald, warning/pending = amber, danger/overdue = red, info = sky. Soft surfaces use the `-50` tint with `-700/-800` text.

**HR:** authenticated HR routes use the same enterprise teal tokens. The legacy HRMS purple (`#9B5BB8`) is allowed only inside `.hrms-theme` on the candidate onboarding portal, never on the shell or authenticated HR pages.

**Dark mode:** `.dark` tokens exist, but the authenticated app never defaults to dark.

### Typography

- **Font:** Plus Jakarta Sans for headings and body (`--font-sans`, `--font-heading`, loaded in `apps/web/src/app/layout.tsx`)
- **Mono:** Geist Mono (`--font-mono`) for codes and identifiers only
- **Scale:** `html { font-size: 90% }` gives app-wide density without zoom gaps
- **Page title:** `text-2xl` semibold (`PageHeader`); no display or hero type inside the app
- **Section title:** `text-sm`/`text-base` semibold
- **Table body:** 12–13px; table heads `text-xs` uppercase with wide tracking
- **Numbers:** `tabular-nums` on every metric and numeric column

### Spacing (high density)

| Token | Tailwind | Usage |
|-------|----------|-------|
| 4px | `gap-1` | Icon-to-label, badge internals |
| 8px | `gap-2` | Toolbar controls, filter rows, KPI grid gaps |
| 12px | `p-3` | KPI tiles and compact cards |
| 16px | `p-4`, `space-y-4` | Section bodies, page vertical rhythm |
| 24px | `px-6 py-6` | Workspace gutter (set once by `AppShell`) |

- Table rows are about 36px (`px-3 py-2` cells with 13px text)
- Page vertical rhythm is `space-y-4` everywhere (`WorkspacePage`)

### Radius and Elevation

- `--radius: 0.7rem`; cards and panels use `rounded-xl`, controls use `rounded-lg`
- One shadow level for panels (`shadow-sm` equivalent); no multi-layer glow shadows
- Overlays (dialogs, popovers) may use `shadow-lg`

### Motion

- Hover and focus transitions: 150–300ms, `ease-out` or the shell curve `cubic-bezier(0.16, 1, 0.3, 1)`
- Sidebar collapse: Figma choreography in `pages/app-shell.md`
- Always pair animations with `motion-reduce:` fallbacks
- No `scale` or `translate` hover effects on table rows or other dense rows

### Icons

- Lucide only (Heroicons acceptable for brand marks). No emoji icons.

---

## Application Pattern

- **Shell:** left vertical sidebar (260px expanded / 72px collapsed rail) + thin sticky topbar + scrollable main content capped at ~1400px.
- **Primary module navigation lives in the left sidebar.** The topbar is global chrome only (account, notifications, company context). Do not build a top-nav admin shell, horizontal mega-menu, or top module tabs as primary navigation.
- **Pages:** `PageHeader` → dense filter/search toolbar → content (table, board, detail). See `MODULE_UI_PLAN.md` for the four page templates.
- **Shared components:** `apps/web/src/components/shared/*` (workspace UI, `DataTable`, `EmptyState`, `ErrorBanner`, `TableSkeleton`, `KpiCard`, `ListToolbar`). Modules must not ship their own copies.

---

## Anti-Patterns (Do NOT Use)

- Replacing the left module sidebar with a top navbar
- Dark-mode-by-default authenticated UI
- AI purple/pink gradients; purple in the main shell
- Marketing heroes, oversized display type, or waitlist-style sections inside app routes
- Emoji icons
- Module-specific `*-page-header.tsx` or `*-ui.tsx` kits that duplicate `components/shared`
- Layout-shifting hovers on tables and dense rows
- Raw `/api/v1` paths shown as product UX
- Missing `cursor-pointer` on clickable elements
- Invisible focus states; text contrast below 4.5:1
- Instant state changes without a transition

---

## Pre-Delivery Checklist

- [ ] Uses semantic tokens from `globals.css` (no raw hex outside documented status colors)
- [ ] Left sidebar unchanged as primary module nav; no new top-nav chrome
- [ ] Page follows a `MODULE_UI_PLAN.md` template and uses `components/shared`
- [ ] Lucide icons only; no emojis
- [ ] `cursor-pointer` on all clickable elements
- [ ] Hover states with 150–300ms transitions, no layout shift on rows
- [ ] Text contrast at least 4.5:1
- [ ] Visible focus rings for keyboard navigation
- [ ] `prefers-reduced-motion` respected
- [ ] Responsive at 375px, 768px, 1024px, 1440px; no horizontal page scroll on mobile
