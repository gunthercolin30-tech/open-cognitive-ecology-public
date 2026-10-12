from __future__ import annotations

import ast
import hashlib
import importlib
import json
import py_compile
import stat
from pathlib import Path

from oif1_renderer_call_policy import renderer_policy_findings

LOCK_VERSION = "oif1-extended-validation-final-lock-v2"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def main() -> None:
    root = Path.home() / "open-cognitive-ecology"
    constitution_path = root / "oif_functional_constitution.py"
    compliance_path = root / "oif_nicegui_compliance.py"
    report_path = root / "oif1_refinement_report.json"
    policy_path = root / "oif1_renderer_call_policy.py"

    for path in (constitution_path, compliance_path, report_path, policy_path):
        assert path.is_file(), "missing required OIF-1 artifact: %s" % path

    for path in root.glob("oif_functional_constitution*.py"):
        py_compile.compile(str(path), doraise=True)
    for path in (compliance_path, policy_path):
        py_compile.compile(str(path), doraise=True)

    constitution_imports = imports_from(constitution_path)
    assert not any(name == "nicegui" or name.startswith("nicegui.") for name in constitution_imports)

    constitution = importlib.import_module("oif_functional_constitution")
    invariants = dict(getattr(constitution, "EPISTEMIC_INVARIANTS"))
    expected = {
        "consciousness_proven": False,
        "subjectivity_proven": False,
        "qualia_proven": False,
        "phenomenology_proven": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }
    assert invariants == expected

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report.get("error_count") == 0
    assert report.get("ontology_inventory_checked") is True
    assert report.get("renderer_ast_valid") is True
    assert report.get("service_ast_valid") is True
    for relative, expected_hash in report["target_sha256"].items():
        path = root / relative
        assert path.is_file(), "missing hashed artifact: %s" % relative
        assert sha256(path) == expected_hash, "hash mismatch: %s" % relative

    protected = sorted(set([constitution_path, compliance_path, policy_path] + list(root.glob("oif_functional_constitution*.py"))))
    for path in protected:
        assert not path.is_symlink(), "symlink forbidden: %s" % path
        mode = stat.S_IMODE(path.stat().st_mode)
        assert not (mode & stat.S_IWOTH), "world-writable file: %s" % path

    renderer_candidates = []
    ui_dir = root / "oif" / "ui"
    if ui_dir.is_dir():
        for path in sorted(ui_dir.glob("*.py")):
            lower = path.name.lower()
            if any(token in lower for token in ("app", "view", "page", "renderer")):
                renderer_candidates.append(path)
    assert renderer_candidates, "no renderer candidate found"

    renderer_findings = {
        str(path.relative_to(root)): renderer_policy_findings(path)
        for path in renderer_candidates
    }
    renderer_findings = {name: values for name, values in renderer_findings.items() if values}
    assert not renderer_findings, renderer_findings

    review_app = root / "oif" / "ui" / "review_app.py"
    review_source = review_app.read_text(encoding="utf-8")
    assert "ui.run(" in review_source, "NiceGUI lifecycle entry point missing"

    service_path = root / "oif" / "ui" / "campaign_service.py"
    if service_path.is_file():
        service_source = service_path.read_text(encoding="utf-8")
        assert "os.replace" in service_source
        assert "os.fsync" in service_source

    print("OIF1_EXTENDED_COMPILATION_OK")
    print("OIF1_NO_NICEGUI_DEPENDENCY_OK")
    print("OIF1_EPISTEMIC_INVARIANTS_OK")
    print("OIF1_REFINEMENT_REPORT_INTEGRITY_OK")
    print("OIF1_NICEGUI_UI_RUN_ALLOWED_OK")
    print("OIF1_RENDERER_NO_DIRECT_WRITE_OK")
    print("OIF1_RENDERER_NO_ARBITRARY_EXECUTION_OK")
    print("OIF1_FILE_SAFETY_OK")
    print("OIF1_EXTENDED_VALIDATION_FINAL_LOCK_OK")
    print(json.dumps({
        "lock_version": LOCK_VERSION,
        "renderer_files_checked": [str(p.relative_to(root)) for p in renderer_candidates],
        "protected_file_count": len(protected),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
