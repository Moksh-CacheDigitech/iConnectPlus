"""Fix escaped quotes in assembled payroll generator."""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_payroll_module.py"
text = p.read_text(encoding="utf-8")
text2 = text.replace("r\\'\\'\\'", "r'''").replace("\\'\\'\\'", "'''")
p.write_text(text2, encoding="utf-8")
print("fixed", len(text), "->", len(text2))

import py_compile

py_compile.compile(str(p), doraise=True)
print("syntax ok")
