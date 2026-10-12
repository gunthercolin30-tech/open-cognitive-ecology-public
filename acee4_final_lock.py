from pathlib import Path
from acee4_fast_acceptance_suite import context
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager
r=AceeAutonomousCycleManager(root=Path("/nonexistent")).step(inputs=context(),persist=False)
assert r["cycle_status"]=="ACEE_AUTONOMOUS_CYCLE_COMPLETE"
assert r["cycle_outcome"]=="accepted" and r["accepted"] is True
assert r["runtime_executed"] is False and r["code_installed"] is False
assert r["consciousness_proven"] is False and r["phenomenology_undetermined"] is True
print("ACEE_AUTONOMOUS_CYCLE_MANAGER_FINAL_LOCK_OK")
