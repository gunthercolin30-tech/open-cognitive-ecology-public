from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
Path("/private/tmp").mkdir(parents=True, exist_ok=True)
py_compile.compile(str(ROOT / "ontology" / "theorem_prediction_generator.py"), cfile="/private/tmp/theorem_prediction_generator.pyc", doraise=True)

from ontology.theorem_prediction_generator import TheoremPredictionGenerator

ready_or_synthetic_context = {
    "axis": "AT",
    "step": "AT2",
    "synthetic_context": True,
    "theorems": [
        {"theorem_id": "AT2-SYN-STRUCTURAL", "name": "synthetic structural theorem", "statement": "Functional theorem structure requires observable dependency and guard signatures.", "source": "AT2_fast_acceptance", "epistemic_status": "certified_functional"},
        {"theorem_id": "AT2-SYN-GOVERNANCE", "name": "synthetic governance continuity theorem", "statement": "Governance continuity requires dynamic regression and recovery observables.", "source": "AT2_fast_acceptance", "epistemic_status": "certified_functional"},
    ],
}

r = TheoremPredictionGenerator().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "THEOREM_PREDICTION_GENERATOR"
assert r["step"] == "AT2"
assert r["status"] == "THEOREM_PREDICTION_GENERATOR_READY"
assert r["theorem_prediction_generator_status"] == "THEOREM_PREDICTION_GENERATOR_READY"
assert r["generator_ready"] is True
assert r["theorem_count"] >= 2
assert r["prediction_count"] >= r["theorem_count"]
assert isinstance(r["theorem_predictions"], list) and r["theorem_predictions"]
assert isinstance(r["generated_prediction_categories"], list) and r["generated_prediction_categories"]
assert r["metrics"]["observable_completion_ratio"] == 1.0
assert r["prediction_generation_policy"]["epistemic_scope"] == "functional_only"
assert r["validation_policy"]["replication_required"] is True
assert r["falsification_policy"]["refutable"] is True
assert r["epistemic_guards"]["functional_conclusion_only"] is True
assert r["epistemic_guards"]["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
assert r["persisted"] is False

degraded = TheoremPredictionGenerator().step(inputs={"synthetic_context": True, "theorems": []}, persist=False)
assert degraded["consciousness_proven"] is False
assert degraded["qualia_proven"] is False
assert degraded["subjectivity_proven"] is False
assert degraded["phenomenology_proven"] is False
assert degraded["phenomenology_undetermined"] is True
assert degraded["functional_conclusion_only"] is True
assert degraded["prediction_count"] >= 1

print("AT2_FAST_ACCEPTANCE_ALL_OK")
