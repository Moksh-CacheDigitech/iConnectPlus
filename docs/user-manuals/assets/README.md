# Asset Management User Manual

Intake-to-disposal walkthrough (Incoming → QC → Registration → Inventory → Assignment → DC / Transfers / Maintenance → Disposal), plus Components, Documents, Reports, Users, and Non-IT domain.

## Outputs

| File | Description |
|------|-------------|
| `assets-user-manual.html` | Print-ready HTML (ERP theme) |
| `Assets-Module-User-Manual.pdf` | PDF printed via headless Chrome |
| `assets/screenshots/process/` | Steps 01–15 |
| `assets/screenshots/sidebar/` | 19 primary panes |

## Demo profile

- **Asset:** CT-HP-Aman (`AST-2026-000003`)
- **Make / Model:** HP · HP ELITEBOOK 840 G7
- **Assignee:** Aman Raj (`CT5319`) · New Delhi - CRC2
- **Assignment:** `AASN-2026-000002`
- **IDs:** see `assets/demo-ids.txt`

## Rebuild

```powershell
python docs/user-manuals/assets/_build_assets_manual.py
```

Print PDF (prefer `C:\Temp` if OneDrive yields a tiny file):

```powershell
$chrome = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
$pdfTemp = "C:\Temp\Assets-Module-User-Manual.pdf"
# serve HTML via python -m http.server, then:
& $chrome --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdfTemp" "http://127.0.0.1:8880/assets-user-manual.html"
Copy-Item $pdfTemp "docs\user-manuals\assets\Assets-Module-User-Manual.pdf" -Force
```

## Audience

Asset admins and assigned IT / Non-IT domain members. Sign in with Microsoft Entra SSO.
