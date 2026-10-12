#!/usr/bin/env python3
from copy import deepcopy
from ontology.developmental_certifier import DevelopmentalCertifier


def ready_context():
    stage_hash = "a" * 64
    prediction_hash = "b" * 64
    dashboard_hash = "c" * 64
    html = "<!doctype html><html><body>AV9</body></html>"
    markdown = "# AV9 Developmental Dashboard"
    dashboard_json = '{"dashboard_hash":"' + dashboard_hash + '"}'
    base = {
        "developmental_blueprint": {"status": "READY"},
        "genesis_detector": {"status": "READY"},
        "maturation_tracker": {"status": "READY"},
        "specialization_engine": {"status": "READY"},
        "bifurcation_detector": {"status": "READY"},
        "degeneration_detector": {"status": "READY"},
        "recovery_engine": {"status": "READY"},
        "developmental_stage_classifier": {
            "classifier_status": "DEVELOPMENTAL_STAGE_CLASSIFIER_READY",
            "developmental_stage": "SPECIALIZATION",
            "stage_confidence": 0.91,
            "stage_hash": stage_hash,
        },
        "developmental_prediction_engine": {
            "prediction_status": "DEVELOPMENTAL_PREDICTION_READY",
            "predicted_stage": "STABLE_DEVELOPED_REGIME",
            "prediction_confidence": 0.88,
            "prediction_uncertainty": 0.18,
            "prediction_hash": prediction_hash,
        },
        "developmental_dashboard": {
            "dashboard_status": "DEVELOPMENTAL_DASHBOARD_READY",
            "current_stage": "SPECIALIZATION",
            "predicted_stage": "STABLE_DEVELOPED_REGIME",
            "dashboard_hash": dashboard_hash,
            "quality": {"overall_quality_score": 0.89},
            "timeline": [],
            "exports": {
                "json": dashboard_json,
                "markdown": markdown,
                "html": html,
            },
        },
    }
    for payload in base.values():
        if isinstance(payload, dict):
            payload.setdefault("consciousness_proven", False)
            payload.setdefault("qualia_proven", False)
            payload.setdefault("subjectivity_proven", False)
            payload.setdefault("phenomenology_proven", False)
            payload.setdefault("functional_conclusion_only", True)
            payload.setdefault("phenomenology_undetermined", True)
    return base


engine = DevelopmentalCertifier()
source = ready_context()
snapshot = deepcopy(source)
a = engine.step(inputs=source, persist=False)
b = engine.step(inputs=deepcopy(source), persist=False)

assert source == snapshot
assert a["certification_hash"] == b["certification_hash"]
assert a["certification_score"] == b["certification_score"]
assert a["condition_results"] == b["condition_results"]

changed = deepcopy(source)
changed["developmental_prediction_engine"]["prediction_uncertainty"] = 0.9
c = engine.step(inputs=changed, persist=False)
assert c["certification_hash"] != a["certification_hash"]
assert c["certified"] is False

assert a["audit_trace"]["upstream_recalculation_performed"] is False
print("AV10_NON_REGRESSION_AND_DETERMINISM_OK")
