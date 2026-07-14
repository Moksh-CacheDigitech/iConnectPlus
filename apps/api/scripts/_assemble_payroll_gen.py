"""Assemble complete _gen_payroll_module.py from partials."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

head_path = SCRIPTS / "_gen_payroll_module.head"
if head_path.exists():
    head = head_path.read_text(encoding="utf-8")
else:
    head = (SCRIPTS / "_gen_payroll_module.py").read_text(encoding="utf-8")
    if "def main()" in head:
        head = head.split("def main()")[0]
tail = (SCRIPTS / "_gen_payroll_module.tail").read_text(encoding="utf-8")
finish = (SCRIPTS / "_finish_payroll_gen.py").read_text(encoding="utf-8")
funcs = (SCRIPTS / "_gen_payroll_module_funcs.py").read_text(encoding="utf-8")
body = (SCRIPTS / "_gen_payroll_module_body.py").read_text(encoding="utf-8")

match = re.search(r"remainder = r'''(.+)'''\s*\n\n# Import", finish, re.DOTALL)
remainder = match.group(1) if match else ""
remainder = remainder.replace("r\\'\\'\\'", "r'''").replace("\\'\\'\\'", "'''")

full = head + tail + remainder + "\n\n" + funcs + "\n\n" + body
out = SCRIPTS / "_gen_payroll_module.py"
out.write_text(full, encoding="utf-8")
print(f"Assembled {out} ({len(full.splitlines())} lines)")
