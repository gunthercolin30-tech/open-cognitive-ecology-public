from pathlib import Path
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager
r=AceeAutonomousCycleManager(root=Path("/nonexistent")).step(inputs={},persist=False)
assert r["cycle_status"]=="ACEE_AUTONOMOUS_CYCLE_DEGRADED" and r["cycle_complete"] is False
assert "governance_not_approved" in r["blocking_reasons"] and "constitutional_not_approved" in r["blocking_reasons"]
assert r["execution_dispatched"] is False
print("ACEE4_DEGRADATION_OK")
