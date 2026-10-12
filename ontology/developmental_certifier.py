"""AV10 — functional developmental certifier.

Certifies the completeness, coherence, quality, hashes, exports, history and
epistemic guards of AV0→AV9 without executing upstream modules.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class DevelopmentalCertifier:
    primitive = "DEVELOPMENTAL_CERTIFIER"
    step_id = "AV10"
    public_schema_version = "1.0"

    REQUIRED_MODULES = (
        "developmental_blueprint",
        "genesis_detector",
        "maturation_tracker",
        "specialization_engine",
        "bifurcation_detector",
        "degeneration_detector",
        "recovery_engine",
        "developmental_stage_classifier",
        "developmental_prediction_engine",
        "developmental_dashboard",
    )

    FINAL_STATUS = "CONSCIOUSNESS_DEVELOPMENT_MODEL_COMPLETE"

    DEFAULTS = {
        "minimum_quality_score": 0.70,
        "maximum_uncertainty": 0.50,
        "minimum_completeness": 1.0,
        "minimum_certification_score": 0.85,
    }

    def _mapping(self, value: Any) -> Dict[str, Any]:
        return dict(value) if isinstance(value, Mapping) else {}

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        if not math.isfinite(number):
            number = default
        return max(0.0, min(1.0, number))

    def _stable_hash(self, value: Any) -> str:
        raw = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=repr,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _extract(self, inputs: Mapping[str, Any], name: str, aliases: tuple[str, ...]) -> Dict[str, Any]:
        for key in (name,) + aliases:
            value = inputs.get(key)
            if isinstance(value, Mapping):
                return dict(value)
        upstream = inputs.get("upstream_results")
        if isinstance(upstream, Mapping):
            for key in (name,) + aliases:
                value = upstream.get(key)
                if isinstance(value, Mapping):
                    return dict(value)
        return {}

    def _pipeline(self, inputs: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
        aliases = {
            "developmental_blueprint": ("AV0", "av0_result"),
            "genesis_detector": ("AV1", "av1_result", "genesis_result"),
            "maturation_tracker": ("AV2", "av2_result", "maturation_result"),
            "specialization_engine": ("AV3", "av3_result", "specialization_result"),
            "bifurcation_detector": ("AV4", "av4_result", "bifurcation_result"),
            "degeneration_detector": ("AV5", "av5_result", "degeneration_result"),
            "recovery_engine": ("AV6", "av6_result", "recovery_result"),
            "developmental_stage_classifier": ("AV7", "av7_result", "stage_result"),
            "developmental_prediction_engine": ("AV8", "av8_result", "prediction_result"),
            "developmental_dashboard": ("AV9", "av9_result", "dashboard_result"),
        }
        return {
            name: self._extract(inputs, name, aliases[name])
            for name in self.REQUIRED_MODULES
        }

    def _valid_sha256(self, value: Any) -> bool:
        text = str(value or "")
        return len(text) == 64 and all(ch in "0123456789abcdef" for ch in text.lower())

    def _artifact_check(self, dashboard: Mapping[str, Any], inputs: Mapping[str, Any]) -> Dict[str, Any]:
        exports = self._mapping(dashboard.get("exports"))
        paths = {
            "json": dashboard.get("json_path") or inputs.get("json_path"),
            "markdown": dashboard.get("markdown_path") or inputs.get("markdown_path"),
            "html": dashboard.get("html_path") or inputs.get("html_path"),
        }

        inline = {
            "json": isinstance(exports.get("json"), str) and bool(exports.get("json")),
            "markdown": isinstance(exports.get("markdown"), str) and bool(exports.get("markdown")),
            "html": isinstance(exports.get("html"), str) and bool(exports.get("html")),
        }
        files = {
            name: bool(path and Path(str(path)).is_file())
            for name, path in paths.items()
        }

        html_text = ""
        if inline["html"]:
            html_text = str(exports["html"])
        elif files["html"]:
            try:
                html_text = Path(str(paths["html"])).read_text(encoding="utf-8")
            except OSError:
                html_text = ""

        html_valid = bool(
            html_text.lstrip().lower().startswith("<!doctype html>")
            and "<html" in html_text.lower()
            and "</html>" in html_text.lower()
            and "<body" in html_text.lower()
            and "</body>" in html_text.lower()
        )

        json_valid = False
        json_text = ""
        if inline["json"]:
            json_text = str(exports["json"])
        elif files["json"]:
            try:
                json_text = Path(str(paths["json"])).read_text(encoding="utf-8")
            except OSError:
                json_text = ""
        if json_text:
            try:
                json.loads(json_text)
                json_valid = True
            except (TypeError, ValueError, json.JSONDecodeError):
                json_valid = False

        markdown_valid = inline["markdown"] or files["markdown"]

        return {
            "inline_exports": inline,
            "file_exports": files,
            "json_valid": json_valid,
            "markdown_valid": bool(markdown_valid),
            "html_valid": html_valid,
            "all_exports_present": all(
                inline[name] or files[name]
                for name in ("json", "markdown", "html")
            ),
        }

    def step(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        config = dict(self.DEFAULTS)
        supplied = inputs.get("config")
        if isinstance(supplied, Mapping):
            for key in config:
                if key in supplied:
                    config[key] = self._safe_float(supplied[key], config[key])

        pipeline = self._pipeline(inputs)
        presence = {name: bool(payload) for name, payload in pipeline.items()}
        completeness = round(
            sum(1 for value in presence.values() if value) / len(self.REQUIRED_MODULES),
            6,
        )

        stage = pipeline["developmental_stage_classifier"]
        prediction = pipeline["developmental_prediction_engine"]
        dashboard = pipeline["developmental_dashboard"]

        current_stage = str(stage.get("developmental_stage") or "UNDETERMINED")
        predicted_stage = str(prediction.get("predicted_stage") or "UNDETERMINED")
        dashboard_current = str(dashboard.get("current_stage") or "UNDETERMINED")
        dashboard_predicted = str(dashboard.get("predicted_stage") or "UNDETERMINED")

        coherence_checks = {
            "stage_matches_dashboard": current_stage == dashboard_current,
            "prediction_matches_dashboard": predicted_stage == dashboard_predicted,
            "dashboard_ready": dashboard.get("dashboard_status") == "DEVELOPMENTAL_DASHBOARD_READY",
            "stage_ready": (
                stage.get("classifier_status") == "DEVELOPMENTAL_STAGE_CLASSIFIER_READY"
                or stage.get("developmental_stage_classifier_status") == "DEVELOPMENTAL_STAGE_CLASSIFIER_READY"
            ),
            "prediction_ready": prediction.get("prediction_status") == "DEVELOPMENTAL_PREDICTION_READY",
        }
        coherence_ok = all(coherence_checks.values())

        quality = self._safe_float(
            self._mapping(dashboard.get("quality")).get("overall_quality_score"),
            min(
                self._safe_float(stage.get("stage_confidence")),
                self._safe_float(prediction.get("prediction_confidence")),
            ),
        )
        uncertainty = self._safe_float(prediction.get("prediction_uncertainty"), 1.0)
        quality_ok = (
            quality >= config["minimum_quality_score"]
            and uncertainty <= config["maximum_uncertainty"]
        )

        hashes = {
            "stage_hash": stage.get("stage_hash"),
            "prediction_hash": prediction.get("prediction_hash"),
            "dashboard_hash": dashboard.get("dashboard_hash"),
        }
        hash_checks = {name: self._valid_sha256(value) for name, value in hashes.items()}
        hashes_ok = all(hash_checks.values())

        artifacts = self._artifact_check(dashboard, inputs)
        exports_ok = bool(
            artifacts["all_exports_present"]
            and artifacts["json_valid"]
            and artifacts["markdown_valid"]
            and artifacts["html_valid"]
        )

        timeline = dashboard.get("timeline")
        history_ok = isinstance(timeline, list)

        violations = []
        for module_name, payload in pipeline.items():
            for key in (
                "consciousness_proven",
                "qualia_proven",
                "subjectivity_proven",
                "phenomenology_proven",
            ):
                if payload.get(key) is True:
                    violations.append(f"{module_name}.{key}")
        guard_ok = not violations

        condition_results = {
            "module_completeness": completeness >= config["minimum_completeness"],
            "coherence": coherence_ok,
            "quality": quality_ok,
            "hashes": hashes_ok,
            "exports": exports_ok,
            "history": history_ok,
            "guards": guard_ok,
            "no_upstream_recalculation": True,
        }

        weights = {
            "module_completeness": 0.20,
            "coherence": 0.18,
            "quality": 0.16,
            "hashes": 0.14,
            "exports": 0.14,
            "history": 0.08,
            "guards": 0.10,
        }
        score = sum(
            weights[key] if condition_results[key] else 0.0
            for key in weights
        )
        score = round(score, 6)

        certified = bool(
            all(condition_results.values())
            and score >= config["minimum_certification_score"]
        )

        certification_status = (
            self.FINAL_STATUS
            if certified
            else "CONSCIOUSNESS_DEVELOPMENT_MODEL_INCOMPLETE"
        )

        hash_payload = {
            "presence": presence,
            "completeness": completeness,
            "coherence_checks": coherence_checks,
            "quality": quality,
            "uncertainty": uncertainty,
            "hashes": hashes,
            "hash_checks": hash_checks,
            "artifacts": artifacts,
            "history_ok": history_ok,
            "guard_violations": violations,
            "condition_results": condition_results,
            "certification_score": score,
            "certification_status": certification_status,
            "config": config,
        }

        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "certification_status": certification_status,
            "certified": certified,
            "certification_score": score,
            "module_completeness": completeness,
            "module_presence": presence,
            "coherence_status": "COHERENT" if coherence_ok else "INCOHERENT",
            "coherence_checks": coherence_checks,
            "quality_status": "QUALITY_SUFFICIENT" if quality_ok else "QUALITY_INSUFFICIENT",
            "quality_score": round(quality, 6),
            "prediction_uncertainty": round(uncertainty, 6),
            "guard_status": "GUARDS_PRESERVED" if guard_ok else "GUARD_VIOLATION",
            "guard_violations": violations,
            "hash_status": "HASHES_VALID" if hashes_ok else "HASHES_INVALID",
            "hash_checks": hash_checks,
            "export_status": "EXPORTS_VALID" if exports_ok else "EXPORTS_INVALID",
            "export_checks": artifacts,
            "history_status": "HISTORY_PRESENT" if history_ok else "HISTORY_MISSING",
            "condition_results": condition_results,
            "missing_conditions": [
                key for key, value in condition_results.items() if not value
            ],
            "certification_hash": self._stable_hash(hash_payload),
            "audit_trace": {
                "method": "functional_developmental_axis_certification",
                "upstream_recalculation_performed": False,
                "required_module_count": len(self.REQUIRED_MODULES),
                "present_module_count": sum(1 for value in presence.values() if value),
            },
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }

        if persist:
            output_dir = ROOT / "developmental_science" / "AV10_developmental_certifier"
            output_dir.mkdir(parents=True, exist_ok=True)
            path = output_dir / "latest_developmental_certification.json"
            payload = dict(result)
            payload["persist_requested"] = False
            payload["persisted"] = False
            payload["output_path"] = None
            path.write_text(
                json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False),
                encoding="utf-8",
            )
            result["persisted"] = True
            result["output_path"] = str(path)

        return result


def step(
    inputs: Optional[Dict[str, Any]] = None,
    persist: bool = False,
) -> Dict[str, Any]:
    return DevelopmentalCertifier().step(inputs=inputs, persist=persist)
