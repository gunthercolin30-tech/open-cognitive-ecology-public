#!/usr/bin/env python3
from pathlib import Path
import py_compile
from ontology.developmental_certifier import DevelopmentalCertifier

ROOT = Path.home() / "open-cognitive-ecology"
py_compile.compile(
    str(ROOT / "ontology" / "developmental_certifier.py"),
    cfile="/private/tmp/developmental_certifier.pyc",
    doraise=True,
)


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
ready = engine.step(inputs=ready_context(), persist=False)
assert ready["certification_status"] == "CONSCIOUSNESS_DEVELOPMENT_MODEL_COMPLETE"
assert ready["certified"] is True
assert ready["certification_score"] == 1.0
assert ready["module_completeness"] == 1.0
assert ready["coherence_status"] == "COHERENT"
assert ready["quality_status"] == "QUALITY_SUFFICIENT"
assert ready["guard_status"] == "GUARDS_PRESERVED"
assert ready["hash_status"] == "HASHES_VALID"
assert ready["export_status"] == "EXPORTS_VALID"
assert len(ready["certification_hash"]) == 64

missing = ready_context()
missing.pop("developmental_dashboard")
r_missing = engine.step(inputs=missing, persist=False)
assert r_missing["certified"] is False

guard = ready_context()
guard["developmental_prediction_engine"]["consciousness_proven"] = True
r_guard = engine.step(inputs=guard, persist=False)
assert r_guard["guard_status"] == "GUARD_VIOLATION"
assert r_guard["certified"] is False

for result in (ready, r_missing, r_guard):
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True

print("AV10_FAST_ACCEPTANCE_OK")
