# Service Module User Manual

SOP service request ticket walkthrough (New Ticket → Assign → Engineer Working → SLA → Resolve / Close), plus Dashboard, Users, Mailbox, and SLA Policies.

## Outputs

| File | Description |
|------|-------------|
| `service-user-manual.html` | Print-ready HTML (ERP theme) |
| `Service-Module-User-Manual.pdf` | PDF printed via headless Chrome |
| `assets/screenshots/process/` | Steps 01–09 |
| `assets/screenshots/sidebar/` | 6 panes (incl. Mailbox) |

## Demo profile

- **Ticket:** SR-2026-000007 — Email test - automatic ticket
- **Status:** Engineer Working · P3 · Remote Support
- **Contact:** Test Customer · **Owner:** Anita Rao
- **Service Head:** Techbank
- **IDs:** see `assets/demo-ids.txt`

## Rebuild

```powershell
python docs/user-manuals/service/_build_service_manual.py
```

Print PDF (prefer `C:\Temp` if OneDrive yields a tiny file):

```powershell
$chrome = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
$pdfTemp = "C:\Temp\Service-Module-User-Manual.pdf"
# serve HTML via python -m http.server, then:
& $chrome --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdfTemp" "http://127.0.0.1:8880/service-user-manual.html"
Copy-Item $pdfTemp "docs\user-manuals\service\Service-Module-User-Manual.pdf" -Force
```

## Audience

Service Heads, Service Engineers, and Field Engineers. Sign in with Microsoft Entra SSO.

## Role-gated panes

- **Mailbox** — requires `service.request:update` or `service.request:approve`
- **Field Engineer** — visible for Field Engineer roles only
