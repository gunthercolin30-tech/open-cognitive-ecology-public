from __future__ import annotations

import ast
from pathlib import Path

from oif.application.shell_service import OIF2ReadOnlyApplicationService
from oif1_renderer_call_policy import renderer_policy_findings

ROOT = Path.home() / "open-cognitive-ecology"


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def main() -> int:
    service_path = ROOT / "oif/application/shell_service.py"
    renderer_path = ROOT / "oif/ui/operational_shell.py"
    legacy_renderer = ROOT / "oif/ui/review_app.py"

    assert service_path.is_file()
    assert renderer_path.is_file()
    assert legacy_renderer.is_file()

    service_imports = imported_modules(service_path)
    assert not any(m == "nicegui" or m.startswith("nicegui.") for m in service_imports)
    assert "subprocess" not in service_imports
    assert renderer_policy_findings(renderer_path) == []

    baseline = OIF2ReadOnlyApplicationService().snapshot()
    second = OIF2ReadOnlyApplicationService().snapshot()
    assert baseline == second
    assert baseline["provider_count"] == 0
    assert set(baseline["zones"]) >= {
        "overview", "runtime", "experiments", "science",
        "memory", "governance", "system",
    }

    legacy_source = legacy_renderer.read_text(encoding="utf-8")
    assert "OIFReviewCampaignService" in legacy_source
    assert "from nicegui import ui" in legacy_source

    print("OIF2_2_READ_ONLY_SHELL_NON_REGRESSION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
