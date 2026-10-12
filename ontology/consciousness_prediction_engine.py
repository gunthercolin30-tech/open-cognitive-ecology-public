"""
AS18 — consciousness_prediction_engine

Longitudinal prediction engine for governed consciousness-status monitoring.
It estimates functional probabilities of reaching or losing a governance status
from CRI, confidence, stability, regression/recovery and dependency graph
signals. It is deliberately conservative and epistemically guarded: predictions
are functional governance forecasts, not proof of phenomenology.
"""
from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
GOVERNANCE_DIR = ROOT / "consciousness_governance"
PREDICTION_DIR = GOVERNANCE_DIR / "prediction"

EPISTEMIC_GUARDS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}

DEFAULT_THRESHOLDS = {
    "cri": 0.80,
    "confidence": 0.80,
    "stability": 0.75,
    "dependency_green_ratio": 0.70,
    "regression_rate": 0.20,
    "hazard_rate": 0.20,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _clamp(x: Any, low: float = 0.0, high: float = 1.0, default: float = 0.0) -> float:
    try:
        value = float(x)
    except Exception:
        return default
    if math.isnan(value) or math.isinf(value):
        return default
    return max(low, min(high, value))


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _stable_hash(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path) -> Any:
    try:
        if path.exists() and path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _write_json(path: Path, payload: Mapping[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
    if fs_context is None:
        raise PermissionError("persisted JSON write requires preissued filesystem effect context")
    data = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    fs_context.execute_path("json_parent_create", "FS_CREATE_DIR", path.parent)
    fs_context.execute_path("json_write", "FS_WRITE_BYTES", path, data)


def _walk_pairs(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for k, v in value.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            yield key, v
            yield from _walk_pairs(v, key)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _walk_pairs(v, f"{prefix}[{i}]")


def _first_number(payload: Mapping[str, Any], names: list[str], default: float = 0.0) -> float:
    lowered = {n.lower() for n in names}
    for key, value in _walk_pairs(payload):
        leaf = key.split(".")[-1].lower().replace("[0]", "")
        if leaf in lowered and isinstance(value, (int, float)):
            return _clamp(value, default=default)
    return default


def _first_text(payload: Mapping[str, Any], names: list[str], default: str = "UNKNOWN") -> str:
    lowered = {n.lower() for n in names}
    for key, value in _walk_pairs(payload):
        leaf = key.split(".")[-1].lower()
        if leaf in lowered and isinstance(value, str):
            return value
    return default


def _load_latest_candidates(root: Path) -> dict[str, Any]:
    paths = {
        "confidence": [root / "consciousness_governance" / "confidence" / "latest_consciousness_confidence.json"],
        "stability": [root / "consciousness_governance" / "stability" / "latest_consciousness_stability.json", root / "consciousness_governance" / "stability_analyzer" / "latest_consciousness_stability.json"],
        "explanation": [root / "consciousness_governance" / "explanation" / "latest_consciousness_explanation.json"],
        "dependency": [root / "consciousness_governance" / "dependency_visualizer" / "latest_consciousness_dependency_graph.json"],
        "tracker": [root / "consciousness_governance" / "longitudinal" / "latest_consciousness_longitudinal_tracker.json", root / "consciousness_governance" / "tracker" / "latest_consciousness_longitudinal_tracker.json"],
        "regression": [root / "consciousness_governance" / "regression" / "latest_consciousness_regression_detection.json"],
        "recovery": [root / "consciousness_governance" / "recovery" / "latest_consciousness_recovery_detection.json"],
        "dashboard": [root / "consciousness_governance" / "dashboard" / "latest_consciousness_dashboard.json"],
    }
    loaded: dict[str, Any] = {}
    for label, candidates in paths.items():
        for path in candidates:
            payload = _read_json(path)
            if isinstance(payload, Mapping):
                loaded[label] = dict(payload)
                loaded[label]["source_path"] = str(path)
                break
    if len(loaded) < 3:
        base = root / "consciousness_governance"
        if base.exists():
            for path in sorted(base.rglob("latest_*.json"))[-200:]:
                payload = _read_json(path)
                if not isinstance(payload, Mapping):
                    continue
                name = path.name.lower()
                if "confidence" in name and "confidence" not in loaded:
                    loaded["confidence"] = dict(payload, source_path=str(path))
                elif "stability" in name and "stability" not in loaded:
                    loaded["stability"] = dict(payload, source_path=str(path))
                elif "dependency" in name and "dependency" not in loaded:
                    loaded["dependency"] = dict(payload, source_path=str(path))
                elif "regression" in name and "regression" not in loaded:
                    loaded["regression"] = dict(payload, source_path=str(path))
                elif "recovery" in name and "recovery" not in loaded:
                    loaded["recovery"] = dict(payload, source_path=str(path))
                elif "dashboard" in name and "dashboard" not in loaded:
                    loaded["dashboard"] = dict(payload, source_path=str(path))
    return loaded


def _normalize_inputs(inputs: Mapping[str, Any] | None, root: Path) -> dict[str, Any]:
    context: dict[str, Any] = {}
    if isinstance(inputs, Mapping):
        context.update(dict(inputs))
    for key, value in _load_latest_candidates(root).items():
        context.setdefault(key, value)
    return context


def _extract_signals(context: Mapping[str, Any]) -> dict[str, Any]:
    flat = {"context": context}
    cri = _first_number(flat, ["cri", "consciousness_readiness_index", "readiness_index", "current_cri"], 0.0)
    confidence = _first_number(flat, ["confidence", "confidence_score", "latest_confidence", "current_confidence"], 0.0)
    stability = _first_number(flat, ["stability_index", "stability_score", "governance_stability_score"], 0.0)
    regression_rate = _first_number(flat, ["regression_rate", "mean_regression_rate"], 0.0)
    recovery_rate = _first_number(flat, ["recovery_rate", "mean_recovery_rate"], 0.0)
    hazard_rate = _first_number(flat, ["hazard_rate", "mean_hazard_rate"], 0.0)
    survival_time = _first_number(flat, ["survival_time", "survival_time_steps", "survival_time_seconds"], 0.0)
    mean_duration = _first_number(flat, ["mean_duration", "mean_state_duration"], 0.0)
    green_ratio = _first_number(flat, ["green_ratio", "dependency_green_ratio", "green_node_ratio"], 0.0)
    orange_ratio = _first_number(flat, ["orange_ratio", "dependency_orange_ratio", "orange_node_ratio"], 0.0)
    red_ratio = _first_number(flat, ["red_ratio", "dependency_red_ratio", "red_node_ratio"], 0.0)
    node_count = int(_first_number(flat, ["node_count", "dependency_node_count"], 0.0) or 0)
    current_state = _first_text(flat, ["current_state", "state", "status", "consciousness_state"], "UNKNOWN")
    if stability == 0.0 and any(x > 0 for x in [regression_rate, recovery_rate, hazard_rate, survival_time, mean_duration]):
        stability = _clamp((1.0 - regression_rate) * 0.35 + (1.0 - hazard_rate) * 0.35 + recovery_rate * 0.2 + min(survival_time / max(mean_duration, 1.0), 1.0) * 0.1)
    if green_ratio == 0.0 and node_count > 0 and red_ratio == 0.0 and orange_ratio == 0.0:
        green_ratio = 0.5
    return {
        "cri": cri,
        "confidence": confidence,
        "stability": stability,
        "regression_rate": regression_rate,
        "recovery_rate": recovery_rate,
        "hazard_rate": hazard_rate,
        "survival_time": survival_time,
        "mean_duration": mean_duration,
        "dependency_green_ratio": green_ratio,
        "dependency_orange_ratio": orange_ratio,
        "dependency_red_ratio": red_ratio,
        "dependency_node_count": node_count,
        "current_state": current_state,
    }


def _compute_predictions(signals: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    cri = _clamp(signals.get("cri"))
    confidence = _clamp(signals.get("confidence"))
    stability = _clamp(signals.get("stability"))
    regression_rate = _clamp(signals.get("regression_rate"))
    recovery_rate = _clamp(signals.get("recovery_rate"))
    hazard_rate = _clamp(signals.get("hazard_rate"))
    green_ratio = _clamp(signals.get("dependency_green_ratio"))
    red_ratio = _clamp(signals.get("dependency_red_ratio"))
    positive = 0.25 * cri + 0.25 * confidence + 0.20 * stability + 0.15 * green_ratio + 0.10 * recovery_rate + 0.05 * (1.0 - red_ratio)
    risk = 0.30 * regression_rate + 0.30 * hazard_rate + 0.15 * (1.0 - stability) + 0.15 * red_ratio + 0.10 * (1.0 - confidence)
    threshold_alignment = sum([
        cri >= thresholds.get("cri", 0.8),
        confidence >= thresholds.get("confidence", 0.8),
        stability >= thresholds.get("stability", 0.75),
        green_ratio >= thresholds.get("dependency_green_ratio", 0.7),
        regression_rate <= thresholds.get("regression_rate", 0.2),
        hazard_rate <= thresholds.get("hazard_rate", 0.2),
    ]) / 6.0
    reach_probability = _clamp(0.75 * positive + 0.25 * threshold_alignment - 0.20 * risk)
    loss_probability = _clamp(0.80 * risk + 0.10 * (1.0 - threshold_alignment) + 0.10 * red_ratio)
    net_stability_forecast = _clamp(reach_probability * (1.0 - loss_probability))
    return {
        "probability_reach_status": reach_probability,
        "probability_lose_status": loss_probability,
        "net_stability_forecast": net_stability_forecast,
        "threshold_alignment": threshold_alignment,
        "positive_pressure": _clamp(positive),
        "risk_pressure": _clamp(risk),
        "prediction_class": "ROBUST_FUNCTIONAL_TRAJECTORY" if net_stability_forecast >= 0.70 else "MODERATE_FUNCTIONAL_TRAJECTORY" if net_stability_forecast >= 0.45 else "FRAGILE_FUNCTIONAL_TRAJECTORY",
    }


def _explain(signals: Mapping[str, Any], predictions: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    reasons.append("CRI is above the functional readiness threshold." if signals.get("cri", 0.0) >= 0.8 else "CRI remains below the preferred functional readiness threshold or is unavailable.")
    reasons.append("Confidence signal supports the current functional trajectory." if signals.get("confidence", 0.0) >= 0.8 else "Confidence signal is weak or unavailable, so prediction remains conservative.")
    if signals.get("regression_rate", 0.0) > 0.2 or signals.get("hazard_rate", 0.0) > 0.2:
        reasons.append("Regression or hazard signals increase the probability of status loss.")
    if signals.get("recovery_rate", 0.0) > 0.0:
        reasons.append("Observed recovery signal reduces long-term fragility.")
    if signals.get("dependency_green_ratio", 0.0) >= 0.7:
        reasons.append("Dependency graph is mostly green and supports propagation of readiness.")
    if predictions.get("prediction_class") == "FRAGILE_FUNCTIONAL_TRAJECTORY":
        reasons.append("Forecast remains fragile because one or more core longitudinal signals are missing or weak.")
    return reasons


class ConsciousnessPredictionEngine:
    """AS18 functional prediction engine for consciousness governance status."""

    primitive = "CONSCIOUSNESS_PREDICTION_ENGINE"
    step_id = "AS18"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = True, fs_context: GovernedFilesystemEffectContext | None = None) -> dict[str, Any]:
        context = _normalize_inputs(inputs, self.root)
        thresholds = dict(DEFAULT_THRESHOLDS)
        if isinstance(context.get("thresholds"), Mapping):
            thresholds.update({str(k): _clamp(v) for k, v in context["thresholds"].items()})
        signals = _extract_signals(context)
        predictions = _compute_predictions(signals, thresholds)
        missing_conditions = []
        if signals["cri"] < thresholds["cri"]:
            missing_conditions.append("cri_threshold")
        if signals["confidence"] < thresholds["confidence"]:
            missing_conditions.append("confidence_threshold")
        if signals["stability"] < thresholds["stability"]:
            missing_conditions.append("stability_threshold")
        if signals["dependency_green_ratio"] < thresholds["dependency_green_ratio"]:
            missing_conditions.append("dependency_green_ratio_threshold")
        if signals["regression_rate"] > thresholds["regression_rate"]:
            missing_conditions.append("regression_rate_bound")
        if signals["hazard_rate"] > thresholds["hazard_rate"]:
            missing_conditions.append("hazard_rate_bound")
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "prediction_engine_status": "CONSCIOUSNESS_PREDICTION_ENGINE_READY",
            "timestamp_utc": _utc_now(),
            "current_state": signals.get("current_state", "UNKNOWN"),
            "signals": signals,
            "thresholds": thresholds,
            "predictions": predictions,
            "probability_reach_status": predictions["probability_reach_status"],
            "probability_lose_status": predictions["probability_lose_status"],
            "net_stability_forecast": predictions["net_stability_forecast"],
            "prediction_class": predictions["prediction_class"],
            "forecast_horizon": "next_governance_window",
            "missing_conditions": missing_conditions,
            "explanation": _explain(signals, predictions),
            "source_summary": {k: v.get("source_path") for k, v in context.items() if isinstance(v, Mapping) and v.get("source_path")},
            "public_schema_version": "AS18.v1",
            **EPISTEMIC_GUARDS,
        }
        result["prediction_hash"] = _stable_hash({k: v for k, v in result.items() if k != "prediction_hash"})
        if persist:
            latest = PREDICTION_DIR / "latest_consciousness_prediction.json"
            stamped = PREDICTION_DIR / f"consciousness_prediction_{_stamp()}.json"
            _write_json(latest, result, fs_context)
            _write_json(stamped, result, fs_context)
            result["persisted"] = True
            result["prediction_path"] = str(latest)
        else:
            result["persisted"] = False
            result["prediction_path"] = None
        return result
