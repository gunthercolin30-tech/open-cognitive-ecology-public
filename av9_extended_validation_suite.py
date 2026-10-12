#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path

from ontology.developmental_dashboard import DevelopmentalDashboard


def guards(result: dict) -> None:
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True


def ready_context() -> dict:
    return {
        "developmental_blueprint": {
            "developmental_blueprint_status": "DEVELOPMENTAL_BLUEPRINT_READY",
        },
        "genesis_detector": {
            "genesis_detector_status": "GENESIS_DETECTOR_READY",
        },
        "maturation_tracker": {
            "maturation_tracker_status": "MATURATION_TRACKER_READY",
        },
        "specialization_engine": {
            "specialization_engine_status": "SPECIALIZATION_ENGINE_READY",
        },
        "bifurcation_detector": {
            "bifurcation_detector_status": "BIFURCATION_DETECTOR_READY",
        },
        "degeneration_detector": {
            "degeneration_detector_status": "DEGENERATION_DETECTOR_READY",
        },
        "recovery_engine": {
            "recovery_engine_status": "RECOVERY_ENGINE_READY",
        },
        "developmental_stage_classifier": {
            "classifier_status": "DEVELOPMENTAL_STAGE_CLASSIFIER_READY",
            "developmental_stage": "SPECIALIZATION",
            "stage_confidence": 0.91,
            "evidence_quality_score": 0.94,
            "stage_history": [
                {
                    "developmental_stage": "GENESIS",
                    "timestamp_utc": "2026-01-01T00:00:00Z",
                },
                {
                    "developmental_stage": "MATURATION",
                    "timestamp_utc": "2026-02-01T00:00:00Z",
                },
                {
                    "developmental_stage": "SPECIALIZATION",
                    "timestamp_utc": "2026-03-01T00:00:00Z",
                },
            ],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
        "developmental_prediction_engine": {
            "prediction_status": "DEVELOPMENTAL_PREDICTION_READY",
            "predicted_stage": "STABLE_DEVELOPED_REGIME",
            "prediction_confidence": 0.84,
            "prediction_uncertainty": 0.16,
            "input_quality_score": 0.93,
            "forecast_horizon": {
                "label": "MEDIUM",
                "windows": 3,
            },
            "alternative_scenarios": [
                {
                    "rank": 1,
                    "stage": "STABLE_DEVELOPED_REGIME",
                    "probability": 0.64,
                },
                {
                    "rank": 2,
                    "stage": "BIFURCATION",
                    "probability": 0.21,
                },
                {
                    "rank": 3,
                    "stage": "DEGENERATION",
                    "probability": 0.15,
                },
            ],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
    }


engine = DevelopmentalDashboard()
source = ready_context()
snapshot = deepcopy(source)

# 1. Nominal et non-mutation.
first = engine.step(inputs=source, persist=False)
second = engine.step(inputs=deepcopy(source), persist=False)

assert source == snapshot
assert first["dashboard_status"] == "DEVELOPMENTAL_DASHBOARD_READY"
assert first["developmental_dashboard_ready"] is True
assert first["module_completeness"] == 1.0
assert first["dashboard_hash"] == second["dashboard_hash"]
assert first["exports"] == second["exports"]
assert first["export_integrity"] == second["export_integrity"]
assert first["audit_trace"]["aggregation_only"] is True
assert first["audit_trace"]["upstream_recalculation_performed"] is False
guards(first)
guards(second)

# 2. Intégrité croisée JSON / Markdown / HTML.
json_payload = json.loads(first["exports"]["json"])
assert json_payload["dashboard_hash"] == first["dashboard_hash"]
assert json_payload["current_stage"] == first["current_stage"]
assert json_payload["predicted_stage"] == first["predicted_stage"]
assert json_payload["quality"] == first["quality"]
assert json_payload["timeline"] == first["timeline"]
assert json_payload["alternative_scenarios"] == first["alternative_scenarios"]

markdown = first["exports"]["markdown"]
html_export = first["exports"]["html"]

assert "# AV9 Developmental Dashboard" in markdown
assert first["current_stage"] in markdown
assert first["predicted_stage"] in markdown
assert first["dashboard_hash"] in markdown

assert html_export.startswith("<!doctype html>")
assert "<html>" in html_export
assert "</html>" in html_export
assert "<head>" in html_export
assert "</head>" in html_export
assert "<body>" in html_export
assert "</body>" in html_export
assert first["current_stage"] in html_export
assert first["predicted_stage"] in html_export
assert first["dashboard_hash"] in html_export

# 3. Hashes d'exports sensibles à une modification réelle.
changed = deepcopy(source)
changed["developmental_prediction_engine"]["predicted_stage"] = "BIFURCATION"
changed_result = engine.step(inputs=changed, persist=False)

assert changed_result["dashboard_hash"] != first["dashboard_hash"]
assert (
    changed_result["export_integrity"]["json_hash"]
    != first["export_integrity"]["json_hash"]
)
assert (
    changed_result["export_integrity"]["markdown_hash"]
    != first["export_integrity"]["markdown_hash"]
)
assert (
    changed_result["export_integrity"]["html_hash"]
    != first["export_integrity"]["html_hash"]
)
guards(changed_result)

# 4. Persistance réelle et idempotence des trois fichiers.
with tempfile.TemporaryDirectory(prefix="oce_av9_") as tmp:
    local = DevelopmentalDashboard()
    local.output_dir = Path(tmp)

    persisted_1 = local.step(inputs=deepcopy(source), persist=True)
    paths_1 = {
        key: Path(persisted_1[key])
        for key in ("json_path", "markdown_path", "html_path")
    }

    assert persisted_1["persisted"] is True
    assert all(path.is_file() for path in paths_1.values())
    assert len(list(Path(tmp).iterdir())) == 3

    disk_json = paths_1["json_path"].read_text(encoding="utf-8")
    disk_markdown = paths_1["markdown_path"].read_text(encoding="utf-8")
    disk_html = paths_1["html_path"].read_text(encoding="utf-8")

    assert disk_json == persisted_1["exports"]["json"]
    assert disk_markdown == persisted_1["exports"]["markdown"]
    assert disk_html == persisted_1["exports"]["html"]

    persisted_2 = local.step(inputs=deepcopy(source), persist=True)
    paths_2 = {
        key: Path(persisted_2[key])
        for key in ("json_path", "markdown_path", "html_path")
    }

    assert paths_1 == paths_2
    assert persisted_2["dashboard_hash"] == persisted_1["dashboard_hash"]
    assert persisted_2["export_integrity"] == persisted_1["export_integrity"]
    assert len(list(Path(tmp).iterdir())) == 3
    guards(persisted_1)
    guards(persisted_2)

# 5. Échappement HTML exhaustif.
unsafe_context = ready_context()
unsafe_context["developmental_stage_classifier"]["developmental_stage"] = (
    "<script>alert('stage')</script>"
)
unsafe_context["developmental_stage_classifier"]["stage_history"] = [
    {
        "developmental_stage": "<img src=x onerror=alert(1)>",
        "timestamp_utc": "<svg/onload=alert(2)>",
    }
]
unsafe_context["developmental_prediction_engine"]["predicted_stage"] = (
    "\"><script>alert('prediction')</script>"
)
unsafe_context["developmental_prediction_engine"]["alternative_scenarios"] = [
    {
        "rank": 1,
        "stage": "<iframe src=javascript:alert(3)>",
        "probability": 1.0,
    }
]

unsafe = engine.step(inputs=unsafe_context, persist=False)
unsafe_html = unsafe["exports"]["html"]

for raw in (
    "<script>alert('stage')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(2)>",
    "\"><script>alert('prediction')</script>",
    "<iframe src=javascript:alert(3)>",
):
    assert raw not in unsafe_html

assert "&lt;script&gt;" in unsafe_html
assert "&lt;img" in unsafe_html
assert "&lt;svg" in unsafe_html
assert "&lt;iframe" in unsafe_html
guards(unsafe)

# 6. Données absentes ou partielles.
empty = engine.step(inputs={}, persist=False)
assert empty["dashboard_status"] == "DEVELOPMENTAL_DASHBOARD_INCOMPLETE"
assert empty["developmental_dashboard_ready"] is False
assert empty["current_stage"] == "UNDETERMINED"
assert empty["predicted_stage"] == "UNDETERMINED"
assert empty["module_completeness"] == 0.0
assert empty["exports"]["html"].startswith("<!doctype html>")
guards(empty)

partial = engine.step(
    inputs={
        "developmental_stage_classifier": {
            "classifier_status": "DEVELOPMENTAL_STAGE_CLASSIFIER_READY",
            "developmental_stage": "MATURATION",
            "stage_confidence": 0.80,
            "evidence_quality_score": 0.82,
        }
    },
    persist=False,
)
assert partial["dashboard_status"] == "DEVELOPMENTAL_DASHBOARD_INCOMPLETE"
assert partial["current_stage"] == "MATURATION"
assert partial["predicted_stage"] == "UNDETERMINED"
assert 0.0 < partial["module_completeness"] < 1.0
guards(partial)

# 7. Violation simulée des garde-fous amont.
violated_context = ready_context()
violated_context["developmental_prediction_engine"]["consciousness_proven"] = True

violated = engine.step(inputs=violated_context, persist=False)

assert violated["guard_summary"]["guard_status"] == "GUARD_VIOLATION"
assert (
    "developmental_prediction_engine.consciousness_proven"
    in violated["guard_summary"]["violations"]
)
assert violated["dashboard_status"] == "DEVELOPMENTAL_DASHBOARD_INCOMPLETE"
assert violated["developmental_dashboard_ready"] is False

# Les sorties publiques du dashboard restent elles-mêmes gouvernées.
guards(violated)

# 8. Entrées malformées et valeurs non finies.
malformed = engine.step(
    inputs={
        "developmental_blueprint": [],
        "genesis_detector": "invalid",
        "developmental_stage_classifier": {
            "developmental_stage": 123,
            "stage_confidence": float("nan"),
            "evidence_quality_score": float("inf"),
            "stage_history": [None, "invalid", {"stage": 999}],
        },
        "developmental_prediction_engine": {
            "predicted_stage": None,
            "prediction_confidence": "invalid",
            "prediction_uncertainty": float("inf"),
            "input_quality_score": -999,
            "forecast_horizon": "invalid",
            "alternative_scenarios": [None, "invalid", {"rank": "x"}],
        },
        "timeline": "invalid",
    },
    persist=False,
)

assert malformed["dashboard_status"] in {
    "DEVELOPMENTAL_DASHBOARD_READY",
    "DEVELOPMENTAL_DASHBOARD_INCOMPLETE",
}
assert 0.0 <= malformed["quality"]["overall_quality_score"] <= 1.0
assert 0.0 <= malformed["prediction_uncertainty"] <= 1.0
assert malformed["exports"]["html"].startswith("<!doctype html>")
guards(malformed)

print("AV9_EXTENDED_VALIDATION_OK")
