\
from acee3_fast_acceptance_suite import SAMPLES
from ontology.acee_bridge_adapter import AceeBridgeAdapter

result = AceeBridgeAdapter().step(
    inputs={
        "source_module": "evolution_sandbox",
        "source_result": SAMPLES["evolution_sandbox"],
        "adapter_timestamp_utc": "2026-07-13T15:41:00Z",
    },
    persist=False,
)
assert result["adapter_status"] == "ACEE_BRIDGE_ADAPTER_READY"
assert result["adapter_ready"] is True
assert result["status"] == "approved"
assert result["accepted"] is True
assert result["executed"] is not True
assert result["rollback_required"] is False
assert result["rollback_performed"] is not True
assert result["raw_result"] == SAMPLES["evolution_sandbox"]
assert result["normalization_complete"] is True
assert 0.0 <= result["normalization_confidence"] <= 1.0
assert result["consciousness_proven"] is False
assert result["collective_consciousness_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("ACEE_BRIDGE_ADAPTER_FINAL_LOCK_OK")
