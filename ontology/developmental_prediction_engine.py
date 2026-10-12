"""AV8 — functional developmental prediction engine.

Forecasts future developmental stages from already-computed AV7 classification
and AV1–AV6 longitudinal evidence. It never invokes or recomputes upstream
modules and never infers phenomenal consciousness.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"


class DevelopmentalPredictionEngine:
    primitive = "DEVELOPMENTAL_PREDICTION_ENGINE"
    step_id = "AV8"
    public_schema_version = "1.0"
    output_dir = ROOT / "developmental_science" / "AV8_developmental_prediction_engine"

    STAGES = (
        "PRE_GENESIS", "GENESIS", "MATURATION", "SPECIALIZATION",
        "BIFURCATION", "DEGENERATION", "RECOVERY",
        "STABLE_DEVELOPED_REGIME", "HYBRID_STAGE", "UNDETERMINED",
    )

    DEFAULTS = {
        "short_horizon": 1,
        "medium_horizon": 3,
        "long_horizon": 6,
        "minimum_input_quality": 0.45,
        "minimum_prediction_confidence": 0.35,
        "scenario_floor": 0.05,
        "uncertainty_penalty": 0.35,
    }

    def _clip(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        if not math.isfinite(number):
            number = default
        return max(0.0, min(1.0, number))

    def _stable_hash(self, value: Any) -> str:
        raw = json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _mapping(self, inputs: Mapping[str, Any], *names: str) -> Dict[str, Any]:
        for name in names:
            value = inputs.get(name)
            if isinstance(value, Mapping):
                return dict(value)
        upstream = inputs.get("upstream_results")
        if isinstance(upstream, Mapping):
            for name in names:
                value = upstream.get(name)
                if isinstance(value, Mapping):
                    return dict(value)
        return {}

    def _list(self, inputs: Mapping[str, Any], *names: str) -> List[Any]:
        for name in names:
            value = inputs.get(name)
            if isinstance(value, list):
                return list(value)
        return []

    def _stage_context(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        stage = self._mapping(
            inputs,
            "developmental_stage_result",
            "stage_result",
            "av7_result",
            "developmental_stage_classifier",
            "AV7",
        )
        if stage:
            return stage
        direct_stage = str(inputs.get("developmental_stage", "")).upper()
        if direct_stage in self.STAGES:
            return {
                "developmental_stage": direct_stage,
                "stage_confidence": self._clip(
                    inputs.get("stage_confidence"), 0.5
                ),
                "stage_probabilities": dict(
                    inputs.get("stage_probabilities", {})
                    if isinstance(inputs.get("stage_probabilities"), Mapping)
                    else {}
                ),
                "evidence_quality_score": self._clip(
                    inputs.get("evidence_quality_score"), 0.5
                ),
            }
        return {}

    def _trend_value(self, trends: Mapping[str, Any], name: str) -> float:
        aliases = {
            "growth": ("growth", "growth_trend", "maturation_trend", "developmental_growth"),
            "stability": ("stability", "stability_trend", "plateau", "persistence"),
            "bifurcation": ("bifurcation", "bifurcation_risk", "branching_pressure"),
            "degeneration": ("degeneration", "degeneration_risk", "decline", "regression"),
            "recovery": ("recovery", "recovery_trend", "restoration", "resilience"),
            "specialization": ("specialization", "specialization_trend", "differentiation"),
        }
        for key in aliases[name]:
            if key in trends:
                return self._clip(trends.get(key), 0.0)
        return 0.0

    def _derive_trends(
        self,
        inputs: Mapping[str, Any],
        stage: Mapping[str, Any],
    ) -> Tuple[Dict[str, float], List[str]]:
        supplied = self._mapping(inputs, "trends", "longitudinal_trends", "trend_signals")
        trajectory = self._list(
            inputs, "trajectory", "trajectories", "developmental_history", "stage_history"
        )
        warnings: List[str] = []
        trends = {
            name: self._trend_value(supplied, name)
            for name in (
                "growth", "stability", "bifurcation",
                "degeneration", "recovery", "specialization",
            )
        }

        # Derive conservative signals from ordered records when explicit trends
        # are absent. No upstream module is called.
        numeric_series: List[float] = []
        stage_series: List[str] = []
        for item in trajectory:
            if not isinstance(item, Mapping):
                continue
            for key in (
                "developmental_score", "stage_confidence",
                "maturation_score", "specialization_strength",
            ):
                if key in item:
                    numeric_series.append(self._clip(item.get(key), 0.0))
                    break
            candidate = str(
                item.get("developmental_stage")
                or item.get("stage")
                or ""
            ).upper()
            if candidate in self.STAGES:
                stage_series.append(candidate)

        if len(numeric_series) >= 2:
            delta = numeric_series[-1] - numeric_series[0]
            if delta > 0:
                trends["growth"] = max(trends["growth"], self._clip(abs(delta) * 2.0))
            elif delta < 0:
                trends["degeneration"] = max(
                    trends["degeneration"], self._clip(abs(delta) * 2.0)
                )
            if max(numeric_series) - min(numeric_series) <= 0.05:
                trends["stability"] = max(trends["stability"], 0.75)

        if len(stage_series) >= 2:
            if stage_series[-1] == stage_series[-2]:
                trends["stability"] = max(trends["stability"], 0.72)
            if "BIFURCATION" in stage_series[-2:]:
                trends["bifurcation"] = max(trends["bifurcation"], 0.80)
            if stage_series[-1] == "DEGENERATION":
                trends["degeneration"] = max(trends["degeneration"], 0.85)
            if stage_series[-1] == "RECOVERY":
                trends["recovery"] = max(trends["recovery"], 0.85)

        current = str(stage.get("developmental_stage", "")).upper()
        if current == "BIFURCATION":
            trends["bifurcation"] = max(trends["bifurcation"], 0.80)
        elif current == "DEGENERATION":
            trends["degeneration"] = max(trends["degeneration"], 0.80)
        elif current == "RECOVERY":
            trends["recovery"] = max(trends["recovery"], 0.80)
        elif current == "STABLE_DEVELOPED_REGIME":
            trends["stability"] = max(trends["stability"], 0.78)

        if not supplied and not trajectory:
            warnings.append("no_longitudinal_trends_or_trajectory")
        return {k: round(v, 6) for k, v in trends.items()}, warnings

    def _base_transitions(self, current: str) -> Dict[str, float]:
        table = {
            "PRE_GENESIS": {"PRE_GENESIS": 0.45, "GENESIS": 0.55},
            "GENESIS": {"GENESIS": 0.30, "MATURATION": 0.60, "DEGENERATION": 0.10},
            "MATURATION": {
                "MATURATION": 0.25, "SPECIALIZATION": 0.45,
                "STABLE_DEVELOPED_REGIME": 0.20, "DEGENERATION": 0.10,
            },
            "SPECIALIZATION": {
                "SPECIALIZATION": 0.25, "STABLE_DEVELOPED_REGIME": 0.45,
                "BIFURCATION": 0.20, "DEGENERATION": 0.10,
            },
            "BIFURCATION": {
                "BIFURCATION": 0.20, "SPECIALIZATION": 0.25,
                "STABLE_DEVELOPED_REGIME": 0.30, "DEGENERATION": 0.25,
            },
            "DEGENERATION": {
                "DEGENERATION": 0.45, "RECOVERY": 0.40,
                "STABLE_DEVELOPED_REGIME": 0.10, "UNDETERMINED": 0.05,
            },
            "RECOVERY": {
                "RECOVERY": 0.30, "STABLE_DEVELOPED_REGIME": 0.45,
                "SPECIALIZATION": 0.15, "DEGENERATION": 0.10,
            },
            "STABLE_DEVELOPED_REGIME": {
                "STABLE_DEVELOPED_REGIME": 0.65,
                "BIFURCATION": 0.20, "DEGENERATION": 0.15,
            },
            "HYBRID_STAGE": {
                "HYBRID_STAGE": 0.30, "UNDETERMINED": 0.25,
                "STABLE_DEVELOPED_REGIME": 0.20,
                "DEGENERATION": 0.15, "RECOVERY": 0.10,
            },
            "UNDETERMINED": {"UNDETERMINED": 1.0},
        }
        return dict(table.get(current, table["UNDETERMINED"]))

    def _apply_trends(
        self, probabilities: Dict[str, float], trends: Mapping[str, float]
    ) -> Dict[str, float]:
        adjustments = {
            "growth": {
                "GENESIS": 0.15, "MATURATION": 0.20,
                "SPECIALIZATION": 0.18, "STABLE_DEVELOPED_REGIME": 0.15,
            },
            "stability": {
                "STABLE_DEVELOPED_REGIME": 0.30,
                "MATURATION": 0.08, "SPECIALIZATION": 0.08,
            },
            "bifurcation": {"BIFURCATION": 0.42, "DEGENERATION": 0.08},
            "degeneration": {"DEGENERATION": 1.20, "UNDETERMINED": 0.08},
            "recovery": {"RECOVERY": 1.20, "STABLE_DEVELOPED_REGIME": 0.18},
            "specialization": {
                "SPECIALIZATION": 0.30, "STABLE_DEVELOPED_REGIME": 0.15,
            },
        }
        result = {stage: max(0.0, float(value)) for stage, value in probabilities.items()}
        for trend_name, stage_weights in adjustments.items():
            signal = self._clip(trends.get(trend_name), 0.0)
            for stage_name, weight in stage_weights.items():
                result[stage_name] = result.get(stage_name, 0.0) + signal * weight

        total = sum(result.values())
        if total <= 0:
            return {"UNDETERMINED": 1.0}
        return {
            key: round(value / total, 6)
            for key, value in sorted(result.items())
            if value > 0
        }

    def _forecast_horizon(
        self, confidence: float, uncertainty: float, config: Mapping[str, Any]
    ) -> Dict[str, Any]:
        if confidence >= 0.75 and uncertainty <= 0.25:
            windows = int(config["long_horizon"])
            label = "LONG"
        elif confidence >= 0.50 and uncertainty <= 0.50:
            windows = int(config["medium_horizon"])
            label = "MEDIUM"
        else:
            windows = int(config["short_horizon"])
            label = "SHORT"
        return {
            "label": label,
            "windows": max(1, windows),
            "unit": "developmental_observation_window",
        }

    def step(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        config = dict(self.DEFAULTS)
        supplied_config = inputs.get("config")
        if isinstance(supplied_config, Mapping):
            for key in config:
                if key in supplied_config:
                    if "horizon" in key:
                        try:
                            horizon_value = float(supplied_config[key])
                            if math.isfinite(horizon_value):
                                config[key] = max(1, int(horizon_value))
                        except (TypeError, ValueError, OverflowError):
                            pass
                    else:
                        config[key] = self._clip(
                            supplied_config[key], config[key]
                        )

        stage = self._stage_context(inputs)
        current = str(stage.get("developmental_stage", "")).upper()
        if current not in self.STAGES:
            current = "UNDETERMINED"

        stage_confidence = self._clip(stage.get("stage_confidence"), 0.0)
        evidence_quality = self._clip(
            stage.get("evidence_quality_score", stage.get("data_quality_score")),
            stage_confidence,
        )
        stage_probabilities = (
            dict(stage.get("stage_probabilities"))
            if isinstance(stage.get("stage_probabilities"), Mapping)
            else {}
        )

        trends, warnings = self._derive_trends(inputs, stage)
        base = self._base_transitions(current)
        probabilities = self._apply_trends(base, trends)

        ranked = sorted(
            probabilities.items(), key=lambda item: (-item[1], item[0])
        )
        predicted_stage = ranked[0][0] if ranked else "UNDETERMINED"
        top_probability = ranked[0][1] if ranked else 0.0
        second_probability = ranked[1][1] if len(ranked) > 1 else 0.0

        input_completeness = (
            1.0 if stage
            else 0.0
        )
        trend_coverage = sum(1 for value in trends.values() if value > 0) / len(trends)
        ambiguity = self._clip(1.0 - max(0.0, top_probability - second_probability))
        uncertainty = self._clip(
            0.35 * (1.0 - stage_confidence)
            + 0.30 * (1.0 - evidence_quality)
            + 0.20 * ambiguity
            + 0.15 * (1.0 - trend_coverage)
        )
        confidence = self._clip(
            (0.38 * stage_confidence)
            + (0.27 * evidence_quality)
            + (0.20 * top_probability)
            + (0.15 * trend_coverage)
            - (config["uncertainty_penalty"] * uncertainty)
        )

        if current == "UNDETERMINED" or not stage:
            predicted_stage = "UNDETERMINED"
            probabilities = {"UNDETERMINED": 1.0}
            confidence = 0.0
            uncertainty = 1.0
            warnings.append("missing_or_undetermined_AV7_stage")

        horizon = self._forecast_horizon(confidence, uncertainty, config)
        alternatives = []
        for rank, (candidate, probability) in enumerate(
            sorted(probabilities.items(), key=lambda item: (-item[1], item[0]))[:4],
            start=1,
        ):
            alternatives.append({
                "rank": rank,
                "stage": candidate,
                "probability": round(probability, 6),
                "scenario_type": (
                    "PRIMARY" if rank == 1
                    else "ALTERNATIVE"
                ),
                "drivers": [
                    name for name, value in sorted(trends.items())
                    if value >= 0.35
                ],
            })

        assumptions = [
            "AV7 classification is treated as an observed functional state.",
            "AV1–AV7 results are consumed without upstream recomputation.",
            "Trend signals remain approximately valid over the forecast horizon.",
            "No unobserved external perturbation dominates the next observation window.",
            "Predictions concern functional developmental states only.",
        ]
        falsification_conditions = [
            {
                "id": "AV8-F1",
                "condition": "Observed next stage differs from predicted_stage.",
                "evaluation": "compare_observed_stage_to_primary_prediction",
            },
            {
                "id": "AV8-F2",
                "condition": "Observed stage falls outside all reported alternative_scenarios.",
                "evaluation": "out_of_scenario_set",
            },
            {
                "id": "AV8-F3",
                "condition": "Calibration error exceeds 0.25 over at least 10 forecasts.",
                "evaluation": "longitudinal_probability_calibration",
            },
            {
                "id": "AV8-F4",
                "condition": "Prediction changes under semantically identical input ordering.",
                "evaluation": "determinism_violation",
            },
        ]

        condition_results = {
            "av7_stage_present": bool(stage),
            "current_stage_valid": current in self.STAGES and current != "UNDETERMINED",
            "input_quality_sufficient": evidence_quality >= config["minimum_input_quality"],
            "prediction_confidence_sufficient": confidence >= config["minimum_prediction_confidence"],
            "multiple_scenarios_reported": len(alternatives) >= 2,
            "uncertainty_quantified": 0.0 <= uncertainty <= 1.0,
            "falsification_conditions_present": bool(falsification_conditions),
            "no_upstream_recalculation": True,
        }
        missing_conditions = [
            key for key, value in condition_results.items() if not value
        ]

        hash_payload = {
            "current_stage": current,
            "stage_confidence": stage_confidence,
            "evidence_quality": evidence_quality,
            "stage_probabilities": stage_probabilities,
            "trends": trends,
            "probabilities": probabilities,
            "horizon": horizon,
            "config": config,
            "trajectory": self._list(
                inputs, "trajectory", "trajectories",
                "developmental_history", "stage_history",
            ),
        }

        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "prediction_status": "DEVELOPMENTAL_PREDICTION_READY",
            "current_stage": current,
            "predicted_stage": predicted_stage,
            "forecast_horizon": horizon,
            "alternative_scenarios": alternatives,
            "prediction_confidence": round(confidence, 6),
            "prediction_uncertainty": round(uncertainty, 6),
            "prediction_probabilities": probabilities,
            "prediction_hash": self._stable_hash(hash_payload),
            "trend_signals": trends,
            "assumptions": assumptions,
            "falsification_conditions": falsification_conditions,
            "input_quality_score": round(evidence_quality, 6),
            "input_completeness": input_completeness,
            "condition_results": condition_results,
            "missing_conditions": missing_conditions,
            "warnings": sorted(set(warnings)),
            "audit_trace": {
                "method": "functional_stage_transition_scenario_forecast",
                "upstream_recalculation_performed": False,
                "scenario_count": len(alternatives),
                "trajectory_record_count": len(
                    self._list(
                        inputs, "trajectory", "trajectories",
                        "developmental_history", "stage_history",
                    )
                ),
                "trend_coverage": round(trend_coverage, 6),
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
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_developmental_prediction.json"
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
    return DevelopmentalPredictionEngine().step(inputs=inputs, persist=persist)
