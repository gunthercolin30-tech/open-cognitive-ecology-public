from pathlib import Path
from ontology.acee_meta_orchestrator import AceeMetaOrchestrator
r=AceeMetaOrchestrator(root=Path("/nonexistent")).step(inputs={},persist=False)
assert r["orchestrator_status"]=="ACEE_META_ORCHESTRATOR_DEGRADED"
assert r["execution_eligible"] is False
assert r["execution_authorized"] is False
assert r["execution_dispatched"] is False
assert "integration_audit_unavailable_or_degraded" in r["blocking_reasons"]
assert "capability_map_unavailable_or_degraded" in r["blocking_reasons"]
assert "normalized_engine_result_unavailable_or_degraded" in r["blocking_reasons"]
print("ACEE2_DEGRADATION_OK")
