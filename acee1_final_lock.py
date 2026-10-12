\
from acee1_fast_acceptance_suite import build_audit
from ontology.acee_capability_map import AceeCapabilityMap

result = AceeCapabilityMap().step(
    inputs={"integration_audit": build_audit(), "map_timestamp_utc": "2026-07-13T13:02:00Z"},
    persist=False,
)
assert result["capability_map_status"] == "ACEE_CAPABILITY_MAP_READY"
assert result["capability_map_ready"] is True
assert result["capability_count"] == 21
assert result["deferred_capabilities"] == ["ACEE5", "ACEE6"]
assert result["capability_matrix"]["ACEE1"]["coverage_level"] == "covered"
assert all(item["justification"] for item in result["recommended_actions"])
assert result["recommendation_justifications_complete"] is True
assert result["consciousness_proven"] is False
assert result["collective_consciousness_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("ACEE_CAPABILITY_MAP_FINAL_LOCK_OK")
