# Projects Module User Manual

End-to-end site delivery walkthrough (PO Queue → Create Project → Survey → SCM → Onsite Delivery → Material Handover → Installation → Acceptance → Completed), plus portfolio/PMO screens and all 8 primary sidebar panes.

## Outputs

| File | Description |
|------|-------------|
| `projects-user-manual.html` | Print-ready HTML (ERP theme, matches CRM manual) |
| `Projects-Module-User-Manual.pdf` | PDF printed from HTML via headless Chrome |
| `assets/screenshots/process/` | Steps 01–21 from one live demo rollout |
| `assets/screenshots/sidebar/` | All 8 Projects workspace panes |

## Demo rollout (capture target)

- **Customer:** Airtel
- **Project:** H2 26-27 - Spectrum Santhome
- **CRM link:** `PRJ-2026-000003` - customer PO `97210`
- **Site:** Spectrum Santhome (`SITE-2026-000003`)
- **Seed:** H-Cloud PO row OK when staging sync is pending
- **IDs:** see `assets/demo-ids.txt`

## Rebuild

From repo root (or this folder):

```powershell
python docs/user-manuals/projects/_build_projects_manual.py
```

Then print PDF (Chrome required). Prefer a local `http.server` and print to `C:\Temp` first if the OneDrive path yields a tiny PDF:

```powershell
$chrome = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
$html = (Resolve-Path "docs\user-manuals\projects\projects-user-manual.html").Path
$pdfTemp = "C:\Temp\Projects-Module-User-Manual.pdf"
$pdf  = (Resolve-Path "docs\user-manuals\projects").Path + "\Projects-Module-User-Manual.pdf"
& $chrome --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdfTemp" "$html"
Copy-Item $pdfTemp $pdf -Force
```

Screenshots: use the locked browser session against the running app, then `_save_shot.ps1` (or copy from `%LOCALAPPDATA%\Temp\cursor\screenshots`).

## Audience

Module admins and assigned members. Sign in with Microsoft Entra SSO.
