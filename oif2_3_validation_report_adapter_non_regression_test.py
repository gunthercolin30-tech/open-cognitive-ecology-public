from __future__ import annotations

import ast
from pathlib import Path

from oif1_renderer_call_policy import renderer_policy_findings

ROOT = Path.home() / "open-cognitive-ecology"


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            result.add(func.id)
        elif isinstance(func, ast.Attribute):
            result.add(func.attr)
    return result


def main() -> int:
    adapter = ROOT / "oif/adapters/validation_report_adapter.py"
    composition = ROOT / "oif/application/default_providers.py"
    renderer = ROOT / "oif/ui/operational_shell.py"
    legacy = ROOT / "oif/ui/review_app.py"

    for path in (adapter, composition, renderer, legacy):
        assert path.is_file(), path

    adapter_imports = imports(adapter)
    composition_imports = imports(composition)
    assert not any(name == "nicegui" or name.startswith("nicegui.") for name in adapter_imports)
    assert not any(name == "nicegui" or name.startswith("nicegui.") for name in composition_imports)
    assert "subprocess" not in adapter_imports
    assert "subprocess" not in composition_imports
    assert renderer_policy_findings(renderer) == []

    renderer_source = renderer.read_text(encoding="utf-8")
    assert "build_default_provider_specs" in renderer_source
    assert "ValidationReportAdapter" not in renderer_source
    assert "scientific_validation_report.json" not in renderer_source
    assert "read_text" not in calls(renderer)
    assert "read_bytes" not in calls(renderer)
    assert "open" not in calls(renderer)

    legacy_source = legacy.read_text(encoding="utf-8")
    assert "OIFReviewCampaignService" in legacy_source
    assert "from nicegui import ui" in legacy_source

    inventory = (ROOT / "ontology_inventory.txt").read_text(encoding="utf-8")
    assert inventory.splitlines().count("oif2_validation_report_adapter") == 1

    registry = (ROOT / "dependency_registry.py").read_text(encoding="utf-8")
    assert registry.count("# OIF2-3 validation adapter dependency registration") == 1

    print("OIF2_3_VALIDATION_REPORT_ADAPTER_NON_REGRESSION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
