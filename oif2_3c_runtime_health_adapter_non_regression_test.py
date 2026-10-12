from __future__ import annotations

import ast
import hashlib
import tempfile
from pathlib import Path

from oif.adapters.runtime_health_adapter import RuntimeHealthAdapter

ROOT = Path.home() / "open-cognitive-ecology"


def digest_tree(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[str(path.relative_to(root))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return result


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            values.add(node.module)
    return values


def main() -> int:
    adapter_path = ROOT / "oif/adapters/runtime_health_adapter.py"
    composition_path = ROOT / "oif/application/default_providers.py"
    renderer_path = ROOT / "oif/ui/operational_shell.py"

    assert adapter_path.is_file()
    assert "subprocess" not in imports(adapter_path)
    assert "nicegui" not in imports(adapter_path)
    assert "nicegui" not in imports(composition_path)

    renderer_source = renderer_path.read_text(encoding="utf-8")
    assert "RuntimeHealthAdapter" not in renderer_source
    assert "service_state.json" not in renderer_source
    assert "latest_hardware_health_monitor.json" not in renderer_source

    with tempfile.TemporaryDirectory(prefix="oif2_3c_immutable_") as tmp:
        root = Path(tmp)
        source = root / "runtime_service/service_state.json"
        source.parent.mkdir(parents=True)
        source.write_text('{"status":"running"}', encoding="utf-8")
        before = digest_tree(root)
        RuntimeHealthAdapter(root=root).read()
        after = digest_tree(root)
        assert before == after

    inventory = (
        ROOT / "ontology_inventory.txt"
    ).read_text(encoding="utf-8").splitlines()
    assert inventory.count("oif2_runtime_health_adapter") == 1

    registry = (
        ROOT / "dependency_registry.py"
    ).read_text(encoding="utf-8")
    assert registry.count(
        "# OIF2-3C runtime health adapter dependency registration"
    ) == 1

    print("OIF2_3C_RUNTIME_HEALTH_ADAPTER_NON_REGRESSION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
