\
from copy import deepcopy
from pathlib import Path
from acee8_fast_acceptance_suite import context
from ontology.acee_impact_evaluator import AceeImpactEvaluator
base = context()
r1 = AceeImpactEvaluator(root=Path("/nonexistent")).step(inputs=base, persist=False)
degraded = deepcopy(base)
degraded["after"]["validation"]["error_count"] = 2
degraded["after"]["stability_score"] = 0.80
degraded["after"]["governance_score"] = 0.85
degraded["after"]["closure_pressure"] = 0.35
r2 = AceeImpactEvaluator(root=Path("/nonexistent")).step(inputs=degraded, persist=False)
assert r1["rollback_recommended"] is False
assert r2["rollback_recommended"] is True
assert {"error_count_increased", "stability_regression", "governance_regression", "closure_pressure_increase"}.issubset(set(r2["rollback_trigger_reasons"]))
assert r2["rollback_executed"] is False
print("ACEE8_NON_REGRESSION_OK")
