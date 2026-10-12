from __future__ import annotations

import hashlib
import json
from pathlib import Path

from oif.audit.active_interface_auditor import OIFActiveInterfaceAuditor, STATUS


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((root / "ontology").glob("*.py"), key=lambda p: p.name):
        digest.update(path.name.encode("utf-8"))
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def main() -> None:
    root = Path.home() / "open-cognitive-ecology"
    before = tree_hash(root)
    auditor = OIFActiveInterfaceAuditor(root)
    dry_a = auditor.step(inputs={}, persist=False)
    dry_b = auditor.step(inputs={}, persist=False)
    assert dry_a["source_fingerprint"] == dry_b["source_fingerprint"]
    result = auditor.step(inputs={"persist": True})
    after = tree_hash(root)
    assert before == after, "ontology sources changed during read-only audit"
    assert result["status"] == STATUS
    assert result["success"] is True
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    output = Path(result["output_dir"])
    required = {
        "oif_active_interface_inventory.json",
        "oif_dependency_map.json",
        "oif_redundancy_report.json",
        "oif_persistence_boundary_report.json",
        "oif_gate_map.json",
        "oif_representative_entrypoint_map.json",
        "oif_baseline_report.md",
        "oif_baseline_manifest.sha256",
    }
    assert required.issubset({p.name for p in output.iterdir() if p.is_file()})
    print(STATUS)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
