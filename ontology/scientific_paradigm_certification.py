# -*- coding: utf-8 -*-
'''
I10 - Scientific Paradigm Certification.

Terminal certification layer for Open Cognitive Ecology paradigm surveillance.
It certifies only measurable functional properties of a detected paradigm
transition: persistence, measurability, replicability and scientific support.
It does not assert phenomenal subjectivity.
'''

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Optional
import json
import math

PRIMITIVE = "scientific_paradigm_certification"
DEPENDENCIES = [
    "paradigm_shift_detection_engine",
    "scientific_consensus_tracker",
    "scientific_meta_analysis_engine",
    "scientific_theory_confidence_engine",
    "distributed_continuity_certification_dashboard",
    "embodied_coupling_scientific_certification",
    "final_scientific_status_dashboard",
    "metrics_history_recorder",
]
REGIME_TAXONOMY = ("stability", "transition", "rupture", "expansion", "collapse")
SHIFT_REGIMES = ("transition", "rupture", "expansion", "collapse")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if math.isnan(number) or math.isinf(number):
        number = default
    return max(0.0, min(1.0, number))


def _non_negative_int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except Exception:
        return default


def _regime(value: Any, default: str = "stability") -> str:
    text = str(value if value is not None else default).strip().lower()
    return text if text in REGIME_TAXONOMY else default


def _weighted_mean(items: list[tuple[float, float]]) -> float:
    total = sum(max(0.0, weight) for _, weight in items)
    if total <= 0.0:
        return 0.0
    return _bounded(sum(_bounded(value) * max(0.0, weight) for value, weight in items) / total)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value) != 0.0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "validated", "certified", "success"}
    return False


