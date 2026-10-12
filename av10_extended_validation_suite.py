#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path

from ontology.developmental_certifier import DevelopmentalCertifier


def guards(result: dict) -> None:
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True


def ready_context(tmpdir: Path | None = None) -> dict:
    stage_hash = "a" * 64
    prediction_hash = "b" * 64
    dashboard_hash = "c" * 64

    html = "<!doctype html><html><body>AV9</body></html>"
    markdown = "# AV9 Developmental Dashboard\n"
    dashboard_json = json.dumps({"dashboard_hash": dashboard_hash})

    dashboard = {
        "dashboard_status": "DEVELOPMENTAL_DASHBOARD_READY",
        "current_stage": "SPECIALIZATION",
        "predicted_stage": "STABLE_DEVELOPED_REGIME",
        "dashboard_hash": dashboard_hash,
        "quality": {"overall_quality_score": 0.89},
        "timeline": [
            {"developmental_stage": "GENESIS"},
            {"developmental_stage": "MATURATION"},
            {"developmental_stage": "SPECIALIZATION"},
        ],
        "exports": {
            "json": dashboard_json,
            "markdown": markdown,
            "html": html,
        },
    }

    if tmpdir is not None:
        json_path = tmpdir / "latest_developmental_dashboard.json"
        md_path = tmpdir / "latest_developmental_dashboard.md"
        html_path = tmpdir / "latest_developmental_dashboard.html"

        json_path.write_text(dashboard_json, encoding="utf-8")
        md_path.write_text(markdown, encoding="utf-8")
        html_path.write_text(html, encoding="utf-8")

        dashboard["json_path"] = str(json_path)
        dashboard["markdown_path"] = str(md_path)
        dashboard["html_path"] = str(html_path)

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
        "developmental_dashboard": dashboard,
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

# 1. Cas nominal complet et déterminisme.
source = ready_context()
snapshot = deepcopy(source)

first = engine.step(inputs=source, persist=False)
second = engine.step(inputs=deepcopy(source), persist=False)

assert source == snapshot
assert first["certification_status"] == "CONSCIOUSNESS_DEVELOPMENT_MODEL_COMPLETE"
assert first["certified"] is True
assert first["certification_score"] == 1.0
assert first["module_completeness"] == 1.0
assert first["coherence_status"] == "COHERENT"
assert first["quality_status"] == "QUALITY_SUFFICIENT"
assert first["guard_status"] == "GUARDS_PRESERVED"
assert first["hash_status"] == "HASHES_VALID"
assert first["export_status"] == "EXPORTS_VALID"
assert first["history_status"] == "HISTORY_PRESENT"
assert first["certification_hash"] == second["certification_hash"]
assert first["condition_results"] == second["condition_results"]
assert first["audit_trace"]["upstream_recalculation_performed"] is False
guards(first)
guards(second)

# 2. Seuils configurables.
strict = ready_context()
strict_result = engine.step(
    inputs={
        **strict,
        "config": {
            "minimum_quality_score": 0.95,
            "maximum_uncertainty": 0.10,
            "minimum_completeness": 1.0,
            "minimum_certification_score": 0.95,
        },
    },
    persist=False,
)
assert strict_result["certified"] is False
assert strict_result["quality_status"] == "QUALITY_INSUFFICIENT"
assert "quality" in strict_result["missing_conditions"]
guards(strict_result)

# 3. Artefacts réels présents sur disque.
with tempfile.TemporaryDirectory(prefix="oce_av10_artifacts_") as tmp:
    ctx = ready_context(Path(tmp))
    disk_result = engine.step(inputs=ctx, persist=False)
    assert disk_result["export_checks"]["all_exports_present"] is True
    assert disk_result["export_checks"]["json_valid"] is True
    assert disk_result["export_checks"]["markdown_valid"] is True
    assert disk_result["export_checks"]["html_valid"] is True
    assert disk_result["certified"] is True
    guards(disk_result)

# 4. Fichier HTML absent.
with tempfile.TemporaryDirectory(prefix="oce_av10_missing_html_") as tmp:
    tmpdir = Path(tmp)
    ctx = ready_context(tmpdir)
    ctx["developmental_dashboard"]["exports"]["html"] = ""
    Path(ctx["developmental_dashboard"]["html_path"]).unlink()

    result = engine.step(inputs=ctx, persist=False)
    assert result["certified"] is False
    assert result["export_status"] == "EXPORTS_INVALID"
    assert result["export_checks"]["html_valid"] is False
    assert "exports" in result["missing_conditions"]
    guards(result)

# 5. HTML structurellement invalide.
invalid_html = ready_context()
invalid_html["developmental_dashboard"]["exports"]["html"] = "<html><body>broken"
invalid_html_result = engine.step(inputs=invalid_html, persist=False)
assert invalid_html_result["certified"] is False
assert invalid_html_result["export_checks"]["html_valid"] is False
guards(invalid_html_result)

