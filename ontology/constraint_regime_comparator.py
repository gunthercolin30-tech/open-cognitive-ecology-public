from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple


class ConstraintRegimeComparator:
    """I4 - Constraint Regime Comparator.

    Cette primitive compare deux regimes successifs de contraintes et produit
    des indicateurs fonctionnels mesurables : distance entre regimes,
    indice de deplacement de contraintes, dimensions dominantes et statut de
    comparaison. Elle ne formule aucune affirmation de subjectivite
    phenomenale.
    """

    primitive = "constraint_regime_comparator"

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
    def _is_constraint_like(key: str) -> bool:
        lowered = key.lower()
        markers = (
            "constraint", "closure", "viability", "openness", "constitutional",
            "pressure", "stability", "resource", "error", "risk", "alignment",
            "governance", "regime", "transition", "break", "anomaly",
        )
        return any(marker in lowered for marker in markers)

    def _numeric_projection(self, regime: Dict[str, Any]) -> Dict[str, float]:
        projection: Dict[str, float] = {}
        for key, value in regime.items():
            numeric = self._to_float(value)
            if numeric is not None:
                projection[key] = numeric
                continue
            if isinstance(value, dict):
                nested = self._numeric_projection(value)
                for sub_key, sub_value in nested.items():
                    projection[f"{key}.{sub_key}"] = sub_value
        return projection

    def _extract_series(self, observations: Iterable[Dict[str, Any]]) -> Dict[str, List[float]]:
        series: Dict[str, List[float]] = {}
        for obs in observations:
            if not isinstance(obs, dict):
                continue
            projected = self._numeric_projection(obs)
            for key, value in projected.items():
                if self._is_constraint_like(key):
                    series.setdefault(key, []).append(value)
        return {k: v for k, v in series.items() if len(v) >= 2}

    def _summarize_half(self, series: Dict[str, List[float]], first: bool) -> Dict[str, float]:
        summary: Dict[str, float] = {}
        for key, values in series.items():
            if len(values) < 2:
                continue
            mid = max(1, len(values) // 2)
            segment = values[:mid] if first else values[mid:]
            if not segment:
                segment = values
            summary[key] = mean(segment)
        return summary

    def _default_observations(self) -> List[Dict[str, Any]]:
        candidates = [
            self.root / "metrics_history.jsonl",
            self.root / "runtime_experiments" / "metrics_history.jsonl",
            self.root / "civilizational_metrics" / "metrics_history.jsonl",
            self.root / "paradigm_surveillance" / "latest_regime_transition_detection.json",
            self.root / "paradigm_surveillance" / "latest_structural_break_analysis.json",
        ]
        observations: List[Dict[str, Any]] = []
        for path in candidates:
            if not path.exists():
                continue
            try:
                if path.suffix == ".jsonl":
                    for line in path.read_text(encoding="utf-8").splitlines()[-250:]:
                        if not line.strip():
                            continue
                        item = json.loads(line)
                        if isinstance(item, dict):
                            observations.append(item)
                elif path.suffix == ".json":
                    item = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(item, dict):
                        observations.append(item)
            except Exception:
                continue
        return observations

    def _coerce_inputs(
        self,
        previous_regime: Optional[Any],
        current_regime: Optional[Any],
        observations: Optional[Iterable[Dict[str, Any]]],
    ) -> Tuple[Dict[str, float], Dict[str, float], int, str]:
        if isinstance(previous_regime, dict) and isinstance(current_regime, dict):
            return (
                self._numeric_projection(previous_regime),
                self._numeric_projection(current_regime),
                2,
                "explicit_regimes",
            )

        if isinstance(previous_regime, dict) and "previous_regime" in previous_regime and "current_regime" in previous_regime:
            prev = previous_regime.get("previous_regime")
            curr = previous_regime.get("current_regime")
            if isinstance(prev, dict) and isinstance(curr, dict):
                return self._numeric_projection(prev), self._numeric_projection(curr), 2, "enveloped_regimes"

        source = observations
        if source is None and isinstance(previous_regime, list):
            source = previous_regime
        if source is None:
            source = self._default_observations()
        obs_list = list(source or [])
        series = self._extract_series(obs_list)
        return self._summarize_half(series, True), self._summarize_half(series, False), len(obs_list), "observation_series"

    def _compare_vectors(self, previous: Dict[str, float], current: Dict[str, float]) -> Dict[str, Any]:
        keys = sorted(set(previous) | set(current))
        if not keys:
            return {
                "constraint_regime_distance": 0.0,
                "constraint_shift_index": 0.0,
                "dimension_distances": {},
                "dominant_constraint_dimensions": [],
            }

        distances: Dict[str, float] = {}
        weighted: List[float] = []
        for key in keys:
            prev = previous.get(key, 0.0)
            curr = current.get(key, 0.0)
            raw = abs(curr - prev)
            scale = max(abs(prev), abs(curr), 1.0)
            normalized = self._clamp(raw / scale)
            weight = 1.25 if self._is_constraint_like(key) else 1.0
            distances[key] = round(normalized, 6)
            weighted.append(self._clamp(normalized * weight))

        euclidean = math.sqrt(sum(v * v for v in distances.values()) / len(distances))
        mean_shift = mean(weighted) if weighted else 0.0
        max_shift = max(weighted) if weighted else 0.0
        constraint_regime_distance = self._clamp((0.55 * euclidean) + (0.45 * mean_shift))
        constraint_shift_index = self._clamp((0.60 * constraint_regime_distance) + (0.40 * max_shift))
        dominant = [key for key, value in sorted(distances.items(), key=lambda item: item[1], reverse=True)[:5] if value > 0.0]

        return {
            "constraint_regime_distance": round(constraint_regime_distance, 6),
            "constraint_shift_index": round(constraint_shift_index, 6),
            "dimension_distances": distances,
            "dominant_constraint_dimensions": dominant,
        }

    @staticmethod
    def _classify(distance: float, shift: float) -> str:
        score = max(distance, shift)
        if score >= 0.65:
            return "divergent_constraint_regime"
        if score >= 0.35:
            return "shifted_constraint_regime"
        if score >= 0.15:
            return "weak_constraint_regime_shift"
        return "stable_constraint_regime"

    def step(
        self,
        previous_regime: Optional[Any] = None,
        current_regime: Optional[Any] = None,
        observations: Optional[Iterable[Dict[str, Any]]] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        previous, current, observation_count, input_mode = self._coerce_inputs(previous_regime, current_regime, observations)
        comparison = self._compare_vectors(previous, current)
        distance = comparison["constraint_regime_distance"]
        shift_index = comparison["constraint_shift_index"]
        comparison_status = self._classify(distance, shift_index)
        compared_dimension_count = len(comparison["dimension_distances"])
        comparison_confidence = self._clamp(0.20 + min(compared_dimension_count, 12) / 20.0 + shift_index * 0.30)

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "input_mode": input_mode,
            "observation_count": observation_count,
            "compared_dimension_count": compared_dimension_count,
            "constraint_regime_distance": distance,
            "constraint_shift_index": shift_index,
            "comparison_status": comparison_status,
            "dominant_constraint_dimensions": comparison["dominant_constraint_dimensions"],
            "dimension_distances": comparison["dimension_distances"],
            "previous_regime_signature": previous,
            "current_regime_signature": current,
            "constraint_regime_comparison_ready": True,
            "comparison_confidence": round(comparison_confidence, 6),
            "epistemic_status": "functional_indicators_only",
            "governance": {
                "non_closure_preserved": True,
                "phenomenal_subjectivity_claimed": False,
                "traceable": True,
                "reversible": True,
            },
        }

        if persist:
            latest = self.output_dir / "latest_constraint_regime_comparison.json"
            archive = self.output_dir / f"constraint_regime_comparison_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            payload = json.dumps(result, indent=2, ensure_ascii=False)
            latest.write_text(payload, encoding="utf-8")
            archive.write_text(payload, encoding="utf-8")
            result["state_path"] = str(latest)
            result["archive_path"] = str(archive)

        return result


__all__ = ["ConstraintRegimeComparator"]
