\
from __future__ import annotations

from ontology.multi_rf_registry import MultiRFRegistry

READY_OR_SYNTHETIC_CONTEXT = {
    "rf_records": [
        {
            "rf_id": "RF-LOCK-A",
            "display_name": "AW1 Lock A",
            "status": "ACTIVE",
            "origin": "synthetic",
            "synthetic": True,
            "lineage_id": "LINEAGE-LOCK-A",
            "individual_id": "INDIVIDUAL-LOCK-A",
            "aliases": ["lock-a"],
            "node_ids": ["NODE-LOCK"],
        },
        {
            "rf_id": "RF-LOCK-B",
            "display_name": "AW1 Lock B",
            "status": "ACTIVE",
            "origin": "synthetic",
            "synthetic": True,
            "lineage_id": "LINEAGE-LOCK-B",
            "individual_id": "INDIVIDUAL-LOCK-B",
            "aliases": ["lock-b"],
            "node_ids": ["NODE-LOCK"],
        },
    ]
}


def main() -> None:
    result = MultiRFRegistry().step(
        inputs=READY_OR_SYNTHETIC_CONTEXT,
        persist=False,
    )

    assert result["primitive"] == "MULTI_RF_REGISTRY"
    assert result["step"] == "AW1"
    assert result["public_schema_version"] == "1.0"
    assert result["multi_rf_registry_status"] == "MULTI_RF_REGISTRY_READY"
    assert result["multi_rf_registry_ready"] is True
    assert result["registry_count"] == 2
    assert result["unique_rf_id_count"] == 2
    assert result["collision_count"] == 0
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["collective_consciousness_proven"] is False

    print("AW1_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
