"""Protect dependency direction for the new contracts and pure models."""

import ast
from pathlib import Path


def test_domain_and_application_do_not_import_frameworks_or_infrastructure() -> None:
    source = Path(__file__).resolve().parents[2] / "src"
    forbidden = (
        "fastapi",
        "pydantic",
        "sqlalchemy",
        "src.infrastructure",
        "src.core",
    )
    violations: list[str] = []
    for layer in ("domain", "use_cases"):
        for path in (source / layer).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                modules: list[str] = []
                if isinstance(node, ast.ImportFrom) and node.module:
                    modules.append(node.module)
                elif isinstance(node, ast.Import):
                    modules.extend(item.name for item in node.names)
                for module in modules:
                    if any(
                        module == item or module.startswith(item + ".")
                        for item in forbidden
                    ):
                        violations.append(f"{path.name}: {module}")
    assert not violations, violations
