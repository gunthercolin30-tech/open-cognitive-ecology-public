from __future__ import annotations

import ast
import hashlib
import tempfile
from pathlib import Path

from oif.adapters.civilizational_state_adapter import CivilizationalStateAdapter

ROOT = Path.home() / "open-cognitive-ecology"


def digest_tree(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*")) if path.is_file()
    }


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def main() -> int:
    adapter = ROOT / "oif/adapters/civilizational_state_adapter.py"
    providers = ROOT / "oif/application/default_providers.py"
    renderer = ROOT / "oif/ui/operational_shell.py"
    assert adapter.is_file()
    assert "subprocess" not in imports(adapter)
    assert "nicegui" not in imports(adapter)
    assert "nicegui" not in imports(providers)
    renderer_source = renderer.read_text(encoding="utf-8")
    assert "CivilizationalStateAdapter" not in renderer_source
    assert "representative_registry.json" not in renderer_source
    with tempfile.TemporaryDirectory(prefix="oif2_3d_immutable_") as tmp:
        root = Path(tmp)
        source = root / "representative_succession/representative_registry.json"
        source.parent.mkdir(parents=True)
        source.write_text('{"current_representative":{}}', encoding="utf-8")
        before = digest_tree(root)
        CivilizationalStateAdapter(root=root).read()
        after = digest_tree(root)
        assert before == after
    inventory = (ROOT / "ontology_inventory.txt").read_text(encoding="utf-8").splitlines()
    assert inventory.count("oif2_civilizational_state_adapter") == 1
    registry = (ROOT / "dependency_registry.py").read_text(encoding="utf-8")
    assert registry.count("# OIF2-3D civilizational state adapter dependency registration") == 1
    providers_source = providers.read_text(encoding="utf-8")
    assert providers_source.count('name="civilizational-state"') == 1
    print("OIF2_3D_CIVILIZATIONAL_STATE_ADAPTER_NON_REGRESSION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
