from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PreventiveStabilityRecommendationEngine:
    '\n    J9 — Preventive Stability Recommendation Engine.\n\n    This primitive is intentionally observational-only. It converts stability\n    and forecasting signals into ranked preventive recommendations. It never\n    modifies identity, memory, strategy, governance, or runtime execution.\n    '

    primitive = "preventive_stability_recommendation_engine"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "civilizational_drift"
        self.latest_path = self.output_dir / "latest_preventive_stability_recommendation_engine.json"
        self.history_path = self.output_dir / "preventive_stability_recommendation_engine_history.jsonl"

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            v = float(value)
        except (TypeError, ValueError):
            v = default
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return v

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _load_default_inputs(self) -> dict[str, Any]:
        return {
            "stability": self._read_json(self.output_dir / "latest_civilizational_stability_index.json"),
            "forecast": self._read_json(self.output_dir / "latest_drift_forecasting_engine.json"),
        }

    def _recommendations_for_context(
        self,
        stability_index: float,
        drift_pressure: float,
        stability_risk: float,
        forecast_risk: float,
        forecast_confidence: float,
        early_warning_adjusted_stability: float,
        horizon_estimate: Any,
    ) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []

        def add(rank: int, code: str, priority: float, target: str, rationale: str, action: str) -> None:
            recommendations.append({
                "rank": rank,
                "code": code,
                "priority_score": round(self._clamp(priority), 6),
                "target": target,
                "recommendation_type": "preventive_observational_recommendation",
                "recommended_action": action,
                "rationale": rationale,
                "requires_direct_identity_change": False,
                "requires_direct_memory_change": False,
                "requires_direct_strategy_change": False,
                "requires_direct_execution": False,
            })

        risk_pressure = max(drift_pressure, stability_risk, forecast_risk)

        if forecast_risk >= 0.70 or stability_risk >= 0.70:
            add(
                1,
                "increase_drift_observation_frequency",
                max(forecast_risk, stability_risk),
                "monitoring_cadence",
                "High forecast or stability risk suggests a possible future degradation regime.",
                "Increase observation frequency for drift metrics and review J7/J8 reports before any intervention.",
            )
            add(
                2,
                "request_constitutional_governance_review",
                max(stability_risk, forecast_risk) * 0.95,
                "governance_review",
                "Elevated risk should be routed through governance checks rather than direct state modification.",
                "Open a governance review checkpoint without changing identity, memory, or strategy.",
            )
        elif risk_pressure >= 0.40:
            add(
                1,
                "maintain_enhanced_stability_watch",
                risk_pressure,
                "stability_watch",
                "Moderate drift pressure warrants reinforced observation but not corrective action.",
                "Continue monitoring J5-J8 outputs and compare next run with the current trajectory.",
            )
        else:
            add(
                1,
                "continue_baseline_monitoring",
                max(0.10, risk_pressure),
                "baseline_monitoring",
                "Current stability and forecast signals remain within a robust observation regime.",
                "Maintain baseline monitoring and preserve historical continuity for longitudinal comparison.",
            )

        if drift_pressure >= 0.50:
            add(
                len(recommendations) + 1,
                "inspect_drift_pressure_sources",
                drift_pressure,
                "drift_source_analysis",
                "Drift pressure is high enough to require source-level inspection of identity, strategy, and memory monitors.",
                "Inspect upstream drift reports; do not directly edit any upstream state.",
            )

        if early_warning_adjusted_stability <= 0.50:
            add(
                len(recommendations) + 1,
                "activate_early_warning_review",
                1.0 - early_warning_adjusted_stability,
                "early_warning_review",
                "Early-warning-adjusted stability indicates reduced future stability margin.",
                "Review cascade and forecasting reports before scheduling any future governance action.",
            )

        if forecast_confidence < 0.35:
            add(
                len(recommendations) + 1,
                "increase_forecast_evidence_depth",
                1.0 - forecast_confidence,
                "forecast_evidence",
                "Low forecast confidence indicates insufficient longitudinal evidence.",
                "Collect more longitudinal observations before interpreting future risk strongly.",
            )

        if isinstance(horizon_estimate, dict):
            horizon_status = str(horizon_estimate.get("status", ""))
            horizon_steps = horizon_estimate.get("steps_until_threshold")
            if horizon_status in {"threshold_reached", "near_threshold", "finite_horizon"} or horizon_steps in (0, 1, 2):
                add(
                    len(recommendations) + 1,
                    "review_stability_horizon",
                    0.75,
                    "stability_horizon",
                    "The forecast horizon suggests possible approach to a stability threshold.",
                    "Review horizon estimates and prepare non-invasive monitoring escalation.",
                )

        recommendations.sort(key=lambda item: item["priority_score"], reverse=True)
        for idx, item in enumerate(recommendations, start=1):
            item["rank"] = idx
        return recommendations

    def step(
        self,
        inputs: dict[str, Any] | None = None,
        persist: bool = True,
    ) -> dict[str, Any]:
        data = inputs if isinstance(inputs, dict) else self._load_default_inputs()
        stability = data.get("stability", {}) if isinstance(data.get("stability", {}), dict) else {}
        forecast = data.get("forecast", {}) if isinstance(data.get("forecast", {}), dict) else {}

        stability_index = self._clamp(stability.get("civilizational_stability_index"), 0.5)
        drift_pressure = self._clamp(stability.get("drift_pressure_index"), 0.0)
        stability_risk = self._clamp(stability.get("stability_risk_index"), 1.0 - stability_index)
        early_warning_adjusted_stability = self._clamp(
            stability.get("early_warning_adjusted_stability"), stability_index
        )
        stability_classification = str(stability.get("stability_classification", "unknown"))

        forecast_risk = self._clamp(forecast.get("forecast_risk_index"), stability_risk)
        forecast_confidence = self._clamp(forecast.get("forecast_confidence"), 0.0)
        stability_horizon_estimate = forecast.get("stability_horizon_estimate", "unknown")

        recommendations = self._recommendations_for_context(
            stability_index=stability_index,
            drift_pressure=drift_pressure,
            stability_risk=stability_risk,
            forecast_risk=forecast_risk,
            forecast_confidence=forecast_confidence,
            early_warning_adjusted_stability=early_warning_adjusted_stability,
            horizon_estimate=stability_horizon_estimate,
        )

        recommendation_count = len(recommendations)
        recommendation_priority_score = max(
            (r["priority_score"] for r in recommendations), default=0.0
        )
        governance_review_recommended = any(
            r["target"] in {"governance_review", "early_warning_review", "stability_horizon"}
            for r in recommendations
        )

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "monitor_ready": True,
            "recommendation_count": recommendation_count,
            "recommendation_priority_score": round(recommendation_priority_score, 6),
            "forecast_risk_context": {
                "civilizational_stability_index": round(stability_index, 6),
                "stability_classification": stability_classification,
                "drift_pressure_index": round(drift_pressure, 6),
                "stability_risk_index": round(stability_risk, 6),
                "forecast_risk_index": round(forecast_risk, 6),
                "forecast_confidence": round(forecast_confidence, 6),
                "early_warning_adjusted_stability": round(early_warning_adjusted_stability, 6),
                "stability_horizon_estimate": stability_horizon_estimate,
            },
            "recommended_actions": recommendations,
            "recommended_observations": [
                "Re-read J7 stability output before interpreting recommendations.",
                "Re-read J8 forecast output before escalating governance review.",
                "Compare recommendation history longitudinally before treating a risk as persistent.",
            ],
            "recommended_monitoring_targets": [
                "identity_drift_score",
                "strategic_drift_score",
                "memory_drift_score",
                "systemic_drift_coupling_index",
                "cascade_risk_index",
                "forecast_risk_index",
                "civilizational_stability_index",
            ],
            "recommended_governance_checks": [
                "governance_consistency_checker",
                "constitutional_governance_supervisor",
                "constitutional_alert_system",
                "openness_preservation_supervisor",
                "closure_pressure_regulator",
            ],
            "governance_review_recommended": governance_review_recommended,
            "governance": {
                "recommendations_only": True,
                "observational_only": True,
                "no_direct_identity_modification": True,
                "no_direct_memory_modification": True,
                "no_direct_strategy_modification": True,
                "does_not_execute_actions": True,
                "does_not_authorize_mutation": True,
                "anti_closure_compliant": True,
            },
        }

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.latest_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            with self.history_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(result, ensure_ascii=False) + "\n")

        return result
