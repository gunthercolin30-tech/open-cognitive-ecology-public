\
from pathlib import Path
from ontology.acee_impact_evaluator import AceeImpactEvaluator
before = {
 "cycle": {"cycle_id": "cycle-7", "cycle_score": 0.80, "closure_pressure": 0.25},
 "validation": {"validation_id": "v-before", "error_count": 0, "modules_discovered": 1200, "active_primitives": 1100, "validation_passed": True},
 "stability_score": 0.88, "governance_consistency_score": 0.90, "effectiveness_score": 0.70, "global_viability_score": 0.89,
}
after = {
 "cycle": {"cycle_id": "cycle-8", "cycle_score": 0.84, "closure_pressure": 0.20},
 "validation": {"validation_id": "v-after", "error_count": 0, "modules_discovered": 1201, "active_primitives": 1101, "validation_passed": True},
 "overall_stability_score": 0.91, "constitutional_integrity_index": 0.93, "improvement_score": 0.77, "runtime_health_score": 0.92,
}
r = AceeImpactEvaluator(root=Path("/nonexistent")).step(inputs={"evaluation_id": "integration", "cycle_id": "cycle-8", "before": before, "after": after}, persist=False)
assert r["comparison_valid"] is True
assert r["source_ids"]["cycle_id"] == "cycle-8"
assert r["source_ids"]["validation_id"] == "v-after"
assert r["rollback_executed"] is False
print("ACEE8_ACEE4_ACEE7_ACEE11_INTEGRATION_OK")
