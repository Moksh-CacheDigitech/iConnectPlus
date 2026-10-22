# CRM Module User Manual

End-to-end process walkthrough for Sales CRM (Company → Lead → BOQ/SOW → Opportunity → Vendor Quote → Quote → PO → OVF → Won), plus all 24 sidebar panes.

## Outputs

| File | Description |
|------|-------------|
| `crm-user-manual.html` | Print-ready HTML (ERP theme, matches Projects manual) |
| `CRM-Module-User-Manual.pdf` | PDF printed from HTML via headless Chrome |
| `assets/screenshots/process/` | Steps 01–31 from one live demo deal |
| `assets/screenshots/sidebar/` | All 24 CRM workspace panes |
| `assets/demo-files/` | Sample BOQ, SOW, OEM quote, customer PO PDFs |
| `assets/demo-ids.txt` | Live IDs for the walkthrough deal |

## Demo deal (captured)

- **Company:** Walkthrough Demo Systems Pvt Ltd (`COMP-111`)
- **DR:** `DR-2026-8`
- **Quote:** `DR-2026-8/Q1` (₹4,50,155, margin 23.33%)
- **PO:** `WDS-PO-FY26-001`
- **OVF:** `DR-2026-8/OVF1`
- **Outcome:** Deal Won

## Rebuild

From repo root (or this folder):

```powershell
python docs/user-manuals/crm/_build_crm_manual.py
```

Then print PDF (Chrome required):

```powershell
$chrome = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
$html = (Resolve-Path "docs\user-manuals\crm\crm-user-manual.html").Path
$pdf  = (Resolve-Path "docs\user-manuals\crm").Path + "\CRM-Module-User-Manual.pdf"
& $chrome --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdf" "$html"
```

Screenshots: use the locked browser session against the running app, then `_save_shot.ps1` (or copy from `%LOCALAPPDATA%\Temp\cursor\screenshots`).

## Audience

Module admins and assigned members. Sign in with Microsoft Entra SSO.
