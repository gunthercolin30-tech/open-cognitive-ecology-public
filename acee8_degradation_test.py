\
from pathlib import Path
from ontology.acee_impact_evaluator import AceeImpactEvaluator
r = AceeImpactEvaluator(root=Path("/nonexistent")).step(inputs={"before": {"error_count": 0}, "after": {"error_count": float("nan")}}, persist=False)
assert r["impact_status"] == "ACEE_IMPACT_EVALUATION_DEGRADED"
assert r["comparison_valid"] is False
assert "error_count" in r["invalid_metrics"]
assert "invalid_or_non_finite_metrics" in r["blocking_reasons"]
print("ACEE8_DEGRADATION_OK")