# 6. JSON invalide.
invalid_json = ready_context()
invalid_json["developmental_dashboard"]["exports"]["json"] = "{bad-json"
invalid_json_result = engine.step(inputs=invalid_json, persist=False)
assert invalid_json_result["certified"] is False
assert invalid_json_result["export_checks"]["json_valid"] is False
guards(invalid_json_result)

# 7. Hashes invalides séparément.
for module_name, hash_key in (
    ("developmental_stage_classifier", "stage_hash"),
    ("developmental_prediction_engine", "prediction_hash"),
    ("developmental_dashboard", "dashboard_hash"),
):
    ctx = ready_context()
    ctx[module_name][hash_key] = "not-a-sha256"
    result = engine.step(inputs=ctx, persist=False)
    assert result["certified"] is False
    assert result["hash_status"] == "HASHES_INVALID"
    assert result["hash_checks"][hash_key] is False
    guards(result)

# 8. Incohérences croisées AV7 / AV8 / AV9.
stage_mismatch = ready_context()
stage_mismatch["developmental_dashboard"]["current_stage"] = "DEGENERATION"
stage_mismatch_result = engine.step(inputs=stage_mismatch, persist=False)
assert stage_mismatch_result["certified"] is False
assert stage_mismatch_result["coherence_checks"]["stage_matches_dashboard"] is False
guards(stage_mismatch_result)

prediction_mismatch = ready_context()
prediction_mismatch["developmental_dashboard"]["predicted_stage"] = "RECOVERY"
prediction_mismatch_result = engine.step(inputs=prediction_mismatch, persist=False)
assert prediction_mismatch_result["certified"] is False
assert (
    prediction_mismatch_result["coherence_checks"]["prediction_matches_dashboard"]
    is False
)
guards(prediction_mismatch_result)

# 9. Historisation invalide.
history_missing = ready_context()
history_missing["developmental_dashboard"]["timeline"] = "invalid"
history_result = engine.step(inputs=history_missing, persist=False)
assert history_result["certified"] is False
assert history_result["history_status"] == "HISTORY_MISSING"
assert "history" in history_result["missing_conditions"]
guards(history_result)

# 10. Violations épistémologiques sur chacun des étages critiques.
for module_name, flag in (
    ("developmental_stage_classifier", "consciousness_proven"),
    ("developmental_prediction_engine", "qualia_proven"),
    ("developmental_dashboard", "subjectivity_proven"),
    ("developmental_dashboard", "phenomenology_proven"),
):
    ctx = ready_context()
    ctx[module_name][flag] = True
    result = engine.step(inputs=ctx, persist=False)
    assert result["certified"] is False
    assert result["guard_status"] == "GUARD_VIOLATION"
    assert f"{module_name}.{flag}" in result["guard_violations"]
    guards(result)

# 11. Persistance AV10 et idempotence.
with tempfile.TemporaryDirectory(prefix="oce_av10_persist_") as tmp:
    local = DevelopmentalCertifier()

    import ontology.developmental_certifier as module
    original_root = module.ROOT

    try:
        module.ROOT = Path(tmp)
        persisted_1 = local.step(inputs=ready_context(), persist=True)
        path = Path(persisted_1["output_path"])

        assert persisted_1["persisted"] is True
        assert path.is_file()

        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["certification_hash"] == persisted_1["certification_hash"]
        assert payload["persisted"] is False
        assert payload["output_path"] is None

        persisted_2 = local.step(inputs=ready_context(), persist=True)
        assert persisted_2["certification_hash"] == persisted_1["certification_hash"]
        assert Path(persisted_2["output_path"]) == path
        assert len(list(path.parent.glob("*.json"))) == 1
        guards(persisted_1)
        guards(persisted_2)
    finally:
        module.ROOT = original_root

# 12. Entrées malformées / non finies.
malformed = engine.step(
    inputs={
        "developmental_blueprint": [],
        "genesis_detector": "invalid",
        "developmental_stage_classifier": {
            "classifier_status": 123,
            "developmental_stage": None,
            "stage_confidence": float("nan"),
            "stage_hash": float("inf"),
        },
        "developmental_prediction_engine": {
            "prediction_status": [],
            "predicted_stage": None,
            "prediction_confidence": "bad",
            "prediction_uncertainty": float("inf"),
            "prediction_hash": None,
        },
        "developmental_dashboard": {
            "dashboard_status": None,
            "current_stage": 123,
            "predicted_stage": [],
            "dashboard_hash": {},
            "quality": {"overall_quality_score": float("nan")},
            "timeline": None,
            "exports": {
                "json": None,
                "markdown": [],
                "html": {},
            },
        },
        "config": {
            "minimum_quality_score": float("nan"),
            "maximum_uncertainty": float("inf"),
            "minimum_completeness": "bad",
            "minimum_certification_score": None,
        },
    },
    persist=False,
)

assert malformed["certified"] is False
assert 0.0 <= malformed["certification_score"] <= 1.0
assert 0.0 <= malformed["module_completeness"] <= 1.0
assert len(malformed["certification_hash"]) == 64
guards(malformed)

print("AV10_EXTENDED_VALIDATION_OK")
