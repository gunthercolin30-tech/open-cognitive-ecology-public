#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.consciousness_prediction_engine import ConsciousnessPredictionEngine

ROOT = Path.home() / "open-cognitive-ecology"
py_compile.compile(str(ROOT / "ontology" / "consciousness_prediction_engine.py"), cfile="/private/tmp/consciousness_prediction_engine.pyc", doraise=True)

ready_context = {
    "confidence": {"confidence": 0.86},
    "stability": {"stability_index": 0.84, "regression_rate": 0.05, "recovery_rate": 0.35, "hazard_rate": 0.04, "survival_time": 100.0, "mean_duration": 25.0},
    "dependency": {"green_ratio": 0.82, "orange_ratio": 0.14, "red_ratio": 0.04, "node_count": 19},
    "dashboard": {"cri": 0.88, "current_state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED"},
}

r = ConsciousnessPredictionEngine().step(inputs=ready_context, persist=False)
assert r["primitive"] == "CONSCIOUSNESS_PREDICTION_ENGINE"
assert r["step"] == "AS18"
assert r["prediction_engine_status"] == "CONSCIOUSNESS_PREDICTION_ENGINE_READY"
assert 0.0 <= r["probability_reach_status"] <= 1.0
assert 0.0 <= r["probability_lose_status"] <= 1.0
assert 0.0 <= r["net_stability_forecast"] <= 1.0
assert r["probability_reach_status"] > r["probability_lose_status"]
assert isinstance(r["prediction_hash"], str) and len(r["prediction_hash"]) == 64
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

fragile_context = {
    "confidence": {"confidence": 0.35},
    "stability": {"stability_index": 0.28, "regression_rate": 0.55, "recovery_rate": 0.0, "hazard_rate": 0.45},
    "dependency": {"green_ratio": 0.25, "red_ratio": 0.45, "node_count": 19},
    "dashboard": {"cri": 0.40, "current_state": "NOT_EVALUATED"},
}
rf = ConsciousnessPredictionEngine().step(inputs=fragile_context, persist=False)
assert rf["probability_lose_status"] > rf["probability_reach_status"]
assert "FRAGILE" in rf["prediction_class"]
assert rf["missing_conditions"]

print("AS18_FAST_ACCEPTANCE_ALL_OK")
