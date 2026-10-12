\
from pathlib import Path
from acee8_fast_acceptance_suite import context
from ontology.acee_impact_evaluator import AceeImpactEvaluator
r = AceeImpactEvaluator(root=Path("/nonexistent")).step(inputs=context(), persist=False)
assert r["impact_status"] == "ACEE_IMPACT_EVALUATED"
assert set(r["before_metrics"]) == {"error_count", "modules_discovered", "active_primitives", "stability_score", "governance_score", "evolution_score", "closure_pressure", "runtime_score"}
assert r["validation_executed_by_evaluator"] is False
assert r["causal_effect_resolved"] is False
assert r["selection_decision_made"] is False
assert r["rollback_executed"] is False
assert all(r[k] is False for k in ("consciousness_proven", "subjectivity_proven", "qualia_proven", "phenomenology_proven"))
print("ACEE_IMPACT_EVALUATOR_FINAL_LOCK_OK")
