\
from pathlib import Path
from ontology.acee_capability_map import AceeCapabilityMap


def main():
    result = AceeCapabilityMap(root=Path("/nonexistent")).step(
        inputs={"integration_audit": {"audit_status": "ACEE_INTEGRATION_AUDIT_DEGRADED", "existing_modules": [], "coverage_matrix": {}}, "map_timestamp_utc": "2026-07-13T13:08:00Z"},
        persist=False,
    )
    assert result["capability_map_status"] == "ACEE_CAPABILITY_MAP_DEGRADED"
    assert result["capability_map_ready"] is False
    assert "source_audit_not_complete" in result["degraded_reasons"]
    assert "empty_source_module_inventory" in result["degraded_reasons"]
    assert result["capability_count"] == 21
    assert result["functional_conclusion_only"] is True
    print("ACEE1_DEGRADATION_OK")


if __name__ == "__main__":
    main()
