# Procurement Module User Manual

End-to-end SCM walkthrough (SCM Queue → View OVF → Item plan → Create PO → Approval → GRN → Billing/DC → Delivery Status), plus inventory/stock paths and all 19 sidebar panes (Workspace + Insight).

## Outputs

| File | Description |
|------|-------------|
| `procurement-user-manual.html` | Print-ready HTML (ERP theme, matches CRM/Projects manuals) |
| `Procurement-Module-User-Manual.pdf` | PDF printed from HTML via headless Chrome |
| `assets/screenshots/process/` | Steps 01–14 from the live demo OVF / PO path |
| `assets/screenshots/sidebar/` | All 19 Procurement workspace + insight panes |

## Demo rollout (capture target)

- **Customer:** Walkthrough Demo Systems Pvt Ltd
- **Project:** Walkthrough Demo - Campus WiFi FY26
- **OVF:** `DR-2026-8/OVF1`
- **Customer PO:** `WDS-PO-FY26-001`
- **Vendor / OEM:** Redington / Cisco
- **Example issued PO (GRN screens):** `PO/CDT/068`
- **IDs:** see `assets/demo-ids.txt`
- **Upstream:** Complete the CRM user manual walkthrough so the OVF is shared to SCM

## Rebuild

From repo root (or this folder):

```powershell
python docs/user-manuals/procurement/_build_procurement_manual.py
```

Then print PDF (Chrome required). Prefer a local `http.server` and print to `C:\Temp` first if the OneDrive path yields a tiny PDF:

```powershell
$chrome = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
$html = (Resolve-Path "docs\user-manuals\procurement\procurement-user-manual.html").Path
$pdfTemp = "C:\Temp\Procurement-Module-User-Manual.pdf"
$pdf  = (Resolve-Path "docs\user-manuals\procurement").Path + "\Procurement-Module-User-Manual.pdf"
& $chrome --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdfTemp" "$html"
Copy-Item $pdfTemp $pdf -Force
```

Screenshots: use the locked browser session against the running app, then `_save_shot.ps1`.

## Audience

Module admins and assigned SCM members. Sign in with Microsoft Entra SSO.
