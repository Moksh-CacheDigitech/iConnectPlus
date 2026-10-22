# Platform (Whole ERP) User Manual

Common orientation for iConnect Plus: Microsoft Entra sign-in, Home dashboard, My Jobs, Foundation / Organization / Master Data pillars, shell navigation, notifications, and the operations module catalog.

Detailed SOP manuals for CRM, Projects, Procurement, HRMS, Assets, Marketing, and Service live in sibling folders under `docs/user-manuals/`.

## Outputs

| File | Description |
|------|-------------|
| `platform-user-manual.html` | Print-ready HTML (ERP theme) |
| `Platform-ERP-User-Manual.pdf` | PDF printed via headless Chrome |
| `assets/screenshots/process/` | Steps 00–09 |
| `assets/screenshots/sidebar/` | 7 shell / pillar panes |

## Demo profile

- **User:** Techbank (`techbank@cachedigitech.com`)
- **Home:** `/home` · **My Jobs:** 2 open CRM jobs (demo capture)
- **IDs:** see `assets/demo-ids.txt`

## Rebuild

```powershell
python docs/user-manuals/platform/_build_platform_manual.py
```

Print PDF (prefer `C:\Temp` if OneDrive yields a tiny file):

```powershell
$chrome = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
$pdfTemp = "C:\Temp\Platform-ERP-User-Manual.pdf"
# serve HTML via python -m http.server, then:
& $chrome --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdfTemp" "http://127.0.0.1:8880/platform-user-manual.html"
Copy-Item $pdfTemp "docs\user-manuals\platform\Platform-ERP-User-Manual.pdf" -Force
```

## Audience

Everyone who signs in to iConnect Plus. Sign in with Microsoft Entra SSO.
