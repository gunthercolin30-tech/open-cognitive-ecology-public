"""
J7 — Civilizational Stability Index

Composite, observational-only synthesis of civilizational stability from:
- identity drift
- strategic drift
- memory drift
- drift correlations
- drift cascades
- optional resilience / viability / metrics signals

This primitive does not modify identity, memory, strategy, or upstream drift states.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def _clamp01(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _mean(values: list[float], default: float = 0.0) -> float:
    clean = [_clamp01(v) for v in values if v is not None]
    if not clean:
        return default
    return sum(clean) / len(clean)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {}


def _extract_first(mapping: Mapping[str, Any] | None, keys: list[str], default: float = 0.0) -> float:
    if not isinstance(mapping, Mapping):
        return default
    for key in keys:
        if key in mapping:
            return _clamp01(mapping.get(key), default)
    return default


class CivilizationalStabilityIndex:
    """
    Computes a synthetic stability index from J2-J6 drift indicators.

    Interpretation:
    - The index is functional and measurable.
    - It does not imply phenomenal subjectivity.
    - It is observational-only and non-mutative.
    """

    primitive = "civilizational_stability_index"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.output_dir = self.root / "civilizational_drift"
        self.latest_path = self.output_dir / "latest_civilizational_stability_index.json"
        self.history_path = self.output_dir / "civilizational_stability_index_history.jsonl"

    def _load_default_inputs(self) -> dict[str, Any]:
        d = self.output_dir
        return {
            "identity": _read_json(d / "latest_identity_drift_monitor.json"),
            "strategy": _read_json(d / "latest_strategic_drift_monitor.json"),
            "memory": _read_json(d / "latest_memory_drift_monitor.json"),
            "correlation": _read_json(d / "latest_drift_correlation_analyzer.json"),
            "cascade": _read_json(d / "latest_drift_cascade_detector.json"),
            "resilience": _read_json(self.root / "civilizational_resilience" / "latest_civilizational_resilience.json"),
            "viability": _read_json(self.root / "global_viability" / "latest_global_viability_certificate.json"),
            "metrics": _read_json(self.root / "civilizational_metrics" / "latest_civilizational_metrics_synthesizer.json"),
        }

    def _classify(self, stability: float, risk: float) -> str:
        stability = _clamp01(stability)
        risk = _clamp01(risk)
        if stability >= 0.82 and risk <= 0.25:
            return "robust"
        if stability >= 0.68 and risk <= 0.40:
            return "stable"
        if stability >= 0.50 and risk <= 0.60:
            return "watch"
        if stability >= 0.30:
            return "fragile"
        return "critical"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        data = self._load_default_inputs()
        if isinstance(inputs, dict):
            data.update(inputs)

        identity = data.get("identity", {})
        strategy = data.get("strategy", {})
        memory = data.get("memory", {})
        correlation = data.get("correlation", {})
        cascade = data.get("cascade", {})
        resilience = data.get("resilience", {})
        viability = data.get("viability", {})
        metrics = data.get("metrics", {})

        identity_drift = _extract_first(identity, [
            "identity_drift_score", "drift_score", "identity_drift_index"
        ])
        strategic_drift = _extract_first(strategy, [
            "strategic_drift_score", "strategy_drift_score", "drift_score", "strategic_drift_index"
        ])
        memory_drift = _extract_first(memory, [
            "memory_drift_score", "drift_score", "memory_drift_index"
        ])

        systemic_coupling = _extract_first(correlation, [
            "systemic_drift_coupling_index", "systemic_coupling_index", "correlation_strength"
        ])
        coordinated_risk = _extract_first(correlation, [
            "coordinated_drift_risk_index", "coordinated_risk_index", "correlation_risk_index"
        ])

        cascade_strength = _extract_first(cascade, ["cascade_strength"])
        cascade_risk = _extract_first(cascade, ["cascade_risk_index"])
        early_warning = _extract_first(cascade, ["early_warning_score"])

        resilience_score = _extract_first(resilience, [
            "civilizational_resilience_index", "resilience_score", "systemic_resilience_score"
        ], default=0.5)
        viability_score = _extract_first(viability, [
            "global_viability_score", "global_viability_index", "viability_score"
        ], default=0.5)
        metrics_viability = _extract_first(metrics, [
            "civilizational_viability_index", "civilizational_viability_score", "operational_viability_index"
        ], default=0.5)

        drift_pressure_index = _mean([identity_drift, strategic_drift, memory_drift])
        correlation_pressure_index = _mean([systemic_coupling, coordinated_risk])
        cascade_pressure_index = _mean([cascade_strength, cascade_risk, early_warning])
        support_index = _mean([resilience_score, viability_score, metrics_viability], default=0.5)

        systemic_resilience_margin = _clamp01(support_index - (0.5 * drift_pressure_index + 0.3 * cascade_pressure_index + 0.2 * correlation_pressure_index) + 0.5)

        stability = _clamp01(
            0.40 * (1.0 - drift_pressure_index)
            + 0.20 * (1.0 - correlation_pressure_index)
            + 0.20 * (1.0 - cascade_pressure_index)
            + 0.20 * support_index
        )

        early_warning_adjusted_stability = _clamp01(stability * (1.0 - 0.35 * early_warning))
        stability_risk_index = _clamp01(1.0 - early_warning_adjusted_stability)
        classification = self._classify(early_warning_adjusted_stability, stability_risk_index)

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "monitor_ready": True,
            "current_drift_scores": {
                "identity": identity_drift,
                "strategy": strategic_drift,
                "memory": memory_drift,
            },
            "correlation_inputs": {
                "systemic_drift_coupling_index": systemic_coupling,
                "coordinated_drift_risk_index": coordinated_risk,
                "correlation_pressure_index": correlation_pressure_index,
            },
            "cascade_inputs": {
                "cascade_strength": cascade_strength,
                "cascade_risk_index": cascade_risk,
                "early_warning_score": early_warning,
                "cascade_pressure_index": cascade_pressure_index,
            },
            "support_inputs": {
                "civilizational_resilience_index": resilience_score,
                "global_viability_score": viability_score,
                "civilizational_viability_index": metrics_viability,
                "support_index": support_index,
            },
            "drift_pressure_index": drift_pressure_index,
            "systemic_resilience_margin": systemic_resilience_margin,
            "civilizational_stability_index": stability,
            "early_warning_adjusted_stability": early_warning_adjusted_stability,
            "stability_risk_index": stability_risk_index,
            "stability_classification": classification,
            "governance": {
                "observational_only": True,
                "does_not_modify_identity": True,
                "does_not_modify_strategy": True,
                "does_not_modify_memory": True,
                "does_not_modify_upstream_monitors": True,
                "non_closure_compliant": True,
            },
        }

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.latest_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            with self.history_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

        return result


if __name__ == "__main__":
    print(json.dumps(CivilizationalStabilityIndex().step(persist=True), ensure_ascii=False, indent=2))
