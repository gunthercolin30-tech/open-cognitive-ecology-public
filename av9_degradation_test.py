#!/usr/bin/env python3
from ontology.developmental_dashboard import DevelopmentalDashboard

engine = DevelopmentalDashboard()

cases = [
    {},
    {"developmental_stage_classifier": []},
    {"developmental_prediction_engine": "bad"},
    {
        "developmental_stage_classifier": {
            "developmental_stage": "<script>alert('x')</script>",
            "stage_confidence": float("nan"),
        },
        "developmental_prediction_engine": {
            "predicted_stage": "<img src=x onerror=alert(1)>",
            "prediction_uncertainty": float("inf"),
            "alternative_scenarios": "bad",
        },
        "timeline": [None, "bad", {"stage": "<b>unsafe</b>"}],
    },
]

for case in cases:
    r = engine.step(inputs=case, persist=False)
    assert r["dashboard_status"] in {
        "DEVELOPMENTAL_DASHBOARD_READY",
        "DEVELOPMENTAL_DASHBOARD_INCOMPLETE",
    }
    assert r["exports"]["html"].startswith("<!doctype html>")
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False

unsafe = engine.step(inputs=cases[-1], persist=False)
assert "<script>alert('x')</script>" not in unsafe["exports"]["html"]
assert "&lt;script&gt;" in unsafe["exports"]["html"]
assert "<img src=x onerror=alert(1)>" not in unsafe["exports"]["html"]

print("AV9_DEGRADATION_OK")
