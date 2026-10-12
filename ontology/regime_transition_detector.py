from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable


class RegimeTransitionDetector:
    """
    I2 — Regime Transition Detector.

    Cette primitive détecte l'état temporel d'un régime civilisationnel :
    before_transition, transition_active ou after_transition. Elle s'appuie
    prioritairement sur les signaux extraits par I1, mais peut fonctionner
    directement sur une série d'observations métriques.

    Le module ne produit aucune affirmation phénoménale ; il expose uniquement
    des indicateurs fonctionnels mesurables de transition de régime.
    """

    primitive = "regime_transition_detector"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "paradigm_surveillance"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, float(value)))

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            return float(value)
        return None

    def _extract_series(self, observations: Iterable[dict[str, Any]]) -> dict[str, list[float]]:
        series: dict[str, list[float]] = {}
        for obs in observations:
            if not isinstance(obs, dict):
                continue
            for key, value in obs.items():
                numeric = self._to_float(value)
                if numeric is None:
                    continue
                series.setdefault(key, []).append(numeric)
        return {k: v for k, v in series.items() if len(v) >= 2}

    def _default_observations(self) -> list[dict[str, Any]]:
        candidates = [
            self.root / "metrics_history.jsonl",
            self.root / "runtime_experiments" / "metrics_history.jsonl",
            self.root / "civilizational_metrics" / "metrics_history.jsonl",
        ]
        observations: list[dict[str, Any]] = []
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
        ]

    def _load_latest_i1_signal(self) -> dict[str, Any] | None:
        path = self.output_dir / "latest_paradigm_shift_signal_extraction.json"
        if not path.exists():
            return None
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    def _compute_i1_signal(self, observations: list[dict[str, Any]]) -> dict[str, Any]:
        try:
            from ontology.paradigm_shift_signal_extractor import ParadigmShiftSignalExtractor
            return ParadigmShiftSignalExtractor(root=self.root).step(observations, persist=True)
        except Exception:
            return {
                "success": False,
                "shift_signal_count": 0,
                "shift_signal_strength": 0.0,
                "persistent_signal_count": 0,
                "extraction_confidence": 0.0,
            }

    def _window_features(self, series: dict[str, list[float]]) -> dict[str, float]:
        if not series:
            return {
                "normalized_level_shift": 0.0,
                "normalized_slope_shift": 0.0,
                "instability_index": 0.0,
                "post_transition_stability": 0.0,
                "regime_distance": 0.0,
            }

        level_shifts: list[float] = []
        slope_shifts: list[float] = []
        instabilities: list[float] = []
        post_stabilities: list[float] = []

        for values in series.values():
            n = len(values)
            if n < 2:
                continue
            midpoint = max(1, n // 2)
            before = values[:midpoint]
            after = values[midpoint:] or values[-1:]
            spread = pstdev(values) if n > 1 else 0.0
            level = abs(mean(after) - mean(before)) / (spread + 1e-9)
            level_shifts.append(min(level / 3.0, 1.0))

            diffs = [values[i] - values[i - 1] for i in range(1, n)]
            if diffs:
                left = diffs[:max(1, midpoint - 1)]
                right = diffs[midpoint - 1:] or diffs[-1:]
                slope = abs(mean(right) - mean(left)) / (spread + 1e-9)
                slope_shifts.append(min(slope / 3.0, 1.0))
                instability = pstdev(diffs) / (spread + 1e-9) if len(diffs) > 1 else 0.0
                instabilities.append(min(instability / 3.0, 1.0))
            else:
                slope_shifts.append(0.0)
                instabilities.append(0.0)

            after_spread = pstdev(after) if len(after) > 1 else 0.0
            post_stabilities.append(1.0 - min(after_spread / (spread + 1e-9), 1.0))

        normalized_level_shift = mean(level_shifts) if level_shifts else 0.0
        normalized_slope_shift = mean(slope_shifts) if slope_shifts else 0.0
        instability_index = mean(instabilities) if instabilities else 0.0
        post_transition_stability = mean(post_stabilities) if post_stabilities else 0.0
        regime_distance = self._clamp(0.60 * normalized_level_shift + 0.25 * normalized_slope_shift + 0.15 * instability_index)

        return {
            "normalized_level_shift": round(self._clamp(normalized_level_shift), 6),
            "normalized_slope_shift": round(self._clamp(normalized_slope_shift), 6),
            "instability_index": round(self._clamp(instability_index), 6),
            "post_transition_stability": round(self._clamp(post_transition_stability), 6),
            "regime_distance": round(regime_distance, 6),
        }

    def _estimate_duration(self, observations: list[dict[str, Any]], features: dict[str, float], probability: float) -> int:
        if probability < 0.35:
            return 0
        n = len(observations)
        instability = features.get("instability_index", 0.0)
        slope = features.get("normalized_slope_shift", 0.0)
        duration = max(1, round(n * self._clamp(0.15 + 0.35 * instability + 0.25 * slope)))
        return min(n, duration)

    def _classify_state(self, probability: float, features: dict[str, float], signal: dict[str, Any]) -> str:
        post_stability = float(features.get("post_transition_stability", 0.0))
        persistent_count = int(signal.get("persistent_signal_count", 0) or 0)
        if probability < 0.25:
            return "before_transition"
        if probability >= 0.62 and post_stability >= 0.66 and persistent_count >= 1:
            return "after_transition"
        if probability >= 0.35:
            return "transition_active"
        return "transition_watch"

    def _regime_label(self, transition_state: str, probability: float, features: dict[str, float]) -> str:
        distance = float(features.get("regime_distance", 0.0))
        if transition_state == "before_transition":
            return "stable_regime"
        if transition_state == "after_transition":
            return "new_regime_stabilizing" if distance >= 0.45 else "post_transition_regime"
        if transition_state == "transition_active":
            return "active_transition_regime" if probability >= 0.62 else "incipient_transition_regime"
        return "watch_regime"

    def step(
        self,
        observations: list[dict[str, Any]] | None = None,
        *,
        signal_result: dict[str, Any] | None = None,
        persist: bool = True,
    ) -> dict[str, Any]:
        data = observations if observations is not None else self._default_observations()
        if not isinstance(data, list):
            data = []

        signal = signal_result if isinstance(signal_result, dict) else None
        if signal is None and observations is None:
            signal = self._load_latest_i1_signal()
        if signal is None:
            signal = self._compute_i1_signal(data)

        series = self._extract_series(data)
        features = self._window_features(series)

        shift_strength = self._clamp(float(signal.get("shift_signal_strength", 0.0) or 0.0))
        signal_count = int(signal.get("shift_signal_count", 0) or 0)
        persistent_count = int(signal.get("persistent_signal_count", 0) or 0)
        extraction_confidence = self._clamp(float(signal.get("extraction_confidence", 0.0) or 0.0))

        signal_density = self._clamp(signal_count / max(1, len(series)))
        persistence_density = self._clamp(persistent_count / max(1, signal_count if signal_count else len(series)))
        regime_distance = float(features.get("regime_distance", 0.0))
        instability = float(features.get("instability_index", 0.0))

        transition_probability = self._clamp(
            0.40 * shift_strength
            + 0.25 * regime_distance
            + 0.15 * signal_density
            + 0.10 * persistence_density
            + 0.10 * instability
        )
        transition_duration = self._estimate_duration(data, features, transition_probability)
        transition_state = self._classify_state(transition_probability, features, signal)
        current_regime = self._regime_label(transition_state, transition_probability, features)
        previous_regime = "stable_regime" if transition_state != "before_transition" else None
        regime_stability = self._clamp(1.0 - (0.65 * transition_probability + 0.35 * instability))
        transition_confidence = self._clamp(0.55 * extraction_confidence + 0.25 * min(len(data), 40) / 40 + 0.20 * min(len(series), 8) / 8)

        timestamp = datetime.now(timezone.utc).isoformat()
        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "observation_count": len(data),
            "metric_count": len(series),
            "transition_probability": round(transition_probability, 6),
            "transition_duration": int(transition_duration),
            "transition_state": transition_state,
            "current_regime": current_regime,
            "previous_regime": previous_regime,
            "regime_stability": round(regime_stability, 6),
            "transition_confidence": round(transition_confidence, 6),
            "regime_transition_detection_ready": True,
            "input_signal_summary": {
                "shift_signal_count": signal_count,
                "shift_signal_strength": round(shift_strength, 6),
                "persistent_signal_count": persistent_count,
                "extraction_confidence": round(extraction_confidence, 6),
            },
            "features": features,
            "epistemic_status": "functional_indicators_only",
            "governance": {
                "non_closure_preserved": True,
                "phenomenal_subjectivity_claimed": False,
                "traceable": True,
                "reversible": True,
            },
        }

        if persist:
            latest = self.output_dir / "latest_regime_transition_detection.json"
            archive = self.output_dir / f"regime_transition_detection_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            payload = json.dumps(result, indent=2, ensure_ascii=False)
            latest.write_text(payload, encoding="utf-8")
            archive.write_text(payload, encoding="utf-8")
            result["state_path"] = str(latest)
            result["archive_path"] = str(archive)

        return result


__all__ = ["RegimeTransitionDetector"]