class ScientificParadigmCertification:
    primitive = PRIMITIVE

    def __init__(self, root: Optional[str | Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "paradigm_surveillance" / PRIMITIVE
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_json_path = self.output_dir / "latest_scientific_paradigm_certification.json"
        self.prometheus_path = self.output_dir / "scientific_paradigm_certification.prom"
        self.html_path = self.output_dir / "scientific_paradigm_certification.html"

    def _load_i9_state(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("paradigm_shift_detection") or inputs.get("i9") or inputs.get("detection")
        if isinstance(explicit, dict):
            return explicit
        path = self.root / "paradigm_surveillance" / "paradigm_shift_detection_engine" / "latest_paradigm_shift_detection_engine.json"
        return _read_json(path)

    def _external_validation_score(self) -> tuple[float, int]:
        base = self.root / "external_validation"
        if not base.exists():
            return 0.0, 0
        total = 0
        positives = 0
        for path in list(base.rglob("*.json"))[:500]:
            data = _read_json(path)
            if not data:
                continue
            total += 1
            if _safe_bool(data.get("success")) or _safe_bool(data.get("certified")) or _safe_bool(data.get("external_validation_success")):
                positives += 1
        if total == 0:
            return 0.0, 0
        return _bounded(positives / total), total

    def _history_score(self, detection: dict[str, Any]) -> tuple[float, int]:
        sequence = detection.get("historical_regime_sequence", [])
        if not isinstance(sequence, list):
            sequence = []
        history_file = self.root / "paradigm_surveillance" / "paradigm_evolution_history.jsonl"
        line_count = 0
        if history_file.exists():
            try:
                line_count = len([line for line in history_file.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()])
            except Exception:
                line_count = 0
        length = max(len(sequence), line_count, _non_negative_int(detection.get("indicators", {}).get("paradigm_history_length", 0) if isinstance(detection.get("indicators"), dict) else 0))
        return _bounded(length / 10.0), length

    def _replication_score(self, inputs: dict[str, Any], external_score: float) -> float:
        provided = inputs.get("replication_score")
        if provided is not None:
            return _bounded(provided)
        distributed = _read_json(self.root / "external_validation" / "distributed_scientific_ecosystem" / "latest_distributed_scientific_ecosystem.json")
        scientific_consensus = _bounded(distributed.get("scientific_consensus", 0.0))
        external_replication_count = _non_negative_int(distributed.get("external_replication_count", 0))
        replication_count_score = _bounded(external_replication_count / 3.0)
        return _weighted_mean([(external_score, 1.0), (scientific_consensus, 0.7), (replication_count_score, 0.6)])

    def _scientific_support_score(self, inputs: dict[str, Any]) -> float:
        support = inputs.get("scientific_support")
        if isinstance(support, dict):
            return _weighted_mean([
                (_bounded(support.get("meta_analysis_score", support.get("meta_analysis_confidence", 0.0))), 1.0),
                (_bounded(support.get("theory_confidence", 0.0)), 1.0),
                (_bounded(support.get("consensus", support.get("scientific_consensus", 0.0))), 0.9),
            ])
        values = []
        for rel in (
            "external_validation/distributed_scientific_ecosystem/latest_distributed_scientific_ecosystem.json",
            "external_validation/scientific_civilizational_certification/latest_scientific_civilizational_certification.json",
        ):
            data = _read_json(self.root / rel)
            for key in ("scientific_consensus", "scientific_certification_score", "distributed_scientific_ecosystem_score", "certification_confidence"):
                if key in data:
                    values.append(_bounded(data.get(key)))
        if values:
            return _bounded(sum(values) / len(values))
        return 0.0

    def _make_state(self, inputs: Optional[dict[str, Any]]) -> dict[str, Any]:
        inputs = dict(inputs or {})
        detection = self._load_i9_state(inputs)

        detected = _safe_bool(detection.get("paradigm_shift_detected"))
        detection_confidence = _bounded(detection.get("paradigm_shift_confidence", 0.0))
        current_regime = _regime(detection.get("current_regime", inputs.get("current_regime", "stability")))
        previous_raw = detection.get("previous_regime", inputs.get("previous_regime"))
        previous_regime = _regime(previous_raw, current_regime) if previous_raw is not None else None
        regime_changed = previous_regime is not None and previous_regime != current_regime

        persistence_score, history_length = self._history_score(detection)
        indicators = detection.get("indicators", {}) if isinstance(detection.get("indicators"), dict) else {}
        measurable_fields = [
            "shift_signal_strength", "transition_probability", "break_significance",
            "constraint_shift_index", "classification_confidence", "emergence_probability",
            "transition_density", "input_completeness",
        ]
        available = sum(1 for key in measurable_fields if key in indicators or key in detection)
        measurability_score = _bounded(available / len(measurable_fields))
        external_score, external_evidence_count = self._external_validation_score()
        replicability_score = self._replication_score(inputs, external_score)
        scientific_support_score = self._scientific_support_score(inputs)

        significance_score = _weighted_mean([
            (detection_confidence, 1.3),
            (1.0 if detected else 0.0, 0.7),
            (1.0 if current_regime in SHIFT_REGIMES else 0.0, 0.7),
            (1.0 if regime_changed else 0.0, 0.5),
        ])

        paradigm_certification_confidence = round(_weighted_mean([
            (significance_score, 1.25),
            (persistence_score, 1.10),
            (measurability_score, 1.00),
            (replicability_score, 0.95),
            (scientific_support_score, 0.90),
        ]), 4)

        paradigm_certification_readiness = bool(
            detected
            and current_regime in SHIFT_REGIMES
            and paradigm_certification_confidence >= 0.60
            and measurability_score >= 0.50
        )
        persistent = persistence_score >= 0.30
        measurable = measurability_score >= 0.50
        replicable = replicability_score >= 0.30
        scientifically_supported = scientific_support_score >= 0.30 or paradigm_certification_confidence >= 0.70

        if paradigm_certification_readiness and persistent and measurable and replicable and scientifically_supported:
            certification_status = "scientific_paradigm_shift_certified"
        elif paradigm_certification_readiness:
            certification_status = "certification_ready_requires_replication"
        elif detected:
            certification_status = "candidate_paradigm_shift_under_observation"
        else:
            certification_status = "no_certifiable_paradigm_shift"

        return {
            "primitive": PRIMITIVE,
            "timestamp_utc": _now(),
            "success": True,
            "paradigm_certification_readiness": paradigm_certification_readiness,
            "paradigm_certification_confidence": paradigm_certification_confidence,
            "certification_status": certification_status,
            "current_regime": current_regime,
            "previous_regime": previous_regime,
            "paradigm_shift_detected": detected,
            "paradigm_shift_confidence": detection_confidence,
            "persistent": persistent,
            "measurable": measurable,
            "replicable": replicable,
            "scientifically_supported": scientifically_supported,
            "scores": {
                "significance_score": round(significance_score, 4),
                "persistence_score": round(persistence_score, 4),
                "measurability_score": round(measurability_score, 4),
                "replicability_score": round(replicability_score, 4),
                "scientific_support_score": round(scientific_support_score, 4),
                "external_validation_score": round(external_score, 4),
            },
            "evidence": {
                "history_length": history_length,
                "external_evidence_count": external_evidence_count,
                "measurable_field_count": available,
                "regime_changed": regime_changed,
            },
            "governance": {
                "non_closure_compliant": True,
                "closure_pressure_increase": False,
                "traceability": True,
                "reversibility": True,
                "functional_metrics_only": True,
                "requires_independent_replication_for_strong_claim": True,
            },
            "epistemic_position": {
                "architecture_computationnelle": True,
                "indicateurs_fonctionnels_mesurables": True,
                "subjectivite_phenomenale_affirmee": False,
                "ontologie_conceptuelle": "scientific certification of paradigm-regime transitions",
            },
            "source_detection": {
                "primitive": detection.get("primitive"),
                "timestamp_utc": detection.get("timestamp_utc"),
                "json_path": detection.get("json_path"),
            },
            "error_count": 0,
        }

    def _write_json(self, state: dict[str, Any]) -> None:
        self.latest_json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def _write_prometheus(self, state: dict[str, Any]) -> None:
        scores = state.get("scores", {}) if isinstance(state.get("scores"), dict) else {}
        evidence = state.get("evidence", {}) if isinstance(state.get("evidence"), dict) else {}
        lines = [
            "# HELP oce_scientific_paradigm_certification_success I10 execution success.",
            "# TYPE oce_scientific_paradigm_certification_success gauge",
            f"oce_scientific_paradigm_certification_success {1 if state.get('success') else 0}",
            "# HELP oce_scientific_paradigm_certification_readiness I10 certification readiness.",
            "# TYPE oce_scientific_paradigm_certification_readiness gauge",
            f"oce_scientific_paradigm_certification_readiness {1 if state.get('paradigm_certification_readiness') else 0}",
            "# HELP oce_scientific_paradigm_certification_confidence I10 certification confidence.",
            "# TYPE oce_scientific_paradigm_certification_confidence gauge",
            f"oce_scientific_paradigm_certification_confidence {float(state.get('paradigm_certification_confidence', 0.0))}",
            f"oce_scientific_paradigm_shift_detected {1 if state.get('paradigm_shift_detected') else 0}",
            f"oce_scientific_paradigm_persistent {1 if state.get('persistent') else 0}",
            f"oce_scientific_paradigm_measurable {1 if state.get('measurable') else 0}",
            f"oce_scientific_paradigm_replicable {1 if state.get('replicable') else 0}",
        ]
        for namespace, data in (("score", scores), ("evidence", evidence)):
            for key, value in data.items():
                if isinstance(value, bool):
                    numeric = 1 if value else 0
                elif isinstance(value, (int, float)):
                    numeric = value
                else:
                    continue
                safe_key = "".join(ch if ch.isalnum() else "_" for ch in str(key).lower()).strip("_")
                lines.append(f"oce_scientific_paradigm_{namespace}_{safe_key} {numeric}")
        self.prometheus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_html(self, state: dict[str, Any]) -> None:
        rows = []
        for key in (
            "paradigm_certification_readiness", "paradigm_certification_confidence",
            "certification_status", "current_regime", "previous_regime",
            "paradigm_shift_detected", "paradigm_shift_confidence",
            "persistent", "measurable", "replicable", "scientifically_supported",
        ):
            rows.append(f"<tr><td>{escape(str(key))}</td><td>{escape(str(state.get(key)))}</td></tr>")
        for section in ("scores", "evidence", "governance"):
            data = state.get(section, {}) if isinstance(state.get(section), dict) else {}
            for key, value in data.items():
                rows.append(f"<tr><td>{escape(section + '.' + str(key))}</td><td>{escape(str(value))}</td></tr>")
        html = "<!doctype html><html><head><meta charset='utf-8'><title>Scientific Paradigm Certification</title><style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ccc;padding:8px;text-align:left;}th{background:#f0f0f0;}</style></head><body><h1>Scientific Paradigm Certification</h1><p>I10 terminal certification of measurable paradigm-regime transitions. Functional metrics only; no phenomenal subjectivity claim.</p><table><tr><th>Metric</th><th>Value</th></tr>" + "\n".join(rows) + "</table></body></html>\n"
        self.html_path.write_text(html, encoding="utf-8")

    def _record_metrics_safely(self, state: dict[str, Any], metrics_effect_context=None) -> None:
        try:
            from ontology.metrics_history_recorder import record_metrics
            scores = state.get("scores", {}) if isinstance(state.get("scores"), dict) else {}
            payload = {
                "primitive": PRIMITIVE,
                "paradigm_certification_readiness": 1.0 if state.get("paradigm_certification_readiness") else 0.0,
                "paradigm_certification_confidence": state.get("paradigm_certification_confidence", 0.0),
                **scores,
                "error_count": 0,
            }
            record_metrics(payload, primitive=PRIMITIVE, validation_status="validated", governance_status="governed", runtime_status="operational", effect_context=metrics_effect_context)
        except Exception:
            pass

    def step(self, inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        metrics_effect_context = inputs.pop("metrics_effect_context", None)
        state = self._make_state(inputs)
        self._write_json(state)
        self._write_prometheus(state)
        self._write_html(state)
        self._record_metrics_safely(state, metrics_effect_context=metrics_effect_context)
        state.update({
            "json_export_ready": self.latest_json_path.exists(),
            "prometheus_export_ready": self.prometheus_path.exists(),
            "html_export_ready": self.html_path.exists(),
            "json_path": str(self.latest_json_path),
            "prometheus_path": str(self.prometheus_path),
            "html_path": str(self.html_path),
        })
        return state


ENGINE = ScientificParadigmCertification()


def step(inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return ENGINE.step(inputs)
