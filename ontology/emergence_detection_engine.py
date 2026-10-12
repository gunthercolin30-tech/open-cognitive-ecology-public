from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


class EmergenceDetectionEngine:
    """I6 - Emergence Detection Engine.

    Cette primitive détecte l'apparition fonctionnelle de structures,
    capacités ou régimes nouveaux à partir d'indicateurs pré-calculés ou
    d'une série d'observations. Elle complète I1-I5 en produisant des
    indicateurs mesurables d'émergence : emergence_probability,
    novelty_index, new_structure_count et capability_emergence_score.
    Elle ne formule aucune affirmation de subjectivité phénoménale.
    """

    primitive = "emergence_detection_engine"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "paradigm_surveillance"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, float(value)))

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            return float(value)
        return None

    @staticmethod
    def _mean(values: Iterable[float]) -> float:
        vals = [float(v) for v in values if math.isfinite(float(v))]
        return mean(vals) if vals else 0.0

    @staticmethod
    def _std(values: Iterable[float]) -> float:
        vals = [float(v) for v in values if math.isfinite(float(v))]
        return pstdev(vals) if len(vals) > 1 else 0.0

    def _extract_numeric(self, obj: Any, prefix: str = "") -> Dict[str, float]:
        projection: Dict[str, float] = {}
        if isinstance(obj, dict):
            for key, value in obj.items():
                name = f"{prefix}.{key}" if prefix else str(key)
                numeric = self._to_float(value)
                if numeric is not None:
                    projection[name] = numeric
                elif isinstance(value, dict):
                    projection.update(self._extract_numeric(value, name))
        return projection

    def _flatten_keys(self, obj: Any, prefix: str = "") -> Set[str]:
        keys: Set[str] = set()
        if isinstance(obj, dict):
            for key, value in obj.items():
                name = f"{prefix}.{key}" if prefix else str(key)
                keys.add(name)
                if isinstance(value, dict):
                    keys.update(self._flatten_keys(value, name))
        return keys

    def _normalize_inputs(self, inputs: Any) -> Tuple[Dict[str, Any], List[Dict[str, Any]], int, str]:
        if inputs is None:
            return {}, [], 0, "empty"
        if isinstance(inputs, list):
            observations = [x for x in inputs if isinstance(x, dict)]
            return {}, observations, len(observations), "observation_series"
        if isinstance(inputs, dict):
            if "observations" in inputs and isinstance(inputs["observations"], list):
                observations = [x for x in inputs["observations"] if isinstance(x, dict)]
                data = dict(inputs)
                data.pop("observations", None)
                return data, observations, len(observations), "mixed_inputs_with_observations"
            return inputs, [], 0, "precomputed_indicators"
        return {}, [], 0, "unsupported_input"

    def _split_series(self, observations: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not observations:
            return [], []
        midpoint = max(1, len(observations) // 2)
        return observations[:midpoint], observations[midpoint:] or observations[-1:]

    def _aggregate_numeric(self, rows: List[Dict[str, Any]]) -> Dict[str, float]:
        values_by_key: Dict[str, List[float]] = {}
        for row in rows:
            for key, value in self._extract_numeric(row).items():
                values_by_key.setdefault(key, []).append(value)
        return {key: self._mean(vals) for key, vals in values_by_key.items()}

    def _run_i1_i5(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        if not observations:
            return results
        try:
            from ontology.paradigm_shift_signal_extractor import ParadigmShiftSignalExtractor
            results["i1"] = ParadigmShiftSignalExtractor(root=self.root).step(observations, persist=False)
        except Exception as exc:  # pragma: no cover - defensive integration
            results["i1_error"] = repr(exc)
        try:
            from ontology.regime_transition_detector import RegimeTransitionDetector
            results["i2"] = RegimeTransitionDetector(root=self.root).step(observations, persist=False)
        except Exception as exc:  # pragma: no cover
            results["i2_error"] = repr(exc)
        try:
            from ontology.structural_break_analyzer import StructuralBreakAnalyzer
            results["i3"] = StructuralBreakAnalyzer(root=self.root).step(observations, persist=False)
        except Exception as exc:  # pragma: no cover
            results["i3_error"] = repr(exc)
        try:
            from ontology.constraint_regime_comparator import ConstraintRegimeComparator
            first, second = self._split_series(observations)
            results["i4"] = ConstraintRegimeComparator(root=self.root).step(
                self._aggregate_numeric(first), self._aggregate_numeric(second), persist=False
            )
        except Exception as exc:  # pragma: no cover
            results["i4_error"] = repr(exc)
        try:
            from ontology.paradigm_classification_engine import ParadigmClassificationEngine
            results["i5"] = ParadigmClassificationEngine(root=self.root).step(observations, persist=False)
        except Exception as exc:  # pragma: no cover
            results["i5_error"] = repr(exc)
        return results

    def _indicator(self, data: Dict[str, Any], direct: str, nested: Tuple[str, str], default: float = 0.0) -> float:
        value = self._to_float(data.get(direct))
        if value is not None:
            return self._clamp(value)
        container = data.get(nested[0])
        if isinstance(container, dict):
            value = self._to_float(container.get(nested[1]))
            if value is not None:
                return self._clamp(value)
        return default

    def _series_emergence_features(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not observations:
            return {
                "new_structure_count": 0,
                "new_metric_count": 0,
                "late_only_keys": [],
                "numeric_growth_score": 0.0,
                "variance_novelty_score": 0.0,
            }

        first, second = self._split_series(observations)
        first_keys: Set[str] = set()
        second_keys: Set[str] = set()
        for row in first:
            first_keys.update(self._flatten_keys(row))
        for row in second:
            second_keys.update(self._flatten_keys(row))
        late_only = sorted(second_keys - first_keys)

        first_agg = self._aggregate_numeric(first)
        second_agg = self._aggregate_numeric(second)
        common = sorted(set(first_agg) & set(second_agg))

        growth_scores: List[float] = []
        variance_scores: List[float] = []
        for key in common:
            a = first_agg[key]
            b = second_agg[key]
            denom = max(abs(a), abs(b), 1.0)
            growth_scores.append(abs(b - a) / denom)

            first_vals = [self._extract_numeric(row).get(key) for row in first]
            second_vals = [self._extract_numeric(row).get(key) for row in second]
            fv = [v for v in first_vals if v is not None]
            sv = [v for v in second_vals if v is not None]
            variance_scores.append(abs(self._std(sv) - self._std(fv)))

        capability_like = [k for k in late_only if any(token in k.lower() for token in ("capability", "module", "primitive", "structure", "skill", "sensor", "node", "discovery"))]

        return {
            "new_structure_count": len(late_only),
            "new_metric_count": len(late_only),
            "late_only_keys": late_only[:20],
            "capability_like_new_keys": capability_like[:20],
            "numeric_growth_score": round(self._clamp(self._mean(growth_scores)), 6),
            "variance_novelty_score": round(self._clamp(self._mean(variance_scores)), 6),
        }

    def _compute_scores(self, data: Dict[str, Any], observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        if observations:
            data = dict(data)
            data.update(self._run_i1_i5(observations))

        features = self._series_emergence_features(observations)
        metrics = self._extract_numeric(data)

        novelty_candidates = [
            value for key, value in metrics.items()
            if any(token in key.lower() for token in ("novelty", "new", "discovery", "innovation", "emergence", "growth", "expansion"))
        ]
        capability_candidates = [
            value for key, value in metrics.items()
            if any(token in key.lower() for token in ("capability", "module", "primitive", "structure", "discovery", "self_extension"))
        ]

        direct_novelty = self._indicator(data, "novelty_index", ("novelty_emergence", "novelty_index"), default=-1.0)
        direct_emergence = self._indicator(data, "emergence_probability", ("regime_emergence", "emergence_probability"), default=-1.0)
        direct_capability = self._indicator(data, "capability_emergence_score", ("open_ended_capability_discovery_engine", "capability_emergence_score"), default=-1.0)

        novelty_from_metrics = self._clamp(self._mean(novelty_candidates)) if novelty_candidates else 0.0
        capability_from_metrics = self._clamp(self._mean(capability_candidates)) if capability_candidates else 0.0

        structure_signal = self._clamp(features["new_structure_count"] / 10.0)
        growth_signal = self._clamp(features["numeric_growth_score"])
        variance_signal = self._clamp(features["variance_novelty_score"])
        shift_signal = self._indicator(data, "shift_signal_strength", ("i1", "shift_signal_strength"))
        transition_probability = self._indicator(data, "transition_probability", ("i2", "transition_probability"))
        current_paradigm = ""
        i5 = data.get("i5")
        if isinstance(i5, dict):
            current_paradigm = str(i5.get("current_paradigm", ""))
        if isinstance(data.get("current_paradigm"), str):
            current_paradigm = str(data.get("current_paradigm"))
        expansion_bonus = 0.18 if current_paradigm == "expansion" else 0.0

        novelty_index = self._clamp(
            (direct_novelty if direct_novelty >= 0 else 0.0) * 0.35
            + novelty_from_metrics * 0.20
            + structure_signal * 0.18
            + growth_signal * 0.15
            + variance_signal * 0.07
            + expansion_bonus
        )
        if direct_novelty < 0 and not novelty_candidates and not observations:
            novelty_index = 0.0

        capability_emergence_score = self._clamp(
            (direct_capability if direct_capability >= 0 else 0.0) * 0.40
            + capability_from_metrics * 0.22
            + self._clamp(len(features.get("capability_like_new_keys", [])) / 5.0) * 0.25
            + structure_signal * 0.13
        )
        if direct_capability < 0 and not capability_candidates and not observations:
            capability_emergence_score = 0.0

        emergence_probability = self._clamp(
            (direct_emergence if direct_emergence >= 0 else 0.0) * 0.32
            + novelty_index * 0.28
            + capability_emergence_score * 0.18
            + transition_probability * 0.08
            + shift_signal * 0.06
            + growth_signal * 0.08
        )
        if direct_emergence < 0 and direct_novelty < 0 and not novelty_candidates and not observations:
            emergence_probability = 0.0

        emergence_detected = emergence_probability >= 0.35 or novelty_index >= 0.45 or capability_emergence_score >= 0.45
        emergence_status = "no_emergence_detected"
        if emergence_detected and emergence_probability >= 0.70:
            emergence_status = "strong_emergence"
        elif emergence_detected:
            emergence_status = "emergence_watch"

        confidence_basis = [emergence_probability, novelty_index, capability_emergence_score, structure_signal]
        detection_confidence = self._clamp(0.45 * max(confidence_basis) + 0.55 * self._mean(confidence_basis))

        return {
            "data": data,
            "features": features,
            "emergence_probability": round(emergence_probability, 6),
            "novelty_index": round(novelty_index, 6),
            "new_structure_count": int(features["new_structure_count"]),
            "capability_emergence_score": round(capability_emergence_score, 6),
            "emergence_detected": bool(emergence_detected),
            "emergence_status": emergence_status,
            "detection_confidence": round(detection_confidence, 6),
        }

    def step(self, inputs: Any = None, persist: bool = True) -> Dict[str, Any]:
        data, observations, observation_count, input_mode = self._normalize_inputs(inputs)
        scores = self._compute_scores(data, observations)

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "input_mode": input_mode,
            "observation_count": observation_count,
            "emergence_probability": scores["emergence_probability"],
            "novelty_index": scores["novelty_index"],
            "new_structure_count": scores["new_structure_count"],
            "capability_emergence_score": scores["capability_emergence_score"],
            "emergence_detected": scores["emergence_detected"],
            "emergence_status": scores["emergence_status"],
            "detection_confidence": scores["detection_confidence"],
            "emergence_features": scores["features"],
            "emergence_detection_ready": True,
            "epistemic_status": "functional_indicators_only",
            "governance": {
                "non_closure_preserved": True,
                "phenomenal_subjectivity_claimed": False,
                "traceable": True,
                "reversible": True,
            },
        }

        if persist:
            latest = self.output_dir / "latest_emergence_detection.json"
            archive = self.output_dir / f"emergence_detection_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            payload = json.dumps(result, indent=2, ensure_ascii=False)
            latest.write_text(payload, encoding="utf-8")
            archive.write_text(payload, encoding="utf-8")
            result["state_path"] = str(latest)
            result["archive_path"] = str(archive)

        return result


__all__ = ["EmergenceDetectionEngine"]
