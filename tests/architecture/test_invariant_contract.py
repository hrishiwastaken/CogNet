"""Starter architecture-contract tests.

These tests become active as the implementation appears.
They intentionally skip when the corresponding module does not yet exist.
"""
from pathlib import Path
import ast
import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

PROVIDERS = ("anthropic", "openai", "cohere", "mistralai")

def test_core_has_no_provider_sdk_imports():
    core = SRC / "cognet" / "core"
    if not core.exists():
        pytest.skip("core package not implemented yet")
    violations = []
    for py in core.rglob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(PROVIDERS):
                        violations.append((py, alias.name))
            if module and module.startswith(PROVIDERS):
                violations.append((py, module))
    assert not violations, f"Provider SDK imports leaked into core: {violations}"

def test_spec_files_exist():
    required = [
        "docs/INVARIANTS.md",
        "docs/ARCHITECTURE.md",
        "docs/MEMORY_IR.md",
        "docs/DECISIONS.md",
        "docs/PHASE_PLAN.md",
        "docs/PHASE_GATES.md",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    assert not missing, f"Missing architecture files: {missing}"
