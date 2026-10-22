# Marketing & Social User Manual

Campaign-to-publish walkthrough (Campaign → Deliverable → My Work / Content Studio → Requests → Calendar), plus Operations, Workload, Brand kit, Insights, Social, Microsoft 365, and Users.

## Outputs

| File | Description |
|------|-------------|
| `marketing-user-manual.html` | Print-ready HTML (ERP theme) |
| `Marketing-Module-User-Manual.pdf` | PDF printed via headless Chrome |
| `assets/screenshots/process/` | Steps 01–15 |
| `assets/screenshots/sidebar/` | 18 workspace panes |

## Demo profile

- **Campaign:** etciso (`MKT-00002`)
- **Deliverable:** 12 pager (`TSK-00001` / `CRQ-00001`)
- **Creator:** Deeksha Sharma · **Approver:** Prarthana Gupta
- **Module admin:** Techbank
- **IDs:** see `assets/demo-ids.txt`

## Rebuild

```powershell
python docs/user-manuals/marketing/_build_marketing_manual.py
```

Print PDF (prefer `C:\Temp` if OneDrive yields a tiny file):

```powershell
$chrome = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
$pdfTemp = "C:\Temp\Marketing-Module-User-Manual.pdf"
# serve HTML via python -m http.server, then:
& $chrome --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdfTemp" "http://127.0.0.1:8880/marketing-user-manual.html"
Copy-Item $pdfTemp "docs\user-manuals\marketing\Marketing-Module-User-Manual.pdf" -Force
```

## Audience

Marketing admins, creators, and approval heads. Sign in with Microsoft Entra SSO.
