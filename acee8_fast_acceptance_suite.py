\
from __future__ import annotations
import py_compile, tempfile
from pathlib import Path
from ontology.acee_impact_evaluator import AceeImpactEvaluator

def context():
    return {
        "evaluation_id": "impact-001",
        "timestamp_utc": "2026-07-13T20:00:00Z",
        "cycle_id": "cycle-001",
        "before": {
            "validation": {"error_count": 0, "modules_discovered": 1200, "active_primitives": 1100, "validation_passed": True},
            "stability_score": 0.90, "governance_score": 0.91,
            "evolution_score": 0.70, "closure_pressure": 0.20, "runtime_score": 0.89,
        },
        "after": {
            "validation": {"error_count": 0, "modules_discovered": 1201, "active_primitives": 1101, "validation_passed": True, "validation_id": "validation-001"},
            "stability_score": 0.92, "governance_score": 0.93,
            "evolution_score": 0.76, "closure_pressure": 0.17, "runtime_score": 0.91,
        },
    }

def main():
    with tempfile.TemporaryDirectory() as td:
        py_compile.compile("ontology/acee_impact_evaluator.py", cfile=str(Path(td)/"x.pyc"), doraise=True)
    result = AceeImpactEvaluator(root=Path("/nonexistent")).step(inputs=context(), persist=False)
    assert result["impact_status"] == "ACEE_IMPACT_EVALUATED"
    assert result["comparison_valid"] is True and result["impact_score"] > 0
    assert result["rollback_recommended"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    print("ACEE8_FAST_ACCEPTANCE_OK")

if __name__ == "__main__": main()
