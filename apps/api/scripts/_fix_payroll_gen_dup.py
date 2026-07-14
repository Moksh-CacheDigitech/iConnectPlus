"""Truncate duplicated payroll generator to single copy and fix migrations."""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_payroll_module.py"
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
# Keep through first `if __name__` block
end = 0
for i, line in enumerate(lines):
    if line.strip() == 'main()':
        # find if __name__ block after this
        if i + 1 < len(lines) and '__name__' in lines[i - 1]:
            end = i + 1
            break
for i, line in enumerate(lines):
    if line.startswith('if __name__ == "__main__":'):
        end = i + 2
        break

truncated = "".join(lines[:end])
truncated = truncated.replace(
    '    if target == "schema" or target.startswith("seed"):',
    '    if target == "schema" or (isinstance(target, str) and target.startswith("seed")):',
)
p.write_text(truncated, encoding="utf-8")
# Save clean head for future assemblies
head_end = truncated.index("MODELS[\"salary_component\"]")
(Path(__file__).parent / "_gen_payroll_module.head").write_text(truncated[:head_end], encoding="utf-8")
print(f"truncated to {len(truncated.splitlines())} lines")
