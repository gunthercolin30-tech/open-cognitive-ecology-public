
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
DRIFT_DIR = ROOT / "civilizational_drift"
LATEST_PATH = DRIFT_DIR / "latest_drift_correlation_analyzer.json"
HISTORY_PATH = DRIFT_DIR / "drift_correlation_analyzer_history.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: Any, default: float = 0.0, low: float = 0.0, high: float = 1.0) -> float:
    try:
        numeric = float(value)
    except Exception:
        numeric = default
    if not math.isfinite(numeric):
        numeric = default
    return max(low, min(high, numeric))


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def _load_jsonl(path: Path, limit: int = 128) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        if not path.exists():
            return records
        lines = path.read_text(encoding="utf-8").splitlines()
        for line in lines[-max(1, limit):]:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if isinstance(data, dict):
                records.append(data)
    except Exception:
        return records
    return records


def _mean(values: Iterable[float]) -> float:
    vals = [float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
    return sum(vals) / len(vals) if vals else 0.0


def _variance(values: list[float]) -> float:
    vals = [float(v) for v in values if math.isfinite(float(v))]
    if len(vals) < 2:
        return 0.0
    m = sum(vals) / len(vals)
    return sum((v - m) ** 2 for v in vals) / len(vals)


def _pearson(left: list[float], right: list[float]) -> float:
    n = min(len(left), len(right))
    if n < 2:
        return 0.0
    x = [float(v) for v in left[-n:]]
    y = [float(v) for v in right[-n:]]
    mx = sum(x) / n
    my = sum(y) / n
    vx = sum((v - mx) ** 2 for v in x)
    vy = sum((v - my) ** 2 for v in y)
    if vx <= 0.0 or vy <= 0.0:
        return 0.0
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    return max(-1.0, min(1.0, cov / math.sqrt(vx * vy)))


def _directional_lag_correlation(cause: list[float], effect: list[float], lag: int = 1) -> float:
    n = min(len(cause), len(effect))
    if n <= lag + 1:
        return 0.0
    x = cause[-n:-lag]
    y = effect[-n + lag:]
    return _pearson(x, y)


def _score_from_record(record: Mapping[str, Any], score_key: str, alternatives: tuple[str, ...]) -> float:
    if score_key in record:
        return _clamp(record.get(score_key))
    diagnostics = _as_mapping(record.get("diagnostics"))
    for key in alternatives:
        if key in record:
            return _clamp(record.get(key))
        if key in diagnostics:
            return _clamp(diagnostics.get(key))
    return 0.0


class DriftCorrelationAnalyzer:
    # J5 - Drift Correlation Analyzer.
    # Measurement-only primitive correlating identity, strategy and memory drift.
    # It never modifies identity, strategy or memory; it only reads drift monitors
    # and emits functional indicators.

    primitive = "drift_correlation_analyzer"
    epistemic_status = "functional_indicators_only"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.drift_dir = self.root / "civilizational_drift"
        self.latest_path = self.drift_dir / "latest_drift_correlation_analyzer.json"
        self.history_path = self.drift_dir / "drift_correlation_analyzer_history.jsonl"
        self.paths = {
            "identity": {
                "latest": self.drift_dir / "latest_identity_drift_monitor.json",
                "history": self.drift_dir / "identity_drift_monitor_history.jsonl",
            },
            "strategy": {
                "latest": self.drift_dir / "latest_strategic_drift_monitor.json",
                "history": self.drift_dir / "strategic_drift_history.jsonl",
            },
            "memory": {
                "latest": self.drift_dir / "latest_memory_drift_monitor.json",
                "history": self.drift_dir / "memory_drift_history.jsonl",
            },
        }

    def _collect_latest(self, provided: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        latest: dict[str, dict[str, Any]] = {}
        for axis in ("identity", "strategy", "memory"):
            supplied = _as_mapping(provided.get(axis))
            latest[axis] = supplied or _load_json(self.paths[axis]["latest"])
        if not latest["identity"]:
            latest["identity"] = self._run_identity_monitor()
        if not latest["strategy"]:
            latest["strategy"] = self._run_strategy_monitor()
        if not latest["memory"]:
            latest["memory"] = self._run_memory_monitor()
        return latest

    def _collect_history(self, provided: Mapping[str, Any], limit: int) -> dict[str, list[dict[str, Any]]]:
        history: dict[str, list[dict[str, Any]]] = {}
        supplied_history = _as_mapping(provided.get("history"))
        for axis in ("identity", "strategy", "memory"):
            raw = supplied_history.get(axis)
            if isinstance(raw, list):
                history[axis] = [r for r in raw if isinstance(r, dict)][-limit:]
            else:
                history[axis] = _load_jsonl(self.paths[axis]["history"], limit=limit)
        return history

    def _run_identity_monitor(self) -> dict[str, Any]:
        try:
            from ontology.identity_drift_monitor import IdentityDriftMonitor
            result = IdentityDriftMonitor(root=self.root).step(persist=False)
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"success": False, "collection_error": repr(exc), "identity_drift_score": 0.0}

    def _run_strategy_monitor(self) -> dict[str, Any]:
        try:
            from ontology.strategic_drift_monitor import StrategicDriftMonitor
            result = StrategicDriftMonitor().step(persist=False)
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"success": False, "collection_error": repr(exc), "strategic_drift_score": 0.0}

    def _run_memory_monitor(self) -> dict[str, Any]:
        try:
            from ontology.memory_drift_monitor import MemoryDriftMonitor
            result = MemoryDriftMonitor().step(persist=False)
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"success": False, "collection_error": repr(exc), "memory_drift_score": 0.0}

    @staticmethod
    def _axis_score(axis: str, record: Mapping[str, Any]) -> float:
        if axis == "identity":
            return _score_from_record(record, "identity_drift_score", ("drift_score", "identity_drift", "semantic_drift_score"))
        if axis == "strategy":
            return _score_from_record(record, "strategic_drift_score", ("strategy_drift_score", "strategic_drift", "goal_drift_score"))
        if axis == "memory":
            return _score_from_record(record, "memory_drift_score", ("memory_drift", "memory_loss_rate", "archive_drift_score"))
        return 0.0

    def _series(self, axis: str, history: list[dict[str, Any]], latest: dict[str, Any]) -> list[float]:
        values = [self._axis_score(axis, r) for r in history]
        latest_score = self._axis_score(axis, latest)
        if not values or abs(values[-1] - latest_score) > 1e-12:
            values.append(latest_score)
        return [_clamp(v) for v in values[-128:]]

    def _pairwise_correlations(self, series: dict[str, list[float]]) -> dict[str, float]:
        pairs = {
            "identity_strategy": _pearson(series["identity"], series["strategy"]),
            "identity_memory": _pearson(series["identity"], series["memory"]),
            "strategy_memory": _pearson(series["strategy"], series["memory"]),
        }
        return pairs

    def _lag_correlations(self, series: dict[str, list[float]]) -> dict[str, float]:
        return {
            "identity_to_strategy_lag1": _directional_lag_correlation(series["identity"], series["strategy"], lag=1),
            "identity_to_memory_lag1": _directional_lag_correlation(series["identity"], series["memory"], lag=1),
            "strategy_to_identity_lag1": _directional_lag_correlation(series["strategy"], series["identity"], lag=1),
            "strategy_to_memory_lag1": _directional_lag_correlation(series["strategy"], series["memory"], lag=1),
            "memory_to_identity_lag1": _directional_lag_correlation(series["memory"], series["identity"], lag=1),
            "memory_to_strategy_lag1": _directional_lag_correlation(series["memory"], series["strategy"], lag=1),
        }

    @staticmethod
    def _systemic_coupling(pairwise: Mapping[str, float], lagged: Mapping[str, float]) -> float:
        positive_pairwise = [max(0.0, float(v)) for v in pairwise.values()]
        positive_lagged = [max(0.0, float(v)) for v in lagged.values()]
        return _clamp((0.75 * _mean(positive_pairwise)) + (0.25 * _mean(positive_lagged)))

    @staticmethod
    def _coordinated_risk(current_scores: Mapping[str, float], coupling: float, variance_score: float) -> float:
        mean_drift = _mean([float(v) for v in current_scores.values()])
        max_drift = max([float(v) for v in current_scores.values()] or [0.0])
        return _clamp((0.45 * mean_drift) + (0.25 * max_drift) + (0.20 * coupling) + (0.10 * variance_score))

    @staticmethod
    def _classify(coupling: float, risk: float) -> str:
        if risk >= 0.75 or coupling >= 0.75:
            return "high_correlated_drift_risk"
        if risk >= 0.45 or coupling >= 0.45:
            return "moderate_correlated_drift_risk"
        return "low_correlated_drift_risk"

    def evaluate(self, inputs: Mapping[str, Any] | None = None, history_limit: int = 128) -> dict[str, Any]:
        data = _as_mapping(inputs)
        latest = self._collect_latest(data)
        history = self._collect_history(data, limit=history_limit)

        series = {
            axis: self._series(axis, history[axis], latest[axis])
            for axis in ("identity", "strategy", "memory")
        }
        current_scores = {axis: _clamp(values[-1] if values else 0.0) for axis, values in series.items()}
        pairwise = self._pairwise_correlations(series)
        lagged = self._lag_correlations(series)
        coupling = self._systemic_coupling(pairwise, lagged)
        drift_variance = _clamp(_variance(list(current_scores.values())), high=1.0)
        coordinated_risk = self._coordinated_risk(current_scores, coupling, drift_variance)

        strongest_pair = max(pairwise.items(), key=lambda item: abs(item[1])) if pairwise else (None, 0.0)
        strongest_lag = max(lagged.items(), key=lambda item: abs(item[1])) if lagged else (None, 0.0)

        sample_lengths = {axis: len(values) for axis, values in series.items()}
        minimum_sample_length = min(sample_lengths.values()) if sample_lengths else 0
        correlation_reliability = _clamp((minimum_sample_length - 1) / 9.0) if minimum_sample_length > 1 else 0.0

        return {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": _utc_now(),
            "current_drift_scores": current_scores,
            "pairwise_correlations": {k: round(float(v), 6) for k, v in pairwise.items()},
            "lagged_correlations": {k: round(float(v), 6) for k, v in lagged.items()},
            "systemic_drift_coupling_index": round(coupling, 6),
            "coordinated_drift_risk_index": round(coordinated_risk, 6),
            "drift_axis_variance": round(drift_variance, 6),
            "strongest_pairwise_relation": {"relation": strongest_pair[0], "correlation": round(float(strongest_pair[1]), 6)},
            "strongest_lagged_relation": {"relation": strongest_lag[0], "correlation": round(float(strongest_lag[1]), 6)},
            "correlation_reliability": round(correlation_reliability, 6),
            "sample_lengths": sample_lengths,
            "classification": self._classify(coupling, coordinated_risk),
            "monitor_ready": True,
            "epistemic_status": self.epistemic_status,
            "diagnostics": {
                "measurement_only": True,
                "history_limit": history_limit,
                "uses_identity_drift_monitor": True,
                "uses_strategic_drift_monitor": True,
                "uses_memory_drift_monitor": True,
                "minimum_sample_length": minimum_sample_length,
            },
            "governance": {
                "phenomenal_subjectivity_claimed": False,
                "does_not_modify_identity": True,
                "does_not_modify_strategy": True,
                "does_not_modify_memory": True,
                "recommendations_only": False,
                "non_closure_compliant": True,
                "functional_indicators_only": True,
            },
        }

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = True, history_limit: int = 128) -> dict[str, Any]:
        result = self.evaluate(inputs=inputs, history_limit=history_limit)
        if persist:
            self._persist(result)
        return result

    def _persist(self, result: Mapping[str, Any]) -> None:
        self.drift_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive_path = self.drift_dir / f"drift_correlation_analyzer_{stamp}.json"
        payload = json.dumps(dict(result), ensure_ascii=False, indent=2, sort_keys=True, default=str)
        archive_path.write_text(payload, encoding="utf-8")
        self.latest_path.write_text(payload, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(result), ensure_ascii=False, sort_keys=True, default=str))
            handle.write("\n")
