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
cases = []

missing = ready_context()
missing.pop("recovery_engine")
cases.append(missing)

dashboard_absent = ready_context()
dashboard_absent.pop("developmental_dashboard")
cases.append(dashboard_absent)

html_absent = ready_context()
html_absent["developmental_dashboard"]["exports"]["html"] = ""
cases.append(html_absent)

bad_hash = ready_context()
bad_hash["developmental_stage_classifier"]["stage_hash"] = "bad"
cases.append(bad_hash)

low_quality = ready_context()
low_quality["developmental_dashboard"]["quality"]["overall_quality_score"] = 0.2
cases.append(low_quality)

guard_violation = ready_context()
guard_violation["developmental_dashboard"]["phenomenology_proven"] = True
cases.append(guard_violation)

incoherent = ready_context()
incoherent["developmental_dashboard"]["predicted_stage"] = "DEGENERATION"
cases.append(incoherent)

for case in cases:
    result = engine.step(inputs=case, persist=False)
    assert result["certified"] is False
    assert result["certification_status"] == "CONSCIOUSNESS_DEVELOPMENT_MODEL_INCOMPLETE"
    assert result["missing_conditions"]
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True

print("AV10_DEGRADATION_OK")
