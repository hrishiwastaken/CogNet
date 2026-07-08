from pathlib import Path
import ast
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

PROVIDER_PREFIXES = {
    "anthropic", "openai", "google.generativeai", "google.genai",
    "cohere", "mistralai"
}

errors = []

def imported_modules(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path}: cannot parse: {exc}")
        return []
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.append(node.module)
    return mods

core = SRC / "cognet" / "core"
if core.exists():
    for py in core.rglob("*.py"):
        for mod in imported_modules(py):
            if any(mod == p or mod.startswith(p + ".") for p in PROVIDER_PREFIXES):
                errors.append(
                    f"{py.relative_to(ROOT)} imports provider SDK '{mod}' "
                    "(violates provider independence)"
                )

# Heuristic guard: direct CAUSES promotion text near CO_ACTIVATED_WITH in core code.
if SRC.exists():
    for py in SRC.rglob("*.py"):
        text = py.read_text(encoding="utf-8", errors="ignore")
        if "CO_ACTIVATED_WITH" in text and "CAUSES" in text:
            # Not automatically a violation, but require explicit review marker.
            if "CAUSAL_ADMISSION_REVIEWED" not in text:
                errors.append(
                    f"{py.relative_to(ROOT)} mentions CO_ACTIVATED_WITH and CAUSES "
                    "without CAUSAL_ADMISSION_REVIEWED marker; review causal admission."
                )

if errors:
    print("Architecture check FAILED:")
    for e in errors:
        print(f" - {e}")
    sys.exit(1)

print("Architecture check passed.")
