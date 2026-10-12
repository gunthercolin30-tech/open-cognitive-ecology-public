#!/usr/bin/env python3
from copy import deepcopy
from ontology.developmental_prediction_engine import DevelopmentalPredictionEngine

E = DevelopmentalPredictionEngine()
source = {
    "developmental_stage_result": {
        "developmental_stage": "SPECIALIZATION",
        "stage_confidence": .88,
        "evidence_quality_score": .92,
        "stage_probabilities": {"SPECIALIZATION": .8, "MATURATION": .2},
    },
    "trends": {"stability": .62, "bifurcation": .25},
    "trajectory": [
        {"developmental_stage": "MATURATION", "stage_confidence": .75},
        {"developmental_stage": "SPECIALIZATION", "stage_confidence": .88},
    ],
}
snapshot = deepcopy(source)
a = E.step(source, False)
b = E.step(deepcopy(source), False)
assert source == snapshot
assert a["prediction_hash"] == b["prediction_hash"]
assert a["predicted_stage"] == b["predicted_stage"]
assert a["prediction_probabilities"] == b["prediction_probabilities"]

reordered = {
    "trajectory": deepcopy(source["trajectory"]),
    "trends": {"bifurcation": .25, "stability": .62},
    "developmental_stage_result": {
        "stage_probabilities": {"MATURATION": .2, "SPECIALIZATION": .8},
        "evidence_quality_score": .92,
        "stage_confidence": .88,
        "developmental_stage": "SPECIALIZATION",
    },
}
c = E.step(reordered, False)
assert a["prediction_hash"] == c["prediction_hash"]

changed = deepcopy(source)
changed["trends"]["degeneration"] = 1.0
d = E.step(changed, False)
assert d["prediction_hash"] != a["prediction_hash"]
assert d["prediction_probabilities"] != a["prediction_probabilities"]

assert a["audit_trace"]["upstream_recalculation_performed"] is False
print("AV8_NON_REGRESSION_AND_DETERMINISM_OK")
