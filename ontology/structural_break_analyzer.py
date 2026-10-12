from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Optional, Tuple


class StructuralBreakAnalyzer:
    """I3 - Structural Break Analyzer.

    Cette primitive identifie les ruptures structurelles mesurables dans une
    serie d'observations civilisationnelles : ruptures de tendance, ruptures de
    variance et ruptures comportementales. Elle intervient apres I1 et I2 sans
    affirmer de subjectivite phenomenale.
    """

    primitive = "structural_break_analyzer"

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

    def _extract_series(self, observations: Iterable[Dict[str, Any]]) -> Dict[str, List[float]]:
        series: Dict[str, List[float]] = {}
        for obs in observations:
            if not isinstance(obs, dict):
                continue
            for key, value in obs.items():
                numeric = self._to_float(value)
                if numeric is None:
                    continue
                series.setdefault(key, []).append(numeric)
        return {k: v for k, v in series.items() if len(v) >= 4}

    def _default_observations(self) -> List[Dict[str, Any]]:
        candidates = [
            self.root / "metrics_history.jsonl",
            self.root / "runtime_experiments" / "metrics_history.jsonl",
            self.root / "civilizational_metrics" / "metrics_history.jsonl",
        ]
        observations: List[Dict[str, Any]] = []
        for path in candidates:
            if not path.exists():
                continue
            try:
                for line in path.read_text(encoding="utf-8").splitlines()[-240:]:
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        observations.append(obj)
            except Exception:
                continue
        if observations:
            return observations
        return [
            {"global_viability_score": 0.91, "civilizational_autonomy_score": 0.92, "error_count": 0},
            {"global_viability_score": 0.918, "civilizational_autonomy_score": 0.928, "error_count": 0},
            {"global_viability_score": 0.931, "civilizational_autonomy_score": 0.936, "error_count": 0},
            {"global_viability_score": 0.929, "civilizational_autonomy_score": 0.934, "error_count": 0},
            {"global_viability_score": 0.930, "civilizational_autonomy_score": 0.935, "error_count": 0},
            {"global_viability_score": 0.932, "civilizational_autonomy_score": 0.937, "error_count": 0},
        ]

    def _load_latest_i2_transition(self) -> Optional[Dict[str, Any]]:
        path = self.output_dir / "latest_regime_transition_detection.json"
        if not path.exists():
            return None
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    def _compute_i2_transition(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            from ontology.regime_transition_detector import RegimeTransitionDetector
            return RegimeTransitionDetector(root=self.root).step(observations, persist=True)
        except Exception:
            return {
                "success": False,
                "transition_probability": 0.0,
                "transition_duration": 0,
                "transition_state": "unavailable",
                "regime_stability": 1.0,
            }

    @staticmethod
    def _linear_slope(values: List[float]) -> float:
        n = len(values)
        if n < 2:
            return 0.0
        xs = list(range(n))
        xbar = mean(xs)
        ybar = mean(values)
        denom = sum((x - xbar) ** 2 for x in xs)
        if denom == 0:
            return 0.0
        return sum((x - xbar) * (y - ybar) for x, y in zip(xs, values)) / denom

    def _best_split_break(self, values: List[float]) -> Dict[str, Any]:
        n = len(values)
        if n < 4:
            return {"trend_break": 0.0, "variance_break": 0.0, "behavioral_break": 0.0, "combined_strength": 0.0, "split_index": None}

        global_spread = pstdev(values) if n > 1 else 0.0
        denominator = global_spread + 1e-9
        candidates: List[Dict[str, Any]] = []
        start = max(2, n // 5)
        end = min(n - 2, (4 * n) // 5)
        for split in range(start, end + 1):
            before = values[:split]
            after = values[split:]
            if len(before) < 2 or len(after) < 2:
                continue
            slope_before = self._linear_slope(before)
            slope_after = self._linear_slope(after)
            trend_break = min(abs(slope_after - slope_before) / denominator, 1.0)

            variance_before = pstdev(before) if len(before) > 1 else 0.0
            variance_after = pstdev(after) if len(after) > 1 else 0.0
            variance_break = min(abs(variance_after - variance_before) / denominator, 1.0)

            level_break = min(abs(mean(after) - mean(before)) / denominator, 1.0)
            direction_change = 1.0 if (slope_before * slope_after) < 0 else 0.0
            behavioral_break = self._clamp(0.65 * level_break + 0.35 * direction_change)

            combined = self._clamp(0.42 * trend_break + 0.28 * variance_break + 0.30 * behavioral_break)
            candidates.append({
                "trend_break": trend_break,
                "variance_break": variance_break,
                "behavioral_break": behavioral_break,
                "combined_strength": combined,
                "split_index": split,
            })

        if not candidates:
            return {"trend_break": 0.0, "variance_break": 0.0, "behavioral_break": 0.0, "combined_strength": 0.0, "split_index": None}
        return max(candidates, key=lambda item: item["combined_strength"])

    def _analyze_series(self, series: Dict[str, List[float]], break_threshold: float) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, float]]:
        metric_breaks: Dict[str, Dict[str, Any]] = {}
        trend_values: List[float] = []
        variance_values: List[float] = []
        behavioral_values: List[float] = []
        combined_values: List[float] = []
        selected_count = 0

        for metric, values in series.items():
            b = self._best_split_break(values)
            combined = self._clamp(float(b.get("combined_strength", 0.0)))
            trend = self._clamp(float(b.get("trend_break", 0.0)))
            variance = self._clamp(float(b.get("variance_break", 0.0)))
            behavioral = self._clamp(float(b.get("behavioral_break", 0.0)))
            selected = combined >= break_threshold
            if selected:
                selected_count += 1
            metric_breaks[metric] = {
                "trend_break": round(trend, 6),
                "variance_break": round(variance, 6),
                "behavioral_break": round(behavioral, 6),
                "combined_strength": round(combined, 6),
                "split_index": b.get("split_index"),
                "selected": selected,
            }
            trend_values.append(trend)
            variance_values.append(variance)
            behavioral_values.append(behavioral)
            combined_values.append(combined)

        aggregate = {
            "trend_break_intensity": mean(trend_values) if trend_values else 0.0,
            "variance_break_intensity": mean(variance_values) if variance_values else 0.0,
            "behavioral_break_intensity": mean(behavioral_values) if behavioral_values else 0.0,
            "mean_combined_break_strength": mean(combined_values) if combined_values else 0.0,
            "max_combined_break_strength": max(combined_values) if combined_values else 0.0,
            "selected_break_count": float(selected_count),
        }
        return metric_breaks, aggregate

    def _classify_break_type(self, aggregate: Dict[str, float]) -> str:
        values = {
            "trend_break": aggregate.get("trend_break_intensity", 0.0),
            "variance_break": aggregate.get("variance_break_intensity", 0.0),
            "behavioral_break": aggregate.get("behavioral_break_intensity", 0.0),
        }
        best = max(values.items(), key=lambda item: item[1])
        if best[1] < 0.20:
            return "no_structural_break"
        return best[0]

    def step(
        self,
        observations: Optional[List[Dict[str, Any]]] = None,
        *,
        transition_result: Optional[Dict[str, Any]] = None,
        break_threshold: float = 0.35,
        persist: bool = True,
    ) -> Dict[str, Any]:
        data = observations if observations is not None else self._default_observations()
        if not isinstance(data, list):
            data = []

        threshold = self._clamp(break_threshold, 0.05, 0.95)
        transition = transition_result if isinstance(transition_result, dict) else None
        if transition is None and observations is None:
            transition = self._load_latest_i2_transition()
        if transition is None:
            transition = self._compute_i2_transition(data)

        series = self._extract_series(data)
        metric_breaks, aggregate = self._analyze_series(series, threshold)

        transition_probability = self._clamp(float(transition.get("transition_probability", 0.0) or 0.0))
        transition_duration = int(transition.get("transition_duration", 0) or 0)
        transition_state = str(transition.get("transition_state", "unknown"))
        mean_strength = self._clamp(aggregate.get("mean_combined_break_strength", 0.0))
        max_strength = self._clamp(aggregate.get("max_combined_break_strength", 0.0))
        selected_break_count = int(aggregate.get("selected_break_count", 0.0))
        structural_break_count = selected_break_count
        if structural_break_count == 0 and max_strength >= threshold:
            structural_break_count = 1

        metric_density = self._clamp(structural_break_count / max(1, len(series)))
        break_significance = self._clamp(
            0.50 * max_strength
            + 0.20 * mean_strength
            + 0.15 * metric_density
            + 0.10 * transition_probability
            + 0.05 * min(transition_duration, max(1, len(data))) / max(1, len(data))
        )
        break_confidence = self._clamp(
            0.45 * min(len(data), 40) / 40
            + 0.25 * min(len(series), 8) / 8
            + 0.20 * metric_density
            + 0.10 * transition_probability
        )
        structural_break_detected = bool(structural_break_count > 0 or break_significance >= threshold)
        break_type = self._classify_break_type(aggregate)

        timestamp = datetime.now(timezone.utc).isoformat()
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "observation_count": len(data),
            "metric_count": len(series),
            "structural_break_count": int(structural_break_count),
            "break_significance": round(break_significance, 6),
            "structural_break_detected": structural_break_detected,
            "dominant_break_type": break_type,
            "trend_break_intensity": round(self._clamp(aggregate.get("trend_break_intensity", 0.0)), 6),
            "variance_break_intensity": round(self._clamp(aggregate.get("variance_break_intensity", 0.0)), 6),
            "behavioral_break_intensity": round(self._clamp(aggregate.get("behavioral_break_intensity", 0.0)), 6),
            "break_confidence": round(break_confidence, 6),
            "break_threshold": round(threshold, 6),
            "metric_breaks": metric_breaks,
            "input_transition_summary": {
                "transition_probability": round(transition_probability, 6),
                "transition_duration": transition_duration,
                "transition_state": transition_state,
                "current_regime": transition.get("current_regime"),
            },
            "structural_break_analysis_ready": True,
            "epistemic_status": "functional_indicators_only",
            "governance": {
                "non_closure_preserved": True,
                "phenomenal_subjectivity_claimed": False,
                "traceable": True,
                "reversible": True,
            },
        }

        if persist:
            latest = self.output_dir / "latest_structural_break_analysis.json"
            archive = self.output_dir / f"structural_break_analysis_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            payload = json.dumps(result, indent=2, ensure_ascii=False)
            latest.write_text(payload, encoding="utf-8")
            archive.write_text(payload, encoding="utf-8")
            result["state_path"] = str(latest)
            result["archive_path"] = str(archive)

        return result


__all__ = ["StructuralBreakAnalyzer"]
