\
from __future__ import annotations

import json
import py_compile
import tempfile
from pathlib import Path

from ontology.multi_rf_registry import MultiRFRegistry

ROOT = Path.home() / "open-cognitive-ecology"


def main() -> None:
    for path in [
        ROOT / "ontology/multi_rf_registry.py",
        ROOT / "aw1_fast_acceptance_suite.py",
        ROOT / "multi_rf_registry_final_lock.py",
    ]:
        py_compile.compile(
            str(path),
            cfile=str(Path("/private/tmp") / (path.name + ".aw1.pyc")),
            doraise=True,
        )

    inputs = {
        "rf_records": [
            {
                "rf_id": "RF-ALPHA",
                "display_name": "Alpha",
                "status": "ACTIVE",
                "origin": "synthetic",
                "synthetic": True,
                "lineage_id": "LINEAGE-ALPHA",
                "individual_id": "INDIVIDUAL-ALPHA",
                "node_ids": ["NODE-1"],
                "aliases": ["alpha"],
                "evidence_refs": ["AW0"],
            },
            {
                "rf_id": "RF-BETA",
                "display_name": "Beta",
                "status": "ACTIVE",
                "origin": "synthetic",
                "synthetic": True,
                "lineage_id": "LINEAGE-BETA",
                "individual_id": "INDIVIDUAL-BETA",
                "node_ids": ["NODE-2"],
                "aliases": ["beta"],
                "evidence_refs": ["AW0"],
            },
        ]
    }

    first = MultiRFRegistry().step(inputs=inputs, persist=False)
    second = MultiRFRegistry().step(inputs=inputs, persist=False)

    assert first["multi_rf_registry_status"] == "MULTI_RF_REGISTRY_READY"
    assert first["multi_rf_registry_ready"] is True
    assert first["registry_count"] == 2
    assert first["active_rf_count"] == 2
    assert first["unique_rf_id_count"] == 2
    assert first["multi_rf_population"] is True
    assert first["collision_count"] == 0
    assert first["alias_conflict_count"] == 0
    assert first["registry_hash"] == second["registry_hash"]
    assert first["contract_hash"] == second["contract_hash"]
    assert first["registry"] == second["registry"]

    with tempfile.TemporaryDirectory(prefix="oce_aw1_") as tmp:
        registry = MultiRFRegistry(root=Path(tmp))
        persisted = registry.step(inputs=inputs, persist=True)
        assert persisted["persisted"] is True
        path = Path(persisted["output_path"])
        assert path.exists()
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["registry_hash"] == persisted["registry_hash"]

        restored = registry.step(
            inputs={"load_existing": True},
            persist=False,
        )
        assert restored["registry_hash"] == persisted["registry_hash"]
        assert restored["registry_count"] == 2

    for payload in [first, second]:
        assert payload["functional_conclusion_only"] is True
        assert payload["phenomenology_undetermined"] is True
        assert payload["consciousness_proven"] is False
        assert payload["qualia_proven"] is False
        assert payload["subjectivity_proven"] is False
        assert payload["phenomenology_proven"] is False
        assert payload["collective_consciousness_proven"] is False
        assert payload["collective_subjectivity_proven"] is False
        assert payload["collective_qualia_proven"] is False
        assert payload["collective_phenomenology_proven"] is False

    print("AW1_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
