from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple


class ParadigmClassificationEngine:
    """I5 - Paradigm Classification Engine.

    Cette primitive agrège les indicateurs I1-I4 ou une série d'observations
    métriques pour classifier l'état paradigmatique courant selon une taxonomie
    fonctionnelle : stability, transition, rupture, expansion, collapse.
    Elle produit uniquement des indicateurs mesurables et ne formule aucune
    affirmation de subjectivité phénoménale.
    """

    primitive = "paradigm_classification_engine"
    allowed_paradigms = ("stability", "transition", "rupture", "expansion", "collapse")

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

    def _split_series(self, observations: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if not observations:
            return {}, {}
        midpoint = max(1, len(observations) // 2)
        first = observations[:midpoint]
        second = observations[midpoint:] or observations[-1:]
        keys = sorted(set().union(*(o.keys() for o in observations if isinstance(o, dict))))

        def aggregate(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
            out: Dict[str, Any] = {}
            for key in keys:
                vals: List[float] = []
                for row in rows:
                    numeric = self._to_float(row.get(key)) if isinstance(row, dict) else None
                    if numeric is not None:
                        vals.append(numeric)
                if vals:
                    out[key] = self._mean(vals)
            return out

        return aggregate(first), aggregate(second)

    def _run_i1_i4(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
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
            prev, curr = self._split_series(observations)
            results["i4"] = ConstraintRegimeComparator(root=self.root).step(prev, curr, persist=False)
        except Exception as exc:  # pragma: no cover
            results["i4_error"] = repr(exc)

        return results

    def _normalize_inputs(self, inputs: Any) -> Tuple[Dict[str, Any], int, str]:
        if inputs is None:
            return {}, 0, "empty"

        if isinstance(inputs, list):
            observations = [x for x in inputs if isinstance(x, dict)]
            integrated = self._run_i1_i4(observations)
            return integrated, len(observations), "observation_series"

        if isinstance(inputs, dict):
            if "observations" in inputs and isinstance(inputs["observations"], list):
                observations = [x for x in inputs["observations"] if isinstance(x, dict)]
                integrated = dict(inputs)
                integrated.update(self._run_i1_i4(observations))
                return integrated, len(observations), "mixed_inputs_with_observations"
            return inputs, 0, "precomputed_indicators"

        return {}, 0, "unsupported_input"

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

    def _latest_metric(self, data: Dict[str, Any], keys: Tuple[str, ...], default: Optional[float] = None) -> Optional[float]:
        for key in keys:
            value = self._to_float(data.get(key))
            if value is not None:
                return self._clamp(value)
        return default

    def _score_paradigms(self, data: Dict[str, Any]) -> Dict[str, float]:
        shift_signal_strength = self._indicator(data, "shift_signal_strength", ("i1", "shift_signal_strength"))
        transition_probability = self._indicator(data, "transition_probability", ("i2", "transition_probability"))
        break_significance = self._indicator(data, "break_significance", ("i3", "break_significance"))
        constraint_shift_index = self._indicator(data, "constraint_shift_index", ("i4", "constraint_shift_index"))
        constraint_distance = self._indicator(data, "constraint_regime_distance", ("i4", "constraint_regime_distance"))

        metrics = self._extract_numeric(data)
        viability_values = [v for k, v in metrics.items() if "viability" in k.lower()]
        openness_values = [v for k, v in metrics.items() if "openness" in k.lower() or "open_ended" in k.lower()]
        error_values = [v for k, v in metrics.items() if "error" in k.lower()]
        risk_values = [v for k, v in metrics.items() if "risk" in k.lower()]
        growth_values = [v for k, v in metrics.items() if "growth" in k.lower() or "novelty" in k.lower() or "emergence" in k.lower()]

        viability = self._clamp(self._mean(viability_values)) if viability_values else self._latest_metric(data, ("global_viability_score",), 0.9)
        openness = self._clamp(self._mean(openness_values)) if openness_values else self._latest_metric(data, ("future_openness_index",), 0.9)
        error_pressure = self._clamp(self._mean(error_values)) if error_values else 0.0
        risk_pressure = self._clamp(self._mean(risk_values)) if risk_values else 0.0
        expansion_pressure = self._clamp(self._mean(growth_values)) if growth_values else 0.0

        instability = self._clamp(
            0.25 * shift_signal_strength
            + 0.25 * transition_probability
            + 0.25 * break_significance
            + 0.15 * constraint_shift_index
            + 0.10 * constraint_distance
        )
        collapse_pressure = self._clamp(
            0.36 * (1.0 - viability)
            + 0.24 * (1.0 - openness)
            + 0.18 * error_pressure
            + 0.14 * risk_pressure
            + 0.08 * constraint_shift_index
        )

        scores = {
            "stability": self._clamp(1.0 - max(instability, collapse_pressure)),
            "transition": self._clamp(0.45 * transition_probability + 0.25 * shift_signal_strength + 0.20 * constraint_shift_index + 0.10 * (1.0 - break_significance)),
            "rupture": self._clamp(0.50 * break_significance + 0.25 * constraint_distance + 0.15 * shift_signal_strength + 0.10 * transition_probability),
            "expansion": self._clamp(0.40 * expansion_pressure + 0.25 * openness + 0.20 * viability + 0.15 * max(0.0, shift_signal_strength - collapse_pressure)),
            "collapse": collapse_pressure,
        }

        # Avoid over-classifying expansion when the system is merely healthy and stable.
        if instability < 0.25 and expansion_pressure < 0.35:
            scores["expansion"] *= 0.45
        if scores["collapse"] >= 0.55:
            scores["stability"] *= 0.25
        return {key: round(self._clamp(value), 6) for key, value in scores.items()}

    def _classify(self, scores: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
        if not scores:
            return "stability", 0.0, {}
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        current, top_score = ranked[0]
        second = ranked[1][1] if len(ranked) > 1 else 0.0
        confidence = self._clamp(0.55 * top_score + 0.45 * max(0.0, top_score - second))
        return current, round(confidence, 6), dict(ranked)

    def step(self, inputs: Any = None, persist: bool = True) -> Dict[str, Any]:
        data, observation_count, input_mode = self._normalize_inputs(inputs)
        scores = self._score_paradigms(data)
        current_paradigm, classification_confidence, ranked_scores = self._classify(scores)

        transition_probability = self._indicator(data, "transition_probability", ("i2", "transition_probability"))
        break_significance = self._indicator(data, "break_significance", ("i3", "break_significance"))
        constraint_shift_index = self._indicator(data, "constraint_shift_index", ("i4", "constraint_shift_index"))
        shift_signal_strength = self._indicator(data, "shift_signal_strength", ("i1", "shift_signal_strength"))

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "input_mode": input_mode,
            "observation_count": observation_count,
            "current_paradigm": current_paradigm,
            "classification_confidence": classification_confidence,
            "paradigm_scores": scores,
            "ranked_paradigm_scores": ranked_scores,
            "indicator_summary": {
                "shift_signal_strength": round(shift_signal_strength, 6),
                "transition_probability": round(transition_probability, 6),
                "break_significance": round(break_significance, 6),
                "constraint_shift_index": round(constraint_shift_index, 6),
            },
            "classification_taxonomy": list(self.allowed_paradigms),
            "paradigm_classification_ready": True,
            "epistemic_status": "functional_indicators_only",
            "governance": {
                "non_closure_preserved": True,
                "phenomenal_subjectivity_claimed": False,
                "traceable": True,
                "reversible": True,
            },
        }

        if persist:
            latest = self.output_dir / "latest_paradigm_classification.json"
            archive = self.output_dir / f"paradigm_classification_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            payload = json.dumps(result, indent=2, ensure_ascii=False)
            latest.write_text(payload, encoding="utf-8")
            archive.write_text(payload, encoding="utf-8")
            result["state_path"] = str(latest)
            result["archive_path"] = str(archive)

        return result


__all__ = ["ParadigmClassificationEngine"]
