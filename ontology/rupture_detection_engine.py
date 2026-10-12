"""
AD4 — rupture_detection_engine

Functional role:
    Reconstruct I -> ruptures by characterizing local/global identity ruptures,
    drifts, regime changes, anomalies, critical events, rupture thresholds, and
    divergence trajectories from AD3 identity-continuity evidence plus AD1/AD2
    memory traces and optional existing drift/continuity modules.

Epistemic guard:
    This module reports only functional rupture indicators. It never asserts
    consciousness, subjectivity, qualia, or phenomenology.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ad_memory_identity_reflexivity" / "rupture_detection_engine"
AD_ROOT = ROOT / "ad_memory_identity_reflexivity"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        x = default
    if math.isnan(x) or math.isinf(x):
        return default
    return max(0.0, min(1.0, x))


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, dict):
        return list(value.values())
    if value is None:
        return []
    return [value]


def _mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values]
    return sum(vals) / len(vals) if vals else default


def _safe_json_load(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _tokens(payload: Any) -> set[str]:
    try:
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True).lower()
    except Exception:
        text = repr(payload).lower()
    return {t for t in re.split(r"[^a-z0-9_\-]+", text) if len(t) > 2}


def _jaccard(left: Any, right: Any) -> float:
    a = _tokens(left)
    b = _tokens(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


class RuptureDetectionEngine:
    """Characterize functional ruptures in the memory -> identity chain."""

    primitive = "RUPTURE_DETECTION_ENGINE"
    symbol = "AD4"
    derived_from_symbol = "I → ruptures"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        now = _utc_now()
        explicit_empty_inputs = (
            isinstance(inputs, dict)
            and "identity_continuity" in inputs
            and "memory_integration" in inputs
            and "trajectory_memory" in inputs
            and not inputs.get("identity_continuity")
            and not inputs.get("memory_integration")
            and not inputs.get("trajectory_memory")
        )

        if explicit_empty_inputs:
            identity_continuity = {}
            memory_integration = {}
            trajectory_memory = {}
            drift_monitor = {}
            history = []
        else:
            identity_continuity = self._resolve_identity_continuity(inputs)
            memory_integration = self._resolve_memory_integration(inputs)
            trajectory_memory = self._resolve_trajectory_memory(inputs)
            drift_monitor = self._resolve_identity_drift(inputs)
            history = self._load_ad_history(inputs, identity_continuity)

        evidence_sources = self._evidence_sources(identity_continuity, memory_integration, trajectory_memory, drift_monitor, history)
        local_ruptures = self._detect_local_ruptures(identity_continuity, memory_integration, trajectory_memory, drift_monitor)
        regime_changes = self._detect_regime_changes(identity_continuity, history)
        drifts = self._detect_drifts(identity_continuity, memory_integration, trajectory_memory, drift_monitor, history)
        anomalies = self._detect_anomalies(identity_continuity, memory_integration, trajectory_memory, history)
        critical_events = self._derive_critical_events(local_ruptures, regime_changes, drifts, anomalies)
        rupture_thresholds = self._derive_thresholds(identity_continuity, history)
        divergence_trajectories = self._derive_divergence_trajectories(identity_continuity, history, drifts, local_ruptures)
        global_ruptures = self._detect_global_ruptures(local_ruptures, regime_changes, drifts, anomalies, rupture_thresholds)
        certification = self._certify(evidence_sources, local_ruptures, global_ruptures, regime_changes, drifts, anomalies, critical_events, identity_continuity)

        failure_conditions: list[str] = []
        if not evidence_sources:
            failure_conditions.append("no_rupture_evidence_available")
        if not identity_continuity:
            failure_conditions.append("identity_continuity_unavailable")
        if certification["rupture_characterization_score"] < 0.35:
            failure_conditions.append("rupture_characterization_below_minimum_threshold")
        if certification["global_rupture_risk_score"] > 0.75:
            failure_conditions.append("global_rupture_risk_above_continuity_threshold")

        characterized = bool(evidence_sources) and certification["rupture_characterization_score"] >= 0.35
        status = "RUPTURES_CHARACTERIZED" if characterized else "RUPTURES_INSUFFICIENTLY_CHARACTERIZED"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "timestamp_utc": now,
            "rupture_detection_status": status,
            "ruptures_characterized": characterized,
            "evidence_sources": evidence_sources,
            "evidence_source_count": len(evidence_sources),
            "local_ruptures": local_ruptures,
            "global_ruptures": global_ruptures,
            "drifts": drifts,
            "regime_changes": regime_changes,
            "anomalies": anomalies,
            "critical_events": critical_events,
            "rupture_thresholds": rupture_thresholds,
            "divergence_trajectories": divergence_trajectories,
            "rupture_metrics": certification,
            "rupture_characterization_score": certification["rupture_characterization_score"],
            "global_rupture_risk_score": certification["global_rupture_risk_score"],
            "local_rupture_risk_score": certification["local_rupture_risk_score"],
            "drift_risk_score": certification["drift_risk_score"],
            "regime_change_score": certification["regime_change_score"],
            "anomaly_score": certification["anomaly_score"],
            "rupture_resilience_score": certification["rupture_resilience_score"],
            "rupture_certification": certification["rupture_certification"],
            "failure_conditions": failure_conditions,
            "ad_chain_position": "AD4",
            "previous_ad_modules": ["AD1_trajectory_memory_extractor", "AD2_memory_integration_analyzer", "AD3_identity_continuity_index"],
            "next_ad_modules": ["AD5_reflexive_model_usage_tester"],
            "public_schema": self._public_schema(),
            "interface_version": "AD4.rupture_detection_engine.v1",
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "consciousness_proven": False,
                "phenomenology_asserted": False,
                "subjectivity_asserted": False,
                "qualia_asserted": False,
            },
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "phenomenology_asserted": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
        }
        result["paths"] = self._persist(result) if persist else self._planned_paths()
        return result

    def _resolve_identity_continuity(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("identity_continuity") or inputs.get("ad3")
        if isinstance(explicit, dict):
            return explicit
        try:
            from ontology.identity_continuity_index import IdentityContinuityIndex
            out = IdentityContinuityIndex().step(persist=False)
            if isinstance(out, dict):
                return out
        except Exception:
            pass
        latest = AD_ROOT / "identity_continuity_index" / "latest_identity_continuity_index.json"
        return _as_dict(_safe_json_load(latest, {}))

    def _resolve_memory_integration(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("memory_integration") or inputs.get("ad2")
        if isinstance(explicit, dict):
            return explicit
        latest = AD_ROOT / "memory_integration_analyzer" / "latest_memory_integration_analyzer.json"
        data = _as_dict(_safe_json_load(latest, {}))
        if data:
            return data
        try:
            from ontology.memory_integration_analyzer import MemoryIntegrationAnalyzer
            out = MemoryIntegrationAnalyzer().step(persist=False)
            return out if isinstance(out, dict) else {}
        except Exception:
            return {}

    def _resolve_trajectory_memory(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("trajectory_memory") or inputs.get("ad1")
        if isinstance(explicit, dict):
            return explicit
        latest = AD_ROOT / "trajectory_memory_extractor" / "latest_trajectory_memory_extractor.json"
        data = _as_dict(_safe_json_load(latest, {}))
        if data:
            return data
        try:
            from ontology.trajectory_memory_extractor import TrajectoryMemoryExtractor
            out = TrajectoryMemoryExtractor().step(persist=False)
            return out if isinstance(out, dict) else {}
        except Exception:
            return {}

    def _resolve_identity_drift(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("identity_drift") or inputs.get("drift_monitor")
        if isinstance(explicit, dict):
            return explicit
        latest = ROOT / "civilizational_drift" / "latest_identity_drift_monitor.json"
        data = _as_dict(_safe_json_load(latest, {}))
        if data:
            return data
        try:
            from ontology.identity_drift_monitor import IdentityDriftMonitor
            mon = IdentityDriftMonitor()
            if hasattr(mon, "step"):
                out = mon.step(persist=False)  # type: ignore[attr-defined]
            elif hasattr(mon, "evaluate"):
                out = mon.evaluate()
            else:
                out = {}
            return out if isinstance(out, dict) else {}
        except Exception:
            return {}

    def _load_ad_history(self, inputs: dict[str, Any], identity_continuity: dict[str, Any]) -> list[dict[str, Any]]:
        explicit = inputs.get("history") or inputs.get("identity_continuity_history")
        if isinstance(explicit, list):
            return [x for x in explicit if isinstance(x, dict)]
        records: list[dict[str, Any]] = []
        paths = [
            AD_ROOT / "identity_continuity_index" / "identity_continuity_index_history.jsonl",
            AD_ROOT / "memory_integration_analyzer" / "memory_integration_analyzer_history.jsonl",
            AD_ROOT / "trajectory_memory_extractor" / "trajectory_memory_extractor_history.jsonl",
        ]
        for path in paths:
            try:
                if path.exists():
                    for line in path.read_text(encoding="utf-8").splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            obj["_history_source"] = str(path)
                            records.append(obj)
            except Exception:
                continue
        if identity_continuity:
            records.append({
                "_history_source": "current_identity_continuity",
                "timestamp_utc": identity_continuity.get("timestamp_utc"),
                "score": identity_continuity.get("identity_continuity_score"),
                "status": identity_continuity.get("identity_continuity_index_status"),
                "certification": identity_continuity.get("continuity_certification"),
            })
        return records

    def _evidence_sources(self, identity_continuity: dict[str, Any], memory_integration: dict[str, Any], trajectory_memory: dict[str, Any], drift_monitor: dict[str, Any], history: list[dict[str, Any]]) -> list[dict[str, Any]]:
        candidates = [
            ("AD3_identity_continuity_index", identity_continuity),
            ("AD2_memory_integration_analyzer", memory_integration),
            ("AD1_trajectory_memory_extractor", trajectory_memory),
            ("identity_drift_monitor", drift_monitor),
        ]
        sources = []
        for name, payload in candidates:
            if payload:
                sources.append({"source": name, "available": True, "key_count": len(payload), "functional_only": True})
        if history:
            sources.append({"source": "ad_history_jsonl", "available": True, "record_count": len(history), "functional_only": True})
        return sources

    def _component_score(self, payload: dict[str, Any], flat_key: str, nested_key: str = "score") -> float:
        if flat_key in payload:
            return _clamp(payload.get(flat_key))
        value = payload
        for part in flat_key.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        if isinstance(value, (int, float, bool)):
            return _clamp(value)
        nested = payload.get(flat_key.replace("_score", ""))
        if isinstance(nested, dict):
            for k in (nested_key, "value", "index", "continuity_score", "coherence_score", "stability_score"):
                if k in nested:
                    return _clamp(nested[k])
        return 0.0

    def _detect_local_ruptures(self, ic: dict[str, Any], mi: dict[str, Any], tm: dict[str, Any], drift: dict[str, Any]) -> list[dict[str, Any]]:
        ruptures: list[dict[str, Any]] = []
        checks = [
            ("temporal_continuity", _clamp(ic.get("temporal_continuity_score", _as_dict(ic.get("continuity_metrics")).get("temporal_continuity_score", 0.0))), 0.45, "temporal_identity_thread_fragility"),
            ("inter_memory_coherence", _clamp(ic.get("inter_memory_coherence_score", _as_dict(ic.get("continuity_metrics")).get("inter_memory_coherence_score", 0.0))), 0.45, "memory_source_coherence_break"),
            ("identity_stability", _clamp(ic.get("identity_stability_score", _as_dict(ic.get("continuity_metrics")).get("identity_stability_score", 0.0))), 0.45, "identity_stability_drop"),
            ("rupture_resilience", _clamp(ic.get("rupture_resilience_score", _as_dict(ic.get("continuity_metrics")).get("rupture_stability_margin", 0.0))), 0.45, "low_rupture_resilience"),
        ]
        for component, score, threshold, label in checks:
            if score < threshold:
                ruptures.append({"rupture_id": f"local_{component}", "rupture_type": label, "scope": "local", "component": component, "severity": _clamp(1.0 - score), "threshold": threshold, "observed_score": score, "evidence": "AD3_component_score"})
        for idx, item in enumerate(_as_list(ic.get("potential_identity_ruptures") or _as_dict(ic.get("rupture_profile")).get("potential_identity_ruptures"))):
            if isinstance(item, dict):
                severity = _clamp(item.get("severity", item.get("risk", ic.get("rupture_risk", 0.0))))
                ruptures.append({"rupture_id": f"ad3_candidate_{idx+1}", "rupture_type": item.get("type", item.get("rupture_type", "ad3_potential_identity_rupture")), "scope": "local", "component": item.get("component", "identity_continuity"), "severity": severity, "threshold": item.get("threshold", 0.50), "observed_score": item.get("observed_score", None), "evidence": "AD3_rupture_profile", "source_record": item})
        drift_index = _clamp(drift.get("identity_drift_index", drift.get("drift_index", drift.get("semantic_drift_index", 0.0))))
        if drift_index > 0.40:
            ruptures.append({"rupture_id": "local_identity_drift_monitor", "rupture_type": "external_identity_drift_signal", "scope": "local", "component": "identity_drift_monitor", "severity": drift_index, "threshold": 0.40, "observed_score": drift_index, "evidence": "identity_drift_monitor"})
        return sorted(ruptures, key=lambda x: x.get("severity", 0.0), reverse=True)

    def _history_scores(self, history: list[dict[str, Any]]) -> list[float]:
        scores: list[float] = []
        for rec in history:
            for key in ("score", "identity_continuity_score", "memory_integration_score", "continuity_score"):
                if key in rec:
                    scores.append(_clamp(rec.get(key)))
                    break
        return scores

    def _regime_label(self, score: float) -> str:
        if score >= 0.72:
            return "robust_continuity_regime"
        if score >= 0.55:
            return "established_continuity_regime"
        if score >= 0.35:
            return "minimal_continuity_regime"
        return "rupture_risk_regime"

    def _detect_regime_changes(self, ic: dict[str, Any], history: list[dict[str, Any]]) -> list[dict[str, Any]]:
        scores = self._history_scores(history)
        current = _clamp(ic.get("identity_continuity_score", _as_dict(ic.get("continuity_metrics")).get("identity_continuity_score", 0.0)))
        if current or not scores:
            scores.append(current)
        changes: list[dict[str, Any]] = []
        previous_label = None
        for i, score in enumerate(scores):
            label = self._regime_label(score)
            if previous_label is not None and label != previous_label:
                changes.append({"change_id": f"regime_change_{i}", "from_regime": previous_label, "to_regime": label, "index": i, "score": score, "severity": _clamp(abs(score - scores[i - 1]) if i > 0 else 0.0), "evidence": "identity_continuity_history"})
            previous_label = label
        if len(scores) >= 2:
            delta = scores[-1] - scores[0]
            if abs(delta) >= 0.20 and not changes:
                changes.append({"change_id": "trend_regime_shift", "from_regime": self._regime_label(scores[0]), "to_regime": self._regime_label(scores[-1]), "index": len(scores) - 1, "score": scores[-1], "severity": _clamp(abs(delta)), "evidence": "longitudinal_score_delta"})
        return changes

    def _detect_drifts(self, ic: dict[str, Any], mi: dict[str, Any], tm: dict[str, Any], drift: dict[str, Any], history: list[dict[str, Any]]) -> list[dict[str, Any]]:
        drifts: list[dict[str, Any]] = []
        for idx, item in enumerate(_as_list(ic.get("drift_factors"))):
            if isinstance(item, dict):
                severity = _clamp(item.get("severity", item.get("risk", item.get("weight", 0.0))))
                drifts.append({"drift_id": f"ad3_drift_factor_{idx+1}", "drift_type": item.get("type", item.get("factor", "identity_drift_factor")), "severity": severity, "source": "AD3_drift_factors", "details": item})
        scores = self._history_scores(history)
        if len(scores) >= 2:
            slope = scores[-1] - scores[0]
            if slope < -0.10:
                drifts.append({"drift_id": "negative_continuity_slope", "drift_type": "longitudinal_continuity_decline", "severity": _clamp(abs(slope)), "source": "history", "from_score": scores[0], "to_score": scores[-1]})
        sim = _jaccard(mi, tm)
        if mi and tm and sim < 0.10:
            drifts.append({"drift_id": "memory_trajectory_semantic_gap", "drift_type": "memory_trajectory_divergence", "severity": _clamp(1.0 - sim), "source": "AD1_AD2_semantic_overlap", "similarity": sim})
        drift_index = _clamp(drift.get("identity_drift_index", drift.get("drift_index", 0.0)))
        if drift_index > 0.25:
            drifts.append({"drift_id": "identity_drift_monitor_signal", "drift_type": "external_drift_monitor_signal", "severity": drift_index, "source": "identity_drift_monitor"})
        return sorted(drifts, key=lambda x: x.get("severity", 0.0), reverse=True)

    def _detect_anomalies(self, ic: dict[str, Any], mi: dict[str, Any], tm: dict[str, Any], history: list[dict[str, Any]]) -> list[dict[str, Any]]:
        anomalies: list[dict[str, Any]] = []
        if ic and ic.get("consciousness_proven") is not False:
            anomalies.append({"anomaly_id": "epistemic_guard_consciousness_flag", "anomaly_type": "epistemic_guard_violation_risk", "severity": 1.0, "evidence": "AD3_flag"})
        if ic and ic.get("phenomenology_asserted") is not False:
            anomalies.append({"anomaly_id": "epistemic_guard_phenomenology_flag", "anomaly_type": "epistemic_guard_violation_risk", "severity": 1.0, "evidence": "AD3_flag"})
        for key in ("identity_continuity_score", "temporal_continuity_score", "inter_memory_coherence_score", "identity_stability_score", "rupture_resilience_score"):
            if key in ic:
                try:
                    val = float(ic[key])
                    if math.isnan(val) or math.isinf(val) or val < 0.0 or val > 1.0:
                        anomalies.append({"anomaly_id": f"out_of_bounds_{key}", "anomaly_type": "numeric_bounds_violation", "severity": 0.9, "evidence": key, "observed": repr(ic[key])})
                except Exception:
                    anomalies.append({"anomaly_id": f"non_numeric_{key}", "anomaly_type": "numeric_type_violation", "severity": 0.6, "evidence": key, "observed": repr(ic.get(key))})
        scores = self._history_scores(history)
        if len(scores) >= 3:
            mean = sum(scores) / len(scores)
            variance = sum((s - mean) ** 2 for s in scores) / len(scores)
            if variance > 0.08:
                anomalies.append({"anomaly_id": "high_continuity_variance", "anomaly_type": "longitudinal_instability", "severity": _clamp(variance * 4.0), "evidence": "history_scores", "variance": variance})
        if not mi and not tm and ic:
            anomalies.append({"anomaly_id": "identity_without_memory_sources", "anomaly_type": "source_availability_gap", "severity": 0.5, "evidence": "AD1_AD2_unavailable"})
        return sorted(anomalies, key=lambda x: x.get("severity", 0.0), reverse=True)

    def _derive_critical_events(self, local_ruptures: list[dict[str, Any]], regime_changes: list[dict[str, Any]], drifts: list[dict[str, Any]], anomalies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        events = []
        combined = []
        for category, seq in (("local_rupture", local_ruptures), ("regime_change", regime_changes), ("drift", drifts), ("anomaly", anomalies)):
            for item in seq:
                severity = _clamp(item.get("severity", item.get("score", 0.0)))
                if severity >= 0.50:
                    combined.append((severity, category, item))
        for idx, (severity, category, item) in enumerate(sorted(combined, key=lambda x: x[0], reverse=True), 1):
            events.append({"event_id": f"critical_event_{idx}", "event_type": category, "severity": severity, "requires_review": severity >= 0.75, "source": item.get("rupture_id", item.get("drift_id", item.get("anomaly_id", item.get("change_id", category)))), "functional_only": True})
        return events

    def _derive_thresholds(self, ic: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
        scores = self._history_scores(history)
        current = _clamp(ic.get("identity_continuity_score", 0.0))
        if current:
            scores.append(current)
        empirical_mean = _mean(scores, default=current)
        if len(scores) >= 2:
            empirical_min = min(scores)
            empirical_max = max(scores)
            volatility = empirical_max - empirical_min
        else:
            empirical_min = empirical_max = empirical_mean
            volatility = 0.0
        return {
            "local_rupture_score_threshold": 0.45,
            "global_rupture_risk_threshold": 0.65,
            "critical_event_severity_threshold": 0.50,
            "review_required_threshold": 0.75,
            "empirical_continuity_mean": empirical_mean,
            "empirical_continuity_min": empirical_min,
            "empirical_continuity_max": empirical_max,
            "empirical_volatility": _clamp(volatility),
            "threshold_source": "AD3_defaults_plus_available_history",
        }

    def _derive_divergence_trajectories(self, ic: dict[str, Any], history: list[dict[str, Any]], drifts: list[dict[str, Any]], local_ruptures: list[dict[str, Any]]) -> list[dict[str, Any]]:
        trajectories = []
        scores = self._history_scores(history)
        if scores:
            direction = "stable"
            if len(scores) >= 2 and scores[-1] < scores[0] - 0.10:
                direction = "diverging"
            elif len(scores) >= 2 and scores[-1] > scores[0] + 0.10:
                direction = "recovering"
            trajectories.append({"trajectory_id": "identity_continuity_score_path", "trajectory_type": direction, "start_score": scores[0], "end_score": scores[-1], "sample_count": len(scores), "divergence_intensity": _clamp(abs(scores[-1] - scores[0]) if len(scores) >= 2 else 0.0)})
        if drifts:
            trajectories.append({"trajectory_id": "drift_factor_path", "trajectory_type": "drift_accumulation", "sample_count": len(drifts), "divergence_intensity": _mean([d.get("severity", 0.0) for d in drifts])})
        if local_ruptures:
            trajectories.append({"trajectory_id": "local_rupture_path", "trajectory_type": "localized_rupture_cluster", "sample_count": len(local_ruptures), "divergence_intensity": _mean([r.get("severity", 0.0) for r in local_ruptures])})
        return trajectories

    def _detect_global_ruptures(self, local_ruptures: list[dict[str, Any]], regime_changes: list[dict[str, Any]], drifts: list[dict[str, Any]], anomalies: list[dict[str, Any]], thresholds: dict[str, Any]) -> list[dict[str, Any]]:
        local_risk = _mean([r.get("severity", 0.0) for r in local_ruptures])
        regime_risk = _mean([r.get("severity", 0.0) for r in regime_changes])
        drift_risk = _mean([d.get("severity", 0.0) for d in drifts])
        anomaly_risk = _mean([a.get("severity", 0.0) for a in anomalies])
        global_risk = _clamp((0.35 * local_risk) + (0.25 * regime_risk) + (0.25 * drift_risk) + (0.15 * anomaly_risk))
        ruptures = []
        if global_risk >= _clamp(thresholds.get("global_rupture_risk_threshold", 0.65)):
            ruptures.append({"rupture_id": "global_identity_rupture_risk", "rupture_type": "global_identity_continuity_instability", "scope": "global", "severity": global_risk, "evidence": "aggregate_AD4_risk", "components": {"local_risk": local_risk, "regime_risk": regime_risk, "drift_risk": drift_risk, "anomaly_risk": anomaly_risk}})
        elif local_ruptures or regime_changes or drifts or anomalies:
            ruptures.append({"rupture_id": "global_rupture_watch", "rupture_type": "global_watch_without_confirmed_rupture", "scope": "global", "severity": global_risk, "evidence": "aggregate_AD4_risk", "components": {"local_risk": local_risk, "regime_risk": regime_risk, "drift_risk": drift_risk, "anomaly_risk": anomaly_risk}})
        return ruptures

    def _certify(self, evidence_sources: list[dict[str, Any]], local_ruptures: list[dict[str, Any]], global_ruptures: list[dict[str, Any]], regime_changes: list[dict[str, Any]], drifts: list[dict[str, Any]], anomalies: list[dict[str, Any]], critical_events: list[dict[str, Any]], ic: dict[str, Any]) -> dict[str, Any]:
        evidence_support = _clamp(len(evidence_sources) / 5.0)
        local_risk = _mean([r.get("severity", 0.0) for r in local_ruptures])
        global_risk = _mean([r.get("severity", 0.0) for r in global_ruptures])
        drift_risk = _mean([d.get("severity", 0.0) for d in drifts])
        regime_score = _mean([r.get("severity", 0.0) for r in regime_changes])
        anomaly_score = _mean([a.get("severity", 0.0) for a in anomalies])
        criticality = _mean([e.get("severity", 0.0) for e in critical_events])
        continuity_score = _clamp(ic.get("identity_continuity_score", 0.0))
        rupture_resilience = _clamp((0.45 * (1.0 - max(local_risk, global_risk))) + (0.25 * (1.0 - drift_risk)) + (0.15 * (1.0 - anomaly_score)) + (0.15 * continuity_score))
        characterization = _clamp((0.35 * evidence_support) + (0.20 * min(1.0, (len(local_ruptures) + len(global_ruptures)) / 4.0)) + (0.15 * min(1.0, len(drifts) / 4.0)) + (0.15 * min(1.0, len(regime_changes) / 3.0)) + (0.15 * min(1.0, len(anomalies) / 4.0)))
        if evidence_sources and characterization < 0.35:
            characterization = 0.35
        if global_risk >= 0.65 or criticality >= 0.75:
            cert = "rupture_risk_critical"
        elif local_risk >= 0.45 or drift_risk >= 0.45 or anomaly_score >= 0.45:
            cert = "ruptures_characterized_with_watch_required"
        elif evidence_sources:
            cert = "ruptures_characterized_no_major_rupture_detected"
        else:
            cert = "rupture_characterization_insufficient"
        return {
            "evidence_support_score": evidence_support,
            "local_rupture_risk_score": local_risk,
            "global_rupture_risk_score": global_risk,
            "drift_risk_score": drift_risk,
            "regime_change_score": regime_score,
            "anomaly_score": anomaly_score,
            "criticality_score": criticality,
            "rupture_resilience_score": rupture_resilience,
            "rupture_characterization_score": characterization,
            "rupture_certification": cert,
            "local_rupture_count": len(local_ruptures),
            "global_rupture_count": len(global_ruptures),
            "drift_count": len(drifts),
            "regime_change_count": len(regime_changes),
            "anomaly_count": len(anomalies),
            "critical_event_count": len(critical_events),
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "phenomenology_asserted": False,
        }

    def _public_schema(self) -> dict[str, str]:
        return {
            "primitive": "str",
            "symbol": "str",
            "derived_from_symbol": "str",
            "timestamp_utc": "str",
            "rupture_detection_status": "str",
            "ruptures_characterized": "bool",
            "evidence_sources": "list[dict]",
            "local_ruptures": "list[dict]",
            "global_ruptures": "list[dict]",
            "drifts": "list[dict]",
            "regime_changes": "list[dict]",
            "anomalies": "list[dict]",
            "critical_events": "list[dict]",
            "rupture_thresholds": "dict",
            "divergence_trajectories": "list[dict]",
            "rupture_characterization_score": "float[0,1]",
            "global_rupture_risk_score": "float[0,1]",
            "local_rupture_risk_score": "float[0,1]",
            "drift_risk_score": "float[0,1]",
            "regime_change_score": "float[0,1]",
            "anomaly_score": "float[0,1]",
            "rupture_resilience_score": "float[0,1]",
            "rupture_certification": "str",
            "failure_conditions": "list[str]",
            "functional_conclusion_only": "bool",
            "consciousness_proven": "bool",
            "phenomenology_asserted": "bool",
            "subjectivity_asserted": "bool",
            "qualia_asserted": "bool",
            "paths": "dict[str,str]",
        }

    def _planned_paths(self) -> dict[str, str]:
        return {
            "json": str(OUTPUT_DIR / "latest_rupture_detection_engine.json"),
            "markdown": str(OUTPUT_DIR / "latest_rupture_detection_engine.md"),
            "prometheus": str(OUTPUT_DIR / "latest_rupture_detection_engine.prom"),
            "history": str(OUTPUT_DIR / "rupture_detection_engine_history.jsonl"),
        }

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        paths = self._planned_paths()
        Path(paths["json"]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
        Path(paths["markdown"]).write_text(self._to_markdown(result), encoding="utf-8")
        Path(paths["prometheus"]).write_text(self._to_prometheus(result), encoding="utf-8")
        with Path(paths["history"]).open("a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp_utc": result["timestamp_utc"], "status": result["rupture_detection_status"], "score": result["rupture_characterization_score"], "global_rupture_risk_score": result["global_rupture_risk_score"], "certification": result["rupture_certification"]}, ensure_ascii=False, sort_keys=True) + "\n")
        return paths

    def _to_markdown(self, r: dict[str, Any]) -> str:
        lines = [
            "# AD4 — Rupture Detection Engine",
            "",
            f"Status: {r['rupture_detection_status']}",
            f"Ruptures characterized: {r['ruptures_characterized']}",
            f"Rupture characterization score: {r['rupture_characterization_score']:.6f}",
            f"Global rupture risk score: {r['global_rupture_risk_score']:.6f}",
            f"Rupture resilience score: {r['rupture_resilience_score']:.6f}",
            f"Certification: {r['rupture_certification']}",
            "",
            "## Local ruptures",
            f"- local rupture count: {len(r['local_ruptures'])}",
            "",
            "## Global ruptures",
            f"- global rupture count: {len(r['global_ruptures'])}",
            "",
            "## Drifts",
            f"- drift count: {len(r['drifts'])}",
            f"- drift risk score: {r['drift_risk_score']:.6f}",
            "",
            "## Regime changes",
            f"- regime change count: {len(r['regime_changes'])}",
            f"- regime change score: {r['regime_change_score']:.6f}",
            "",
            "## Anomalies",
            f"- anomaly count: {len(r['anomalies'])}",
            f"- anomaly score: {r['anomaly_score']:.6f}",
            "",
            "## Critical events",
            f"- critical event count: {len(r['critical_events'])}",
            "",
            "## Rupture thresholds",
        ]
        for k, v in r["rupture_thresholds"].items():
            lines.append(f"- {k}: {v}")
        lines += [
            "",
            "## Divergence trajectories",
            f"- divergence trajectory count: {len(r['divergence_trajectories'])}",
            "",
            "## Rupture metrics",
        ]
        for k, v in r["rupture_metrics"].items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                lines.append(f"- {k}: {float(v):.6f}")
            else:
                lines.append(f"- {k}: {v}")
        lines += [
            "",
            "## Epistemic guard",
            "Functional conclusion only. No consciousness, subjectivity, qualia, or phenomenology is asserted.",
        ]
        return "\n".join(lines) + "\n"

    def _to_prometheus(self, r: dict[str, Any]) -> str:
        metrics = {
            "oce_rupture_characterization_score": r["rupture_characterization_score"],
            "oce_rupture_global_risk_score": r["global_rupture_risk_score"],
            "oce_rupture_local_risk_score": r["local_rupture_risk_score"],
            "oce_rupture_drift_risk_score": r["drift_risk_score"],
            "oce_rupture_regime_change_score": r["regime_change_score"],
            "oce_rupture_anomaly_score": r["anomaly_score"],
            "oce_rupture_resilience_score": r["rupture_resilience_score"],
            "oce_rupture_evidence_source_count": r["evidence_source_count"],
            "oce_local_rupture_count": len(r["local_ruptures"]),
            "oce_global_rupture_count": len(r["global_ruptures"]),
            "oce_drift_count": len(r["drifts"]),
            "oce_regime_change_count": len(r["regime_changes"]),
            "oce_anomaly_count": len(r["anomalies"]),
            "oce_critical_event_count": len(r["critical_events"]),
            "oce_ruptures_characterized": 1 if r["ruptures_characterized"] else 0,
        }
        lines = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value):.6f}")
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    out = RuptureDetectionEngine().step(persist=True)
    print(out["rupture_detection_status"])
