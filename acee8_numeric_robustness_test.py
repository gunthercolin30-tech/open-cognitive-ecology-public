\
from copy import deepcopy
from pathlib import Path
from acee8_fast_acceptance_suite import context
from ontology.acee_impact_evaluator import AceeImpactEvaluator
for bad in (float("nan"), float("inf"), -1.0, "not-a-number"):
    data = deepcopy(context()); data["after"]["runtime_score"] = bad
    r = AceeImpactEvaluator(root=Path("/nonexistent")).step(inputs=data, persist=False)
    assert "runtime_score" in r["invalid_metrics"] and r["comparison_valid"] is False
print("ACEE8_NUMERIC_ROBUSTNESS_OK")
