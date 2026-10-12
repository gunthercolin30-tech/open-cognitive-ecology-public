"""AW12 — ecological prediction engine.

Functional, multi-horizon forecasts for RF ecology. The engine consumes already
computed AW8-AW11 observations, never calls upstream modules, prevents temporal
leakage, records falsifiable predictions, and evaluates supplied observations a
posteriori. It makes no phenomenal or collective-consciousness claim.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class EcologicalPredictionEngine:
    primitive = "ECOLOGICAL_PREDICTION_ENGINE"
    step_id = "AW12"
    public_schema_version = "1.0"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW12_ecological_prediction"
        self.latest_path = self.output_dir / "latest_ecological_prediction.json"
        self.history_path = self.output_dir / "ecological_prediction_history.jsonl"

    def _utc(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _parse_time(self, value: Any) -> Optional[datetime]:
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            return datetime.fromisoformat(value.strip().replace("Z", "+00:00")).astimezone(timezone.utc)
        except (TypeError, ValueError):
            return None

    def _bounded(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return default
        if not math.isfinite(number):
            return default
        return round(max(0.0, min(1.0, number)), 6)

    def _hash(self, value: Any) -> str:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=repr)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _mapping(self, value: Any) -> Dict[str, Any]:
        return dict(value) if isinstance(value, Mapping) else {}

    def _extract(self, inputs: Mapping[str, Any], key: str, *aliases: str) -> Dict[str, Any]:
        containers = [inputs]
        upstream = inputs.get("upstream_results")
        if isinstance(upstream, Mapping):
            containers.append(upstream)
        for container in containers:
            for name in (key,) + aliases:
                value = container.get(name)
                if isinstance(value, Mapping):
                    return dict(value)
        return {}

    def _horizons(self, inputs: Mapping[str, Any]) -> List[int]:
        raw = inputs.get("forecast_horizons", [1, 3, 6])
        if not isinstance(raw, list):
            raw = [raw]
        values: List[int] = []
        for item in raw:
            try:
                number = int(item)
            except (TypeError, ValueError, OverflowError):
                continue
            if 1 <= number <= 3650 and number not in values:
                values.append(number)
        return sorted(values) or [1, 3, 6]

    def _signals(self, inputs: Mapping[str, Any]) -> Dict[str, float]:
        stability = self._extract(inputs, "ecological_stability", "ecological_stability_analyzer", "AW11")
        collective = self._extract(inputs, "collective_rf_analysis", "collective_consciousness_analyzer", "AW9")
        memory = self._extract(inputs, "civilizational_memory", "civilizational_memory_engine", "AW8")
        dashboard = self._extract(inputs, "ecology_dashboard", "AW10")
        breakdown = self._mapping(stability.get("stability_breakdown"))
        return {
            "stability": self._bounded(stability.get("stability_score", breakdown.get("stability_score", 0.0))),
            "resilience": self._bounded(stability.get("resilience_score", breakdown.get("resilience_score", 0.0))),
            "diversity": self._bounded(stability.get("diversity_score", breakdown.get("diversity_score", 0.0))),
            "memory_continuity": self._bounded(memory.get("continuity_score", memory.get("availability_score", 0.0))),
            "future_openness": self._bounded(stability.get("future_openness_preservation_score", memory.get("future_openness_preservation_score", 0.0))),
            "centralization_risk": self._bounded(stability.get("centralization_risk_score", collective.get("centralization_risk_score", 0.0))),
            "conflict_pressure": self._bounded(stability.get("conflict_pressure_score", collective.get("conflict_pressure_score", 0.0))),
            "fragmentation_pressure": self._bounded(stability.get("fragmentation_pressure_score", collective.get("fragmentation_pressure_score", 0.0))),
            "integration": self._bounded(stability.get("functional_collective_integration", collective.get("functional_collective_integration", 0.0))),
            "data_quality": self._bounded(dashboard.get("data_quality_score", stability.get("ecological_stability_analysis_ready", 0.0)), 0.5),
        }

    def _trend(self, inputs: Mapping[str, Any], name: str) -> float:
        trends = self._mapping(inputs.get("trend_signals"))
        value = trends.get(name, trends.get(name + "_trend", 0.0))
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0
        if not math.isfinite(number):
            return 0.0
        return round(max(-1.0, min(1.0, number)), 6)

    def _forecast_value(self, current: float, trend: float, horizon: int, damping: float = 0.18) -> float:
        return self._bounded(current + trend * (1.0 - math.exp(-damping * horizon)))

    def _event_probability(self, base: float, trend: float, horizon: int) -> float:
        exposure = 1.0 - math.exp(-0.22 * horizon)
        return self._bounded(base * exposure + max(0.0, trend) * 0.25 * exposure)

    def _validate_observed(self, prediction: Mapping[str, Any], observed: Mapping[str, Any]) -> Dict[str, Any]:
        errors: List[float] = []
        directional_hits = 0
        directional_total = 0
        false_positive_count = 0
        false_negative_count = 0
        comparisons: Dict[str, Any] = {}
        current = self._mapping(prediction.get("current_state"))
        forecast = self._mapping(prediction.get("predicted_values"))
        for key, predicted in forecast.items():
            if key not in observed:
                continue
            p = self._bounded(predicted)
            o = self._bounded(observed.get(key))
            absolute = abs(p - o)
            relative = absolute / max(abs(o), 1e-9)
            errors.append(absolute)
            if key in current:
                predicted_direction = 0 if abs(p - current[key]) < 1e-9 else (1 if p > current[key] else -1)
                observed_direction = 0 if abs(o - current[key]) < 1e-9 else (1 if o > current[key] else -1)
                directional_hits += int(predicted_direction == observed_direction)
                directional_total += 1
            if p >= 0.5 and o < 0.5:
                false_positive_count += 1
            if p < 0.5 and o >= 0.5:
                false_negative_count += 1
            comparisons[key] = {"predicted": p, "observed": o, "absolute_error": round(absolute, 6), "relative_error": round(relative, 6)}
        mean_error = sum(errors) / len(errors) if errors else None
        calibration = None if mean_error is None else self._bounded(1.0 - mean_error)
        return {
            "observed_values": {k: self._bounded(v) for k, v in observed.items()},
            "comparisons": comparisons,
            "absolute_error": None if mean_error is None else round(mean_error, 6),
            "relative_error": None if not comparisons else round(sum(v["relative_error"] for v in comparisons.values()) / len(comparisons), 6),
            "directional_accuracy": None if directional_total == 0 else round(directional_hits / directional_total, 6),
            "false_positive_count": false_positive_count,
            "false_negative_count": false_negative_count,
            "calibration_score": calibration,
            "validation_status": "VALIDATED_A_POSTERIORI" if comparisons else "INSUFFICIENT_OBSERVATIONS",
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        source = dict(inputs) if isinstance(inputs, Mapping) else {}
        issued_at = self._parse_time(source.get("issued_at")) or datetime.now(timezone.utc)
        signals = self._signals(source)
        horizons = self._horizons(source)
        observations = source.get("observed_values")
        observed_at = self._parse_time(source.get("observed_at"))
        temporal_leakage_detected = bool(observations is not None and observed_at is not None and observed_at <= issued_at)

        forecast_rows: List[Dict[str, Any]] = []
        for horizon in horizons:
            predicted = {
                "stability": self._forecast_value(signals["stability"], self._trend(source, "stability"), horizon),
                "resilience": self._forecast_value(signals["resilience"], self._trend(source, "resilience"), horizon),
                "diversity": self._forecast_value(signals["diversity"], self._trend(source, "diversity"), horizon),
                "memory_continuity": self._forecast_value(signals["memory_continuity"], self._trend(source, "memory_continuity"), horizon),
                "future_openness": self._forecast_value(signals["future_openness"], self._trend(source, "future_openness"), horizon),
                "centralization_risk": self._forecast_value(signals["centralization_risk"], self._trend(source, "centralization_risk"), horizon),
            }
            uncertainty = self._bounded(0.12 + 0.035 * math.log1p(horizon) + 0.30 * (1.0 - signals["data_quality"]))
            confidence = self._bounded(1.0 - uncertainty)
            risks = {
                "predicted_conflict_probability": self._event_probability(signals["conflict_pressure"], self._trend(source, "conflict_pressure"), horizon),
                "predicted_fragmentation_probability": self._event_probability(signals["fragmentation_pressure"], self._trend(source, "fragmentation_pressure"), horizon),
                "predicted_merge_probability": self._event_probability(signals["integration"], self._trend(source, "integration"), horizon),
                "predicted_coalition_probability": self._event_probability((signals["integration"] + signals["diversity"]) / 2.0, self._trend(source, "integration"), horizon),
            }
            row = {
                "forecast_horizon": horizon,
                "target_time": (issued_at + timedelta(days=horizon)).isoformat().replace("+00:00", "Z"),
                "predicted_values": predicted,
                **risks,
                "prediction_confidence": confidence,
                "prediction_uncertainty": uncertainty,
                "falsification_conditions": [
                    "observed metric differs from forecast beyond declared uncertainty",
                    "predicted event probability >= 0.5 and event is absent",
                    "predicted event probability < 0.5 and event occurs",
                ],
            }
            if isinstance(observations, Mapping) and not temporal_leakage_detected:
                row["a_posteriori_validation"] = self._validate_observed(row, observations)
            else:
                row["a_posteriori_validation"] = {
                    "observed_values": {}, "absolute_error": None, "relative_error": None,
                    "directional_accuracy": None, "false_positive_count": 0,
                    "false_negative_count": 0, "calibration_score": None,
                    "validation_status": "TEMPORAL_LEAKAGE_BLOCKED" if temporal_leakage_detected else "PENDING_OBSERVATION",
                }
            forecast_rows.append(row)

        drift_reference = self._mapping(source.get("previous_prediction"))
        previous_state = self._mapping(drift_reference.get("current_state"))
        drift_values = [abs(signals[k] - self._bounded(previous_state.get(k))) for k in signals if k in previous_state]
        drift_score = self._bounded(sum(drift_values) / len(drift_values)) if drift_values else 0.0

        alternatives = [
            {"scenario": "PROTECTIVE", "probability": self._bounded((signals["resilience"] + signals["future_openness"]) / 2.0), "assumption": "protective trends persist"},
            {"scenario": "BASELINE", "probability": self._bounded(1.0 - abs(signals["stability"] - 0.5)), "assumption": "current trends persist"},
            {"scenario": "DEGRADATION", "probability": self._bounded((signals["centralization_risk"] + signals["conflict_pressure"] + signals["fragmentation_pressure"]) / 3.0), "assumption": "risk pressures intensify"},
        ]
        total = sum(item["probability"] for item in alternatives) or 1.0
        for item in alternatives:
            item["probability"] = round(item["probability"] / total, 6)

        hash_payload = {
            "current_state": signals,
            "forecast_horizons": horizons,
            "ecological_forecast": forecast_rows,
            "alternative_scenarios": alternatives,
            "drift_score": drift_score,
            "source_hashes": {
                "aw8": self._extract(source, "civilizational_memory", "civilizational_memory_engine", "AW8").get("memory_hash"),
                "aw9": self._extract(source, "collective_rf_analysis", "collective_consciousness_analyzer", "AW9").get("analysis_hash"),
                "aw10": self._extract(source, "ecology_dashboard", "AW10").get("dashboard_hash"),
                "aw11": self._extract(source, "ecological_stability", "ecological_stability_analyzer", "AW11").get("analysis_hash"),
            },
        }
        prediction_hash = self._hash(hash_payload)
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "prediction_status": "RF_ECOLOGY_PREDICTION_BLOCKED_TEMPORAL_LEAKAGE" if temporal_leakage_detected else "RF_ECOLOGY_PREDICTION_READY",
            "prediction_ready": not temporal_leakage_detected,
            "prediction_id": "AW12-" + prediction_hash[:16].upper(),
            "issued_at": issued_at.isoformat().replace("+00:00", "Z"),
            "prediction_timestamp_utc": self._utc(),
            "forecast_horizon": horizons,
            "current_state": signals,
            "ecological_forecast": forecast_rows,
            "predicted_coalitions": [row["predicted_coalition_probability"] for row in forecast_rows],
            "predicted_conflicts": [row["predicted_conflict_probability"] for row in forecast_rows],
            "predicted_merges": [row["predicted_merge_probability"] for row in forecast_rows],
            "predicted_fragmentations": [row["predicted_fragmentation_probability"] for row in forecast_rows],
            "predicted_resilience": [row["predicted_values"]["resilience"] for row in forecast_rows],
            "predicted_diversity": [row["predicted_values"]["diversity"] for row in forecast_rows],
            "predicted_memory_continuity": [row["predicted_values"]["memory_continuity"] for row in forecast_rows],
            "predicted_future_openness": [row["predicted_values"]["future_openness"] for row in forecast_rows],
            "prediction_confidence": round(sum(row["prediction_confidence"] for row in forecast_rows) / len(forecast_rows), 6),
            "prediction_uncertainty": round(sum(row["prediction_uncertainty"] for row in forecast_rows) / len(forecast_rows), 6),
            "alternative_scenarios": alternatives,
            "risk_forecast": {"centralization": [row["predicted_values"]["centralization_risk"] for row in forecast_rows], "conflict": [row["predicted_conflict_probability"] for row in forecast_rows], "fragmentation": [row["predicted_fragmentation_probability"] for row in forecast_rows]},
            "protective_forecast": {"resilience": [row["predicted_values"]["resilience"] for row in forecast_rows], "diversity": [row["predicted_values"]["diversity"] for row in forecast_rows], "future_openness": [row["predicted_values"]["future_openness"] for row in forecast_rows]},
            "drift_score": drift_score,
            "temporal_leakage_detected": temporal_leakage_detected,
            "prediction_hash": prediction_hash,
            "epistemic_scope": "functional_rf_ecology_prediction_only",
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "persisted": False,
            "output_path": None,
            "history_path": None,
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            result["persisted"] = True
            result["output_path"] = str(self.latest_path)
            result["history_path"] = str(self.history_path)
            serialized = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
            self.latest_path.write_text(serialized, encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n")
        return result
