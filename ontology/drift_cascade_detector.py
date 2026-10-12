from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
DRIFT_DIR = ROOT / "civilizational_drift"
LATEST_PATH = DRIFT_DIR / "latest_drift_cascade_detector.json"
HISTORY_PATH = DRIFT_DIR / "drift_cascade_detector_history.jsonl"


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


def _axis_score(axis: str, record: Mapping[str, Any]) -> float:
    diagnostics = _as_mapping(record.get("diagnostics"))
    candidates = {
        "identity": ("identity_drift_score", "drift_score", "identity_drift", "semantic_drift_score"),
        "strategy": ("strategic_drift_score", "strategy_drift_score", "strategic_drift", "goal_drift_score"),
        "memory": ("memory_drift_score", "memory_drift", "memory_loss_rate", "archive_drift_score"),
    }.get(axis, ())
    for key in candidates:
        if key in record:
            return _clamp(record.get(key))
        if key in diagnostics:
            return _clamp(diagnostics.get(key))
    current = _as_mapping(record.get("current_drift_scores"))
    if axis in current:
        return _clamp(current.get(axis))
    return 0.0


def _delta(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return _clamp(values[-1] - values[-2], low=-1.0, high=1.0)


def _positive_delta(values: list[float]) -> float:
    return max(0.0, _delta(values))


class DriftCascadeDetector:
    # J6 - Drift Cascade Detector.
    # Measurement-only primitive detecting sequential drift propagation among
    # identity, strategy and memory. It does not alter identity, strategy or
    # memory; it emits functional indicators only.

    primitive = "drift_cascade_detector"
    epistemic_status = "functional_indicators_only"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.drift_dir = self.root / "civilizational_drift"
        self.latest_path = self.drift_dir / "latest_drift_cascade_detector.json"
        self.history_path = self.drift_dir / "drift_cascade_detector_history.jsonl"
        self.monitor_paths = {
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
        self.correlation_latest_path = self.drift_dir / "latest_drift_correlation_analyzer.json"
        self.correlation_history_path = self.drift_dir / "drift_correlation_analyzer_history.jsonl"

    def _run_correlation_analyzer(self, provided: Mapping[str, Any] | None = None) -> dict[str, Any]:
        try:
            from ontology.drift_correlation_analyzer import DriftCorrelationAnalyzer
            result = DriftCorrelationAnalyzer(root=self.root).step(inputs=provided or {}, persist=False)
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"success": False, "collection_error": repr(exc)}

    def _collect_correlation(self, data: Mapping[str, Any]) -> dict[str, Any]:
        supplied = _as_mapping(data.get("correlation"))
        if supplied:
            return supplied
        loaded = _load_json(self.correlation_latest_path)
        if loaded:
            return loaded
        return self._run_correlation_analyzer(data)

    def _collect_latest(self, data: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        latest: dict[str, dict[str, Any]] = {}
        for axis in ("identity", "strategy", "memory"):
            supplied = _as_mapping(data.get(axis))
            loaded = supplied or _load_json(self.monitor_paths[axis]["latest"])
            latest[axis] = loaded
        return latest

    def _collect_history(self, data: Mapping[str, Any], limit: int) -> dict[str, list[dict[str, Any]]]:
        supplied_history = _as_mapping(data.get("history"))
        history: dict[str, list[dict[str, Any]]] = {}
        for axis in ("identity", "strategy", "memory"):
            raw = supplied_history.get(axis)
            if isinstance(raw, list):
                history[axis] = [r for r in raw if isinstance(r, dict)][-limit:]
            else:
                history[axis] = _load_jsonl(self.monitor_paths[axis]["history"], limit=limit)
        return history

    def _series(self, axis: str, history: list[dict[str, Any]], latest: Mapping[str, Any]) -> list[float]:
        values = [_axis_score(axis, r) for r in history]
        latest_score = _axis_score(axis, latest)
        if not values or abs(values[-1] - latest_score) > 1e-12:
            values.append(latest_score)
        return [_clamp(v) for v in values[-128:]]

    @staticmethod
    def _relation_correlation(correlation: Mapping[str, Any], cause: str, effect: str) -> float:
        lagged = _as_mapping(correlation.get("lagged_correlations"))
        pairwise = _as_mapping(correlation.get("pairwise_correlations"))
        directional_key = f"{cause}_to_{effect}_lag1"
        if directional_key in lagged:
            return _clamp(lagged.get(directional_key), low=-1.0, high=1.0)
        pair_key = "_".join(sorted([cause, effect]))
        aliases = {
            "identity_strategy": "identity_strategy",
            "identity_memory": "identity_memory",
            "memory_strategy": "strategy_memory",
        }
        key = aliases.get(pair_key, pair_key)
        return _clamp(pairwise.get(key, 0.0), low=-1.0, high=1.0)

    def _detect_edges(self, series: Mapping[str, list[float]], correlation: Mapping[str, Any]) -> list[dict[str, Any]]:
        edges: list[dict[str, Any]] = []
        for cause in ("identity", "strategy", "memory"):
            for effect in ("identity", "strategy", "memory"):
                if cause == effect:
                    continue
                cause_delta = _positive_delta(list(series.get(cause, [])))
                effect_delta = _positive_delta(list(series.get(effect, [])))
                corr = self._relation_correlation(correlation, cause, effect)
                positive_corr = max(0.0, corr)
                temporal_alignment = _clamp((0.55 * cause_delta) + (0.45 * effect_delta))
                edge_strength = _clamp((0.50 * temporal_alignment) + (0.35 * positive_corr) + (0.15 * effect_delta))
                if edge_strength > 0.0:
                    edges.append({
                        "cause": cause,
                        "effect": effect,
                        "cause_delta": round(cause_delta, 6),
                        "effect_delta": round(effect_delta, 6),
                        "directional_or_pairwise_correlation": round(corr, 6),
                        "edge_strength": round(edge_strength, 6),
                    })
        edges.sort(key=lambda item: item["edge_strength"], reverse=True)
        return edges

    @staticmethod
    def _chains_from_edges(edges: list[dict[str, Any]], threshold: float = 0.18) -> list[dict[str, Any]]:
        selected = [e for e in edges if _clamp(e.get("edge_strength")) >= threshold]
        chains: list[dict[str, Any]] = []
        for first in selected:
            for second in selected:
                if first["effect"] != second["cause"]:
                    continue
                if first["cause"] == second["effect"]:
                    continue
                nodes = [first["cause"], first["effect"], second["effect"]]
                if len(set(nodes)) < 3:
                    continue
                strength = _clamp(_mean([first["edge_strength"], second["edge_strength"]]))
                chains.append({
                    "chain": nodes,
                    "length": 3,
                    "strength": round(strength, 6),
                    "edges": [
                        {"cause": first["cause"], "effect": first["effect"]},
                        {"cause": second["cause"], "effect": second["effect"]},
                    ],
                })
        chains.sort(key=lambda item: item["strength"], reverse=True)
        unique: list[dict[str, Any]] = []
        seen: set[tuple[str, ...]] = set()
        for chain in chains:
            key = tuple(chain["chain"])
            if key in seen:
                continue
            seen.add(key)
            unique.append(chain)
        return unique

    @staticmethod
    def _classify(cascade_risk: float, early_warning: float) -> str:
        if cascade_risk >= 0.75 or early_warning >= 0.75:
            return "high_cascade_risk"
        if cascade_risk >= 0.45 or early_warning >= 0.45:
            return "moderate_cascade_risk"
        return "low_cascade_risk"

    def _causal_support(self, strongest_edge: Mapping[str, Any] | None) -> dict[str, Any]:
        if not strongest_edge:
            return {"available": False, "causal_inference_index": 0.0, "confidence_score": 0.0}
        cause = str(strongest_edge.get("cause", "drift_source"))
        effect = str(strongest_edge.get("effect", "drift_effect"))
        strength = _clamp(strongest_edge.get("edge_strength"))
        support: dict[str, Any] = {"available": False, "causal_inference_index": 0.0, "confidence_score": 0.0}
        try:
            from ontology.causal_inference import CausalInference
            ci = CausalInference().step(
                causal_discrimination=strength,
                intervention_predictability=strength,
                structural_consistency=max(0.5, strength),
            )
            support["causal_inference_index"] = _clamp(ci.get("causal_inference_index"))
            support["causal_inference"] = ci
            support["available"] = True
        except Exception as exc:
            support["causal_inference_error"] = repr(exc)
        try:
            from ontology.advanced_causal_reasoning_engine import AdvancedCausalReasoningEngine
            acr = AdvancedCausalReasoningEngine(root=self.root).step({
                "cause": cause,
                "effect": effect,
                "weight": max(0.01, strength),
            })
            support["confidence_score"] = _clamp(acr.get("confidence_score"))
            support["advanced_causal_reasoning"] = acr
            support["available"] = True
        except Exception as exc:
            support["advanced_causal_reasoning_error"] = repr(exc)
        return support

    def _anomaly_support(self) -> dict[str, Any]:
        try:
            from ontology.metrics_anomaly_detection_engine import MetricsAnomalyDetectionEngine
            result = MetricsAnomalyDetectionEngine(root=self.root).step(inputs={})
            return {
                "available": True,
                "anomaly_score": _clamp(result.get("anomaly_score")),
                "anomaly_count": int(result.get("anomaly_count", 0) or 0),
                "result": result,
            }
        except Exception as exc:
            return {"available": False, "anomaly_score": 0.0, "anomaly_count": 0, "error": repr(exc)}

    def evaluate(self, inputs: Mapping[str, Any] | None = None, history_limit: int = 128) -> dict[str, Any]:
        data = _as_mapping(inputs)
        correlation = self._collect_correlation(data)
        latest = self._collect_latest(data)
        history = self._collect_history(data, limit=history_limit)
        series = {axis: self._series(axis, history[axis], latest[axis]) for axis in ("identity", "strategy", "memory")}
        current_scores = {axis: _clamp(values[-1] if values else 0.0) for axis, values in series.items()}
        deltas = {axis: round(_delta(values), 6) for axis, values in series.items()}
        positive_deltas = {axis: round(_positive_delta(values), 6) for axis, values in series.items()}
        edges = self._detect_edges(series, correlation)
        chains = self._chains_from_edges(edges)
        strongest_edge = edges[0] if edges else None
        strongest_chain = chains[0] if chains else None
        correlation_risk = _clamp(correlation.get("coordinated_drift_risk_index", 0.0))
        systemic_coupling = _clamp(correlation.get("systemic_drift_coupling_index", 0.0))
        edge_strength = _clamp(strongest_edge.get("edge_strength") if strongest_edge else 0.0)
        chain_strength = _clamp(strongest_chain.get("strength") if strongest_chain else 0.0)
        propagation_density = _clamp(len([e for e in edges if _clamp(e.get("edge_strength")) >= 0.18]) / 6.0)
        cascade_count = len(chains)
        cascade_depth = int(max([c.get("length", 0) for c in chains] or [0]))
        causal_support = self._causal_support(strongest_edge)
        anomaly_support = self._anomaly_support()
        causal_index = _clamp(max(causal_support.get("causal_inference_index", 0.0), causal_support.get("confidence_score", 0.0)))
        anomaly_score = _clamp(anomaly_support.get("anomaly_score", 0.0))
        cascade_strength = _clamp((0.35 * edge_strength) + (0.30 * chain_strength) + (0.20 * systemic_coupling) + (0.15 * causal_index))
        cascade_risk_index = _clamp((0.35 * cascade_strength) + (0.25 * correlation_risk) + (0.20 * propagation_density) + (0.20 * anomaly_score))
        early_warning_score = _clamp((0.40 * _mean(positive_deltas.values())) + (0.25 * systemic_coupling) + (0.20 * propagation_density) + (0.15 * anomaly_score))
        sample_lengths = {axis: len(values) for axis, values in series.items()}
        minimum_sample_length = min(sample_lengths.values()) if sample_lengths else 0
        detection_reliability = _clamp((minimum_sample_length - 1) / 9.0) if minimum_sample_length > 1 else 0.0
        return {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": _utc_now(),
            "current_drift_scores": current_scores,
            "drift_deltas": deltas,
            "positive_drift_deltas": positive_deltas,
            "cascade_edges": edges,
            "detected_cascade_chains": chains,
            "cascade_count": cascade_count,
            "cascade_depth": cascade_depth,
            "cascade_strength": round(cascade_strength, 6),
            "propagation_density": round(propagation_density, 6),
            "cascade_risk_index": round(cascade_risk_index, 6),
            "early_warning_score": round(early_warning_score, 6),
            "strongest_edge": strongest_edge or {},
            "strongest_chain": strongest_chain or {},
            "causal_support": causal_support,
            "anomaly_support": anomaly_support,
            "upstream_correlation_summary": {
                "systemic_drift_coupling_index": round(systemic_coupling, 6),
                "coordinated_drift_risk_index": round(correlation_risk, 6),
                "correlation_reliability": _clamp(correlation.get("correlation_reliability", 0.0)),
            },
            "sample_lengths": sample_lengths,
            "detection_reliability": round(detection_reliability, 6),
            "classification": self._classify(cascade_risk_index, early_warning_score),
            "monitor_ready": True,
            "epistemic_status": self.epistemic_status,
            "diagnostics": {
                "measurement_only": True,
                "history_limit": history_limit,
                "uses_drift_correlation_analyzer": True,
                "uses_causal_inference": causal_support.get("causal_inference") is not None,
                "uses_advanced_causal_reasoning_engine": causal_support.get("advanced_causal_reasoning") is not None,
                "uses_metrics_anomaly_detection_engine": anomaly_support.get("available") is True,
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
        archive_path = self.drift_dir / f"drift_cascade_detector_{stamp}.json"
        payload = json.dumps(dict(result), ensure_ascii=False, indent=2, sort_keys=True, default=str)
        archive_path.write_text(payload, encoding="utf-8")
        self.latest_path.write_text(payload, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(result), ensure_ascii=False, sort_keys=True, default=str))
            handle.write("\n")


def step(inputs: Mapping[str, Any] | None = None, persist: bool = True, history_limit: int = 128) -> dict[str, Any]:
    return DriftCascadeDetector().step(inputs=inputs, persist=persist, history_limit=history_limit)

