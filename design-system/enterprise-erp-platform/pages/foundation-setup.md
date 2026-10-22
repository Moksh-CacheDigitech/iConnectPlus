# Foundation Setup Wizard — Page Override

> Overrides `MASTER.md` for **domain content only**. Shell, fonts, and primary palette stay global.

**Route:** `/foundation`  
**Template:** Guided multi-step setup (progressive disclosure), not ModuleHub KPIs.

## Purpose

Walk platform admins through the locked Foundation sequence before Organization / Master Data:

1. Access & sessions  
2. Tenant  
3. Users  
4. RBAC (roles → permissions)  
5. Engines (workflow, notification, audit)  
6. Settings  
7. Handoff → Organization  

## Section order

1. PageHeader — “Foundation setup”  
2. Horizontal / responsive step rail (Step N of M + labels)  
3. Active step panel — title, short copy, checklist status, primary CTA into resource admin  
4. Footer — Back / Skip / Continue (final: Go to Organization)

## Status colors

| State | Treatment |
|-------|-----------|
| Done | emerald text / soft emerald chip |
| Needs attention | amber chip |
| Current | primary border / ring |
| Upcoming | muted |

## Do not

- Put company / branch / employee masters in this wizard (Organization / Master Data)  
- Use purple/pink gradients or dark-mode-by-default  
- Show raw `/api/v1` paths as product copy  
