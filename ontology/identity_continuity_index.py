"""
AD3 — identity_continuity_index

Functional role:
    Reconstruct M -> I by estimating identity continuity from AD1 trajectory
    memory and AD2 memory-integration evidence, plus existing identity and
    continuity modules when safely available.

Epistemic guard:
    This module reports only functional identity-continuity indicators.
    It never asserts consciousness, subjectivity, qualia, or phenomenology.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ad_memory_identity_reflexivity" / "identity_continuity_index"


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


def _mean(values: list[float], default: float = 0.0) -> float:
    clean = [_clamp(v) for v in values]
    return sum(clean) / len(clean) if clean else default


class IdentityContinuityIndex:
    """Estimate functional continuity of identity from integrated memory."""

    primitive = "IDENTITY_CONTINUITY_INDEX"
    symbol = "AD3"
    derived_from_symbol = "M → I"

    IDENTITY_COMPONENTS = [
        "memory_integration_analyzer", "trajectory_memory_extractor",
        "civilizational_identity_synthesis", "civilizational_identity_preservation",
        "civilizational_identity_baseline", "identity_drift_monitor",
        "continuity_metrics_engine", "civilizational_continuity_guardian",
        "genealogical_continuity", "narrative_identity_engine",
        "persistent_selfhood_benchmark", "personal_memory_recall_validator",
        "personal_memory_salience_engine", "self_model", "self_model_revision",
        "global_temporal_binding", "meta_cognition", "introspective_reporting",
    ]

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        now = _utc_now()
        explicit_empty_inputs = (
            isinstance(inputs, dict)
            and "memory_integration" in inputs and "trajectory_memory" in inputs
            and "identity_modules" in inputs and "synthetic_identity_records" in inputs
            and not inputs.get("memory_integration") and not inputs.get("trajectory_memory")
            and not inputs.get("identity_modules") and not _as_list(inputs.get("synthetic_identity_records"))
        )
        if explicit_empty_inputs:
            memory_integration, trajectory_memory, identity_modules, synthetic_identity_records = {}, {}, {}, []
        else:
            memory_integration = self._resolve_memory_integration(inputs)
            trajectory_memory = self._resolve_trajectory_memory(inputs, memory_integration)
            identity_modules = self._collect_identity_modules(inputs)
            synthetic_identity_records = _as_list(inputs.get("synthetic_identity_records"))

        identity_evidence = self._build_identity_evidence(memory_integration, trajectory_memory, identity_modules, synthetic_identity_records)
        temporal_profile = self._build_temporal_profile(memory_integration, trajectory_memory, identity_evidence)
        inter_memory_profile = self._build_inter_memory_profile(memory_integration, identity_evidence)
        stability_profile = self._build_stability_profile(identity_modules, identity_evidence)
        rupture_profile = self._build_rupture_profile(memory_integration, trajectory_memory, identity_modules)
        drift_factors = self._derive_drift_factors(memory_integration, trajectory_memory, identity_modules, rupture_profile)
        continuity_threads = self._derive_continuity_threads(memory_integration, trajectory_memory, identity_evidence)
        identity_bindings = self._derive_identity_bindings(memory_integration, trajectory_memory, identity_modules)
        certification = self._certify(identity_evidence, temporal_profile, inter_memory_profile, stability_profile, rupture_profile, drift_factors)

        failure_conditions: list[str] = []
        if not identity_evidence:
            failure_conditions.append("no_identity_evidence_available")
        if not memory_integration:
            failure_conditions.append("memory_integration_unavailable")
        if not trajectory_memory:
            failure_conditions.append("trajectory_memory_unavailable")
        if certification["identity_continuity_score"] < 0.35:
            failure_conditions.append("identity_continuity_below_minimum_threshold")
        if certification["rupture_risk"] > 0.65:
            failure_conditions.append("rupture_risk_above_stability_threshold")

        established = bool(identity_evidence) and certification["identity_continuity_score"] >= 0.35 and certification["rupture_risk"] <= 0.65
        status = "IDENTITY_CONTINUITY_ESTABLISHED" if established else "IDENTITY_CONTINUITY_INSUFFICIENT"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "timestamp_utc": now,
            "identity_continuity_index_status": status,
            "identity_continuity_established": established,
            "identity_evidence": identity_evidence,
            "identity_evidence_count": len(identity_evidence),
            "temporal_continuity": temporal_profile,
            "inter_memory_coherence": inter_memory_profile,
            "identity_stability": stability_profile,
            "rupture_profile": rupture_profile,
            "potential_identity_ruptures": rupture_profile.get("potential_identity_ruptures", []),
            "drift_factors": drift_factors,
            "continuity_threads": continuity_threads,
            "identity_bindings": identity_bindings,
            "continuity_metrics": certification,
            "identity_continuity_score": certification["identity_continuity_score"],
            "continuity_certification": certification["continuity_certification"],
            "failure_conditions": failure_conditions,
            "ad_chain_position": "AD3",
            "previous_ad_modules": ["AD1_trajectory_memory_extractor", "AD2_memory_integration_analyzer"],
            "next_ad_modules": ["AD4_rupture_detection_engine", "AD5_reflexive_model_usage_tester"],
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
        # AD3 v2 public interface normalization: keep nested scientific
        # structures while exposing stable flat aliases for tests, dashboards,
        # downstream AD4/AD5 modules, and external replication scripts.
        result["temporal_continuity_score"] = certification["temporal_continuity_score"]
        result["inter_memory_coherence_score"] = certification["inter_memory_coherence_score"]
        result["identity_stability_score"] = certification["identity_stability_score"]
        result["rupture_risk"] = certification["rupture_risk"]
        result["rupture_resilience_score"] = certification["rupture_stability_margin"]
        result["drift_penalty_margin"] = certification["drift_penalty_margin"]
        result["evidence_support_score"] = certification["evidence_support"]
        result["public_schema"] = self._public_schema()
        result["interface_version"] = "AD3.identity_continuity_index.v2"
        result["paths"] = self._persist(result) if persist else self._planned_paths()
        return result

    def _resolve_memory_integration(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("memory_integration") or inputs.get("ad2")
        if isinstance(explicit, dict):
            return explicit
        try:
            from ontology.memory_integration_analyzer import MemoryIntegrationAnalyzer
            out = MemoryIntegrationAnalyzer().step(inputs={"trajectory_memory": inputs.get("trajectory_memory")} if inputs.get("trajectory_memory") else None, persist=False)
            if isinstance(out, dict):
                return out
        except Exception:
            pass
        latest = ROOT / "ad_memory_identity_reflexivity" / "memory_integration_analyzer" / "latest_memory_integration_analyzer.json"
        try:
            if latest.exists():
                data = json.loads(latest.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            return {}
        return {}

    def _resolve_trajectory_memory(self, inputs: dict[str, Any], memory_integration: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("trajectory_memory") or inputs.get("ad1")
        if isinstance(explicit, dict):
            return explicit
        try:
            from ontology.trajectory_memory_extractor import TrajectoryMemoryExtractor
            out = TrajectoryMemoryExtractor().step(persist=False)
            if isinstance(out, dict):
                return out
        except Exception:
            pass
        latest = ROOT / "ad_memory_identity_reflexivity" / "trajectory_memory_extractor" / "latest_trajectory_memory_extractor.json"
        try:
            if latest.exists():
                data = json.loads(latest.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            return {}
        return {}

    def _collect_identity_modules(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("identity_modules")
        if isinstance(explicit, dict):
            return explicit
        outputs: dict[str, Any] = {}
        calls = [
            ("civilizational_identity_synthesis", "CivilizationalIdentitySynthesis"),
            ("civilizational_identity_preservation", "CivilizationalIdentityPreservation"),
            ("civilizational_identity_baseline", "CivilizationalIdentityBaseline"),
            ("identity_drift_monitor", "IdentityDriftMonitor"),
            ("continuity_metrics_engine", "ContinuityMetricsEngine"),
            ("civilizational_continuity_guardian", "CivilizationalContinuityGuardian"),
            ("genealogical_continuity", "GenealogicalContinuity"),
            ("narrative_identity_engine", "NarrativeIdentityEngine"),
            ("persistent_selfhood_benchmark", "PersistentSelfhoodBenchmark"),
            ("personal_memory_recall_validator", "PersonalMemoryRecallValidator"),
            ("personal_memory_salience_engine", "PersonalMemorySalienceEngine"),
            ("self_model", "SelfModel"),
            ("self_model_revision", "SelfModelRevision"),
            ("global_temporal_binding", "GlobalTemporalBinding"),
            ("meta_cognition", "MetaCognition"),
            ("introspective_reporting", "IntrospectiveReporting"),
        ]
        for module_name, class_name in calls:
            try:
                module = __import__(f"ontology.{module_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                if module_name in {"civilizational_identity_preservation", "continuity_metrics_engine"}:
                    out = cls().step(dry_run=True)
                else:
                    out = cls().step()
                if isinstance(out, dict):
                    outputs[module_name] = out
            except Exception:
                continue
        return outputs

    def _build_identity_evidence(self, memory_integration: dict[str, Any], trajectory_memory: dict[str, Any], identity_modules: dict[str, Any], synthetic_identity_records: list[Any]) -> list[dict[str, Any]]:
        evidence: list[dict[str, Any]] = []
        for i, rec in enumerate(synthetic_identity_records):
            item = _as_dict(rec)
            if item:
                evidence.append({"source": "synthetic_identity_record", "evidence_id": f"synthetic_{i:04d}", "kind": item.get("kind", "synthetic"), "score": _clamp(item.get("score", 0.5)), "payload": item})
        for key in ["identity_bindings", "identity_relevant_memory", "continuity_bindings", "reflexive_bindings"]:
            for i, item in enumerate(_as_list(memory_integration.get(key))):
                d = _as_dict(item)
                evidence.append({"source": f"AD2.{key}", "evidence_id": f"ad2_{key}_{i:04d}", "kind": key, "score": self._score_mapping(d, 0.55), "payload": d})
        for key in ["identity_relevant_events", "continuity_threads", "trajectory_segments", "trajectory_events"]:
            for i, item in enumerate(_as_list(trajectory_memory.get(key))[:200]):
                d = _as_dict(item)
                text = json.dumps(d, ensure_ascii=False, default=str).lower()
                if key in {"identity_relevant_events", "continuity_threads"} or any(term in text for term in ["identity", "continuity", "self", "lineage", "memory", "reflexive"]):
                    evidence.append({"source": f"AD1.{key}", "evidence_id": f"ad1_{key}_{i:04d}", "kind": key, "score": self._score_mapping(d, 0.50), "payload": d})
        for module_name, out in identity_modules.items():
            evidence.append({"source": f"module.{module_name}", "evidence_id": f"module_{module_name}", "kind": "identity_module_output", "score": self._score_mapping(out, 0.50), "payload": self._compact_payload(out)})
        return evidence[:500]

    def _score_mapping(self, mapping: Any, default: float = 0.5) -> float:
        d = _as_dict(mapping)
        if not d:
            return default
        score_keys = [k for k in d if any(token in k.lower() for token in ["score", "index", "coherence", "stability", "continuity", "integrity", "confidence", "preservation"])]
        vals: list[float] = []
        for k in score_keys:
            v = d.get(k)
            if isinstance(v, bool):
                vals.append(1.0 if v else 0.0)
            elif isinstance(v, (int, float, str)):
                vals.append(_clamp(v, default))
        if vals:
            return _mean(vals, default)
        status_text = json.dumps(d, ensure_ascii=False, default=str).lower()
        positives = sum(term in status_text for term in ["validated", "certified", "established", "ready", "success", "stable", "robust"])
        negatives = sum(term in status_text for term in ["failed", "error", "insufficient", "rupture", "drift", "unstable"])
        return _clamp(default + 0.08 * positives - 0.08 * negatives, default)

    def _compact_payload(self, out: dict[str, Any]) -> dict[str, Any]:
        keep: dict[str, Any] = {}
        for k, v in out.items():
            if k in {"primitive", "timestamp_utc", "status", "classification", "certification"} or any(t in k.lower() for t in ["score", "index", "status", "coherence", "continuity", "stability", "identity", "drift"]):
                if isinstance(v, (str, int, float, bool)) or v is None:
                    keep[k] = v
                elif isinstance(v, (list, tuple)):
                    keep[k] = list(v)[:5]
                elif isinstance(v, dict):
                    keep[k] = {str(a): b for a, b in list(v.items())[:10] if isinstance(b, (str, int, float, bool)) or b is None}
        return keep

    def _extract_timestamps(self, trajectory_memory: dict[str, Any], identity_evidence: list[dict[str, Any]]) -> list[str]:
        stamps: list[str] = []
        for item in _as_list(trajectory_memory.get("trajectory_events")) + _as_list(trajectory_memory.get("trajectory_segments")):
            d = _as_dict(item)
            ts = d.get("timestamp_utc") or d.get("timestamp") or d.get("start") or d.get("end")
            if isinstance(ts, str) and ts:
                stamps.append(ts)
        for e in identity_evidence:
            payload = _as_dict(e.get("payload"))
            ts = payload.get("timestamp_utc") or payload.get("timestamp")
            if isinstance(ts, str) and ts:
                stamps.append(ts)
        return sorted(set(stamps))

    def _build_temporal_profile(self, memory_integration: dict[str, Any], trajectory_memory: dict[str, Any], identity_evidence: list[dict[str, Any]]) -> dict[str, Any]:
        stamps = self._extract_timestamps(trajectory_memory, identity_evidence)
        event_count = int(trajectory_memory.get("event_count") or len(_as_list(trajectory_memory.get("trajectory_events"))) or 0)
        segment_count = int(trajectory_memory.get("segment_count") or len(_as_list(trajectory_memory.get("trajectory_segments"))) or 0)
        source_count = int(memory_integration.get("memory_source_count") or len(_as_list(memory_integration.get("memory_sources"))) or 0)
        span_score = _clamp(min(1.0, len(stamps) / 6.0))
        event_density = _clamp(min(1.0, event_count / 12.0))
        segment_support = _clamp(min(1.0, segment_count / 4.0))
        source_support = _clamp(min(1.0, source_count / 4.0))
        temporal_continuity_score = _mean([span_score, event_density, segment_support, source_support])
        return {"timestamp_count": len(stamps), "event_count": event_count, "segment_count": segment_count, "memory_source_count": source_count, "span_score": span_score, "event_density": event_density, "segment_support": segment_support, "source_support": source_support, "temporal_continuity_score": temporal_continuity_score}

    def _build_inter_memory_profile(self, memory_integration: dict[str, Any], identity_evidence: list[dict[str, Any]]) -> dict[str, Any]:
        metrics = _as_dict(memory_integration.get("integration_metrics"))
        coherence = _clamp(metrics.get("coherence_score", metrics.get("integration_coherence", 0.0)))
        diversity = _clamp(metrics.get("source_diversity", metrics.get("source_availability", 0.0)))
        integration = _clamp(memory_integration.get("memory_integration_score", metrics.get("memory_integration_score", 0.0)))
        conflicts = len(_as_list(memory_integration.get("integration_conflicts")))
        conflict_penalty = _clamp(1.0 - min(1.0, conflicts / 8.0), default=1.0)
        evidence_mean = _mean([_clamp(e.get("score")) for e in identity_evidence])
        inter_memory_coherence_score = _mean([coherence, diversity, integration, conflict_penalty, evidence_mean])
        return {"coherence_score": coherence, "source_diversity": diversity, "integration_score": integration, "conflict_count": conflicts, "conflict_penalty": conflict_penalty, "identity_evidence_mean": evidence_mean, "inter_memory_coherence_score": inter_memory_coherence_score}

    def _build_stability_profile(self, identity_modules: dict[str, Any], identity_evidence: list[dict[str, Any]]) -> dict[str, Any]:
        module_scores = {name: self._score_mapping(out, 0.50) for name, out in identity_modules.items()}
        module_mean = _mean(list(module_scores.values()))
        evidence_mean = _mean([_clamp(e.get("score")) for e in identity_evidence])
        robust_module_count = sum(1 for v in module_scores.values() if v >= 0.65)
        module_coverage = _clamp(min(1.0, len(module_scores) / 6.0))
        robust_fraction = _clamp(robust_module_count / max(1, len(module_scores))) if module_scores else 0.0
        identity_stability_score = _mean([module_mean, evidence_mean, module_coverage, robust_fraction])
        return {"module_count": len(module_scores), "module_scores": module_scores, "module_mean": module_mean, "identity_evidence_mean": evidence_mean, "module_coverage": module_coverage, "robust_module_fraction": robust_fraction, "identity_stability_score": identity_stability_score}

    def _build_rupture_profile(self, memory_integration: dict[str, Any], trajectory_memory: dict[str, Any], identity_modules: dict[str, Any]) -> dict[str, Any]:
        candidates: list[dict[str, Any]] = []
        for source, items in [("AD1.rupture_candidates", _as_list(trajectory_memory.get("rupture_candidates"))), ("AD2.integration_conflicts", _as_list(memory_integration.get("integration_conflicts")))]:
            for i, item in enumerate(items):
                d = _as_dict(item)
                candidates.append({"source": source, "rupture_id": f"{source}_{i:04d}", "severity": self._rupture_severity(d), "payload": d})
        for name, out in identity_modules.items():
            text = json.dumps(out, ensure_ascii=False, default=str).lower()
            if any(term in text for term in ["drift", "rupture", "unstable", "divergence", "incoherence"]):
                candidates.append({"source": f"module.{name}", "rupture_id": f"module_{name}", "severity": self._rupture_severity(out), "payload": self._compact_payload(out)})
        severity_mean = _mean([_clamp(c.get("severity")) for c in candidates])
        candidate_pressure = _clamp(min(1.0, len(candidates) / 10.0))
        rupture_risk = _mean([severity_mean, candidate_pressure])
        return {"potential_identity_ruptures": candidates[:100], "rupture_candidate_count": len(candidates), "mean_rupture_severity": severity_mean, "candidate_pressure": candidate_pressure, "rupture_risk": rupture_risk, "rupture_stability_margin": _clamp(1.0 - rupture_risk, 1.0)}

    def _rupture_severity(self, mapping: Any) -> float:
        d = _as_dict(mapping)
        if not d:
            return 0.3
        vals: list[float] = []
        for k, v in d.items():
            lk = str(k).lower()
            if any(t in lk for t in ["severity", "risk", "drift", "rupture", "conflict", "divergence", "anomaly"]):
                if isinstance(v, bool):
                    vals.append(1.0 if v else 0.0)
                elif isinstance(v, (int, float, str)):
                    vals.append(_clamp(v, 0.5))
        if vals:
            return _mean(vals, 0.3)
        text = json.dumps(d, ensure_ascii=False, default=str).lower()
        return _clamp(0.15 + 0.12 * sum(term in text for term in ["failed", "error", "rupture", "drift", "unstable", "conflict", "insufficient"]), 0.3)

    def _derive_drift_factors(self, memory_integration: dict[str, Any], trajectory_memory: dict[str, Any], identity_modules: dict[str, Any], rupture_profile: dict[str, Any]) -> list[dict[str, Any]]:
        factors: list[dict[str, Any]] = []
        if not memory_integration:
            factors.append({"factor": "missing_memory_integration", "severity": 0.55, "source": "AD2"})
        if not trajectory_memory:
            factors.append({"factor": "missing_trajectory_memory", "severity": 0.55, "source": "AD1"})
        if len(identity_modules) < 2:
            factors.append({"factor": "low_identity_module_coverage", "severity": 0.35, "source": "identity_modules"})
        conflicts = len(_as_list(memory_integration.get("integration_conflicts")))
        if conflicts:
            factors.append({"factor": "integration_conflicts", "severity": _clamp(conflicts / 8.0), "source": "AD2.integration_conflicts", "count": conflicts})
        rupture_count = int(rupture_profile.get("rupture_candidate_count") or 0)
        if rupture_count:
            factors.append({"factor": "identity_rupture_candidates", "severity": _clamp(rupture_count / 10.0), "source": "rupture_profile", "count": rupture_count})
        for name, out in identity_modules.items():
            text = json.dumps(out, ensure_ascii=False, default=str).lower()
            if "drift" in text or "unstable" in text:
                factors.append({"factor": f"{name}_drift_signal", "severity": self._rupture_severity(out), "source": f"module.{name}"})
        return sorted(factors, key=lambda x: x.get("severity", 0.0), reverse=True)[:50]

    def _derive_continuity_threads(self, memory_integration: dict[str, Any], trajectory_memory: dict[str, Any], identity_evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
        threads: list[dict[str, Any]] = []
        for i, item in enumerate(_as_list(trajectory_memory.get("continuity_threads"))):
            d = _as_dict(item)
            threads.append({"thread_id": f"ad1_thread_{i:04d}", "source": "AD1.continuity_threads", "support": self._score_mapping(d, 0.55), "payload": d})
        for i, item in enumerate(_as_list(memory_integration.get("continuity_bindings"))):
            d = _as_dict(item)
            threads.append({"thread_id": f"ad2_binding_{i:04d}", "source": "AD2.continuity_bindings", "support": self._score_mapping(d, 0.55), "payload": d})
        if not threads and identity_evidence:
            for i, e in enumerate(identity_evidence[:20]):
                threads.append({"thread_id": f"evidence_thread_{i:04d}", "source": e.get("source", "identity_evidence"), "support": _clamp(e.get("score", 0.5)), "payload": e.get("payload", {})})
        return threads[:100]

    def _derive_identity_bindings(self, memory_integration: dict[str, Any], trajectory_memory: dict[str, Any], identity_modules: dict[str, Any]) -> list[dict[str, Any]]:
        bindings: list[dict[str, Any]] = []
        for source, items in [("AD2.identity_bindings", _as_list(memory_integration.get("identity_bindings"))), ("AD2.identity_relevant_memory", _as_list(memory_integration.get("identity_relevant_memory"))), ("AD1.identity_relevant_events", _as_list(trajectory_memory.get("identity_relevant_events")))]:
            for i, item in enumerate(items):
                d = _as_dict(item)
                bindings.append({"binding_id": f"{source}_{i:04d}", "source": source, "strength": self._score_mapping(d, 0.55), "payload": d})
        for name, out in identity_modules.items():
            bindings.append({"binding_id": f"module_{name}", "source": f"module.{name}", "strength": self._score_mapping(out, 0.50), "payload": self._compact_payload(out)})
        return bindings[:150]

    def _certify(self, evidence: list[dict[str, Any]], temporal_profile: dict[str, Any], inter_memory_profile: dict[str, Any], stability_profile: dict[str, Any], rupture_profile: dict[str, Any], drift_factors: list[dict[str, Any]]) -> dict[str, Any]:
        temporal = _clamp(temporal_profile.get("temporal_continuity_score"))
        coherence = _clamp(inter_memory_profile.get("inter_memory_coherence_score"))
        stability = _clamp(stability_profile.get("identity_stability_score"))
        rupture_risk = _clamp(rupture_profile.get("rupture_risk"))
        rupture_margin = _clamp(1.0 - rupture_risk, 1.0)
        drift_penalty = _clamp(1.0 - _mean([_clamp(f.get("severity")) for f in drift_factors]), 1.0)
        evidence_support = _clamp(min(1.0, len(evidence) / 12.0))
        score = _clamp((0.22 * temporal) + (0.24 * coherence) + (0.24 * stability) + (0.18 * rupture_margin) + (0.07 * drift_penalty) + (0.05 * evidence_support))
        if score >= 0.72 and rupture_risk <= 0.35:
            cert = "identity_continuity_robust"
        elif score >= 0.55 and rupture_risk <= 0.50:
            cert = "identity_continuity_established"
        elif score >= 0.35 and rupture_risk <= 0.65:
            cert = "identity_continuity_minimal"
        else:
            cert = "identity_continuity_insufficient"
        return {"temporal_continuity_score": temporal, "inter_memory_coherence_score": coherence, "identity_stability_score": stability, "rupture_risk": rupture_risk, "rupture_stability_margin": rupture_margin, "drift_penalty_margin": drift_penalty, "evidence_support": evidence_support, "identity_continuity_score": score, "continuity_certification": cert, "functional_conclusion_only": True, "consciousness_proven": False, "phenomenology_asserted": False}

    def _public_schema(self) -> dict[str, str]:
        return {
            "primitive": "str",
            "symbol": "str",
            "derived_from_symbol": "str",
            "timestamp_utc": "str",
            "identity_continuity_index_status": "str",
            "identity_continuity_established": "bool",
            "identity_continuity_score": "float[0,1]",
            "temporal_continuity_score": "float[0,1]",
            "inter_memory_coherence_score": "float[0,1]",
            "identity_stability_score": "float[0,1]",
            "rupture_risk": "float[0,1]",
            "rupture_resilience_score": "float[0,1]",
            "drift_penalty_margin": "float[0,1]",
            "evidence_support_score": "float[0,1]",
            "temporal_continuity": "dict",
            "inter_memory_coherence": "dict",
            "identity_stability": "dict",
            "rupture_profile": "dict",
            "drift_factors": "list[dict]",
            "continuity_threads": "list[dict]",
            "identity_bindings": "list[dict]",
            "continuity_metrics": "dict",
            "continuity_certification": "str",
            "failure_conditions": "list[str]",
            "functional_conclusion_only": "bool",
            "consciousness_proven": "bool",
            "phenomenology_asserted": "bool",
            "subjectivity_asserted": "bool",
            "qualia_asserted": "bool",
            "paths": "dict[str,str]",
        }

    def _planned_paths(self) -> dict[str, str]:
        return {"json": str(OUTPUT_DIR / "latest_identity_continuity_index.json"), "markdown": str(OUTPUT_DIR / "latest_identity_continuity_index.md"), "prometheus": str(OUTPUT_DIR / "latest_identity_continuity_index.prom")}

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        paths = self._planned_paths()
        Path(paths["json"]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
        Path(paths["markdown"]).write_text(self._to_markdown(result), encoding="utf-8")
        Path(paths["prometheus"]).write_text(self._to_prometheus(result), encoding="utf-8")
        hist = OUTPUT_DIR / "identity_continuity_index_history.jsonl"
        with hist.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp_utc": result["timestamp_utc"], "status": result["identity_continuity_index_status"], "score": result["identity_continuity_score"], "certification": result["continuity_certification"]}, ensure_ascii=False, sort_keys=True) + "\n")
        return paths

    def _to_markdown(self, r: dict[str, Any]) -> str:
        m = r["continuity_metrics"]
        lines = [
            "# AD3 — Identity Continuity Index",
            "",
            f"Status: {r['identity_continuity_index_status']}",
            f"Identity continuity established: {r['identity_continuity_established']}",
            f"Identity continuity score: {r['identity_continuity_score']:.6f}",
            f"Certification: {r['continuity_certification']}",
            "",
            "## Temporal continuity",
            f"- temporal_continuity_score: {r['temporal_continuity_score']:.6f}",
            f"- temporal anchors: {len(r.get('temporal_continuity', {}).get('temporal_anchors', []))}",
            "",
            "## Inter-memory coherence",
            f"- inter_memory_coherence_score: {r['inter_memory_coherence_score']:.6f}",
            f"- coherence links: {len(r.get('inter_memory_coherence', {}).get('coherence_links', []))}",
            "",
            "## Identity stability",
            f"- identity_stability_score: {r['identity_stability_score']:.6f}",
            f"- stable components: {len(r.get('identity_stability', {}).get('stable_components', []))}",
            "",
            "## Rupture profile",
            f"- rupture_risk: {r['rupture_risk']:.6f}",
            f"- rupture_resilience_score: {r['rupture_resilience_score']:.6f}",
            f"- potential ruptures: {len(r['potential_identity_ruptures'])}",
            "",
            "## Drift factors",
            f"- drift_factors: {len(r['drift_factors'])}",
            "",
            "## Continuity metrics",
        ]
        for k, v in m.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                lines.append(f"- {k}: {float(v):.6f}")
            else:
                lines.append(f"- {k}: {v}")
        lines += [
            "",
            "## Evidence structures",
            f"- identity_evidence_count: {r['identity_evidence_count']}",
            f"- continuity_threads: {len(r['continuity_threads'])}",
            f"- identity_bindings: {len(r['identity_bindings'])}",
            "",
            "## Epistemic guard",
            "Functional conclusion only. No consciousness, subjectivity, qualia, or phenomenology is asserted.",
        ]
        return "\n".join(lines) + "\n"

    def _to_prometheus(self, r: dict[str, Any]) -> str:
        metrics = {
            "oce_identity_continuity_established": 1 if r["identity_continuity_established"] else 0,
            "oce_identity_continuity_score": r["identity_continuity_score"],
            "oce_identity_temporal_continuity_score": r["temporal_continuity_score"],
            "oce_identity_inter_memory_coherence_score": r["inter_memory_coherence_score"],
            "oce_identity_stability_score": r["identity_stability_score"],
            "oce_identity_rupture_risk": r["rupture_risk"],
            "oce_identity_rupture_resilience_score": r["rupture_resilience_score"],
            "oce_identity_drift_penalty_margin": r["drift_penalty_margin"],
            "oce_identity_evidence_support_score": r["evidence_support_score"],
            "oce_identity_evidence_count": r["identity_evidence_count"],
            "oce_identity_rupture_candidate_count": len(r["potential_identity_ruptures"]),
            "oce_identity_drift_factor_count": len(r["drift_factors"]),
        }
        # Backward-compatible aliases from v1.
        metrics["identity_continuity_established"] = metrics["oce_identity_continuity_established"]
        metrics["identity_continuity_score"] = metrics["oce_identity_continuity_score"]
        lines = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                lines.append(f"{name} {float(value):.6f}")
            else:
                lines.append(f"{name} {value}")
        return "\n".join(lines) + "\n"
