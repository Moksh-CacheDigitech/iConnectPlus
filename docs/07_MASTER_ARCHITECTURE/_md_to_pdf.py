"""Convert Enterprise_ERP_Module_Features.md → HTML, then invoke Chrome for PDF."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "Enterprise_ERP_Module_Features.md"
HTML_PATH = ROOT / "Enterprise_ERP_Module_Features.html"
PDF_PATH = ROOT / "Enterprise_ERP_Module_Features.pdf"

CSS = """
@page {
  size: A4;
  margin: 14mm 12mm 16mm 12mm;
}
* { box-sizing: border-box; }
html, body {
  font-family: "Segoe UI", Arial, Helvetica, sans-serif;
  font-size: 10pt;
  line-height: 1.4;
  color: #0f172a;
  background: #fff;
  margin: 0;
  padding: 0;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
h1 {
  font-size: 20pt;
  color: #0f172a;
  border-bottom: 2px solid #1e3a5f;
  padding-bottom: 8px;
  margin: 0 0 14px;
  page-break-after: avoid;
}
h2 {
  font-size: 14pt;
  color: #1e3a5f;
  margin: 22px 0 10px;
  padding-top: 4px;
  border-top: 1px solid #e2e8f0;
  page-break-after: avoid;
  break-after: avoid-page;
}
h3 {
  font-size: 11.5pt;
  color: #334155;
  margin: 16px 0 8px;
  page-break-after: avoid;
  break-after: avoid-page;
}
h4 {
  font-size: 10.5pt;
  color: #475569;
  margin: 12px 0 6px;
  page-break-after: avoid;
}
p, li { orphans: 3; widows: 3; }
ul, ol { padding-left: 1.6em; margin: 6px 0 10px; }
ol { padding-left: 2.2em; list-style-position: outside; }
li { margin: 2px 0; }
ol li { padding-left: 0.35em; }
table {
  width: 100% !important;
  max-width: 100% !important;
  border-collapse: collapse;
  margin: 10px 0 14px;
  font-size: 8pt;
  table-layout: fixed;
  page-break-inside: auto;
  word-wrap: break-word;
  overflow-wrap: anywhere;
}
thead { display: table-header-group; }
tr { page-break-inside: avoid; break-inside: avoid; }
th, td {
  border: 1px solid #94a3b8;
  padding: 5px 6px;
  vertical-align: top;
  text-align: left;
  word-break: break-word;
  overflow-wrap: anywhere;
  hyphens: auto;
}
th {
  background: #e2e8f0 !important;
  font-weight: 700;
  color: #0f172a;
}
code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 8pt;
  background: #f1f5f9;
  padding: 1px 3px;
  border-radius: 2px;
}
pre {
  font-family: Consolas, "Courier New", monospace;
  font-size: 7.5pt;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 8px;
  white-space: pre-wrap;
  word-break: break-word;
  page-break-inside: avoid;
}
a { color: #1e3a5f; text-decoration: none; }
hr { border: none; border-top: 1px solid #cbd5e1; margin: 18px 0; }
strong { color: #0f172a; }
blockquote {
  margin: 8px 0;
  padding: 6px 10px;
  border-left: 3px solid #1e3a5f;
  background: #f8fafc;
  color: #334155;
}
.mermaid-note {
  font-size: 8pt;
  color: #64748b;
  font-style: italic;
  margin: 0 0 4px;
}
"""


def replace_mermaid(match: re.Match[str]) -> str:
    body = match.group(1).strip()
    return (
        '\n\n<div class="mermaid-note">Architecture diagram (source)</div>\n\n'
        f"```text\n{body}\n```\n\n"
    )


def build_html() -> Path:
    text = MD_PATH.read_text(encoding="utf-8")
    text = re.sub(r"```mermaid\n(.*?)```", replace_mermaid, text, flags=re.DOTALL)
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc", "sane_lists", "smarty"],
        extension_configs={"toc": {"permalink": False}},
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>iConnect Plus - Module Features (as built)</title>
  <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""
    HTML_PATH.write_text(html, encoding="utf-8")
    return HTML_PATH


def find_chrome() -> str:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe",
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in candidates:
        if path.is_file():
            return str(path)
    raise FileNotFoundError("Chrome or Edge not found for PDF print")


def print_pdf(html_path: Path) -> Path:
    chrome = find_chrome()
    html_uri = html_path.resolve().as_uri()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_PATH.resolve()}",
        html_uri,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return PDF_PATH


def main() -> int:
    html_path = build_html()
    print(f"Wrote {html_path} ({html_path.stat().st_size} bytes)")
    pdf_path = print_pdf(html_path)
    if not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
        print(f"PDF missing or too small: {pdf_path}", file=sys.stderr)
        return 1
    print(f"Wrote {pdf_path} ({pdf_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
