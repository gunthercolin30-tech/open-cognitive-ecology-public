from copy import deepcopy
from pathlib import Path
from acee4_fast_acceptance_suite import context
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager
c=context(); c["requested_phases"]=["diagnostic","snapshot"]
r=AceeAutonomousCycleManager(root=Path("/nonexistent")).step(inputs=c,persist=False)
assert "phase_order_invalid" in r["blocking_reasons"] and r["cycle_complete"] is False
u=context(); u["requested_phases"]=["snapshot","bogus"]
r=AceeAutonomousCycleManager(root=Path("/nonexistent")).step(inputs=u,persist=False)
assert any(x.startswith("unknown_phases:") for x in r["blocking_reasons"])
print("ACEE4_PHASE_ORDER_OK")
