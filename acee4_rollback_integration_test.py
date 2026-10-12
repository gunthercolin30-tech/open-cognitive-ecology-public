from pathlib import Path
from acee4_fast_acceptance_suite import context
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager
c=context(); c["phase_results"]["validation"]={"status":"failed","score":0.1}; c["phase_results"]["selection"]={"status":"completed","decision":"rollback","score":0.9}; c["phase_results"]["rollback_or_acceptance"]={"status":"completed","rollback_performed":True,"score":1.0}
r=AceeAutonomousCycleManager(root=Path("/nonexistent")).step(inputs=c,persist=False)
assert r["rollback_required"] is True and r["rollback_completed"] is True and r["rollback_executed_by_manager"] is False
assert r["cycle_outcome"]=="rolled_back"
print("ACEE4_ROLLBACK_INTEGRATION_OK")
