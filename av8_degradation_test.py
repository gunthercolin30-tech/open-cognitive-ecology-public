#!/usr/bin/env python3
from ontology.developmental_prediction_engine import DevelopmentalPredictionEngine

E = DevelopmentalPredictionEngine()

cases = [
    {},
    {"developmental_stage_result": []},
    {"developmental_stage": "UNKNOWN"},
    {
        "developmental_stage_result": {
            "developmental_stage": "HYBRID_STAGE",
            "stage_confidence": "bad",
            "evidence_quality_score": float("nan"),
        },
        "trends": {"growth": float("inf"), "degeneration": -999},
        "trajectory": "bad",
    },
]

for case in cases:
    result = E.step(case, False)
    assert result["predicted_stage"] in E.STAGES
    assert 0.0 <= result["prediction_confidence"] <= 1.0
    assert 0.0 <= result["prediction_uncertainty"] <= 1.0
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False

missing = E.step({}, False)
assert missing["predicted_stage"] == "UNDETERMINED"
assert "missing_or_undetermined_AV7_stage" in missing["warnings"]

print("AV8_DEGRADATION_OK")
