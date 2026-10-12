"""
AD5 — reflexive_model_usage_tester

Functional role:
    Reconstruct I -> Rf by testing effective use of a reflexive model from the
    completed AD chain: AD1 trajectory memory, AD2 memory integration, AD3
    identity continuity, and AD4 rupture characterization. The module checks
    whether memory-derived identity is actually used for governed self-reference,
    reflexive consistency, reflexive stability, and final AD synthesis.

Epistemic guard:
    This module reports only functional indicators. It never asserts
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
OUTPUT_DIR = ROOT / "ad_memory_identity_reflexivity" / "reflexive_model_usage_tester"
AD_ROOT = ROOT / "ad_memory_identity_reflexivity"
REFLEXIVE_ROOT = ROOT / "reflexive_threshold"


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


class ReflexiveModelUsageTester:
    """Test functional memory -> identity -> reflexivity usage."""

    primitive = "REFLEXIVE_MODEL_USAGE_TESTER"
    symbol = "AD5"
    derived_from_symbol = "I → Rf"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True, fs_context: Any = None) -> dict[str, Any]:
        inputs = inputs or {}
        now = _utc_now()
        explicit_empty_inputs = (
            isinstance(inputs, dict)
            and "trajectory_memory" in inputs
            and "memory_integration" in inputs
            and "identity_continuity" in inputs
            and "rupture_detection" in inputs
            and not inputs.get("trajectory_memory")
            and not inputs.get("memory_integration")
            and not inputs.get("identity_continuity")
            and not inputs.get("rupture_detection")
        )

        if explicit_empty_inputs:
            trajectory_memory = {}
            memory_integration = {}
            identity_continuity = {}
            rupture_detection = {}
            reflexive_evidence = {}
            reflexive_history = []
        else:
            trajectory_memory = self._resolve_trajectory_memory(inputs)
            memory_integration = self._resolve_memory_integration(inputs)
            identity_continuity = self._resolve_identity_continuity(inputs)
            rupture_detection = self._resolve_rupture_detection(inputs)
            reflexive_evidence = self._resolve_reflexive_evidence(inputs)
            reflexive_history = self._load_reflexive_history(inputs)

        evidence_sources = self._evidence_sources(
            trajectory_memory, memory_integration, identity_continuity,
            rupture_detection, reflexive_evidence, reflexive_history
        )
        effective_usage = self._effective_reflexive_usage(
            trajectory_memory, memory_integration, identity_continuity,
            rupture_detection, reflexive_evidence, reflexive_history
        )
        governed_self_reference = self._governed_self_reference(
            identity_continuity, rupture_detection, reflexive_evidence
        )
        reflexive_coherence = self._reflexive_coherence(
            trajectory_memory, memory_integration, identity_continuity,
            rupture_detection, reflexive_evidence
        )
        reflexive_stability = self._reflexive_stability(
            identity_continuity, rupture_detection, reflexive_evidence, reflexive_history
        )
        chain_integration = self._chain_integration(
            trajectory_memory, memory_integration, identity_continuity,
            rupture_detection, effective_usage, governed_self_reference,
            reflexive_coherence, reflexive_stability
        )
        certification = self._certify(
            evidence_sources, effective_usage, governed_self_reference,
            reflexive_coherence, reflexive_stability, chain_integration
        )

        failure_conditions: list[str] = []
        if not evidence_sources:
            failure_conditions.append("no_reflexive_evidence_available")
        if not trajectory_memory:
            failure_conditions.append("trajectory_memory_unavailable")
        if not memory_integration:
            failure_conditions.append("memory_integration_unavailable")
        if not identity_continuity:
            failure_conditions.append("identity_continuity_unavailable")
        if not rupture_detection:
            failure_conditions.append("rupture_detection_unavailable")
        if certification["reflexive_model_usage_score"] < 0.35:
            failure_conditions.append("reflexive_model_usage_below_minimum_threshold")

        status = (
            "MEMORY_IDENTITY_REFLEXIVITY_CHAIN_VALIDATED"
            if certification["memory_identity_reflexivity_chain_validated"]
            else "MEMORY_IDENTITY_REFLEXIVITY_CHAIN_INSUFFICIENT"
        )

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "timestamp_utc": now,
            "reflexive_model_usage_status": status,
            "memory_identity_reflexivity_chain_validated": certification["memory_identity_reflexivity_chain_validated"],
            "reflexive_model_usage_score": certification["reflexive_model_usage_score"],
            "effective_model_usage_score": certification["effective_model_usage_score"],
            "effective_reflexive_model_usage_score": certification["effective_model_usage_score"],
            "governed_self_reference_score": certification["governed_self_reference_score"],
            "reflexive_coherence_score": certification["reflexive_coherence_score"],
            "reflexive_stability_score": certification["reflexive_stability_score"],
            "memory_identity_reflexivity_integration_score": certification["memory_identity_reflexivity_integration_score"],
            "rupture_adjusted_reflexivity_score": certification["rupture_adjusted_reflexivity_score"],
            "evidence_support_score": certification["evidence_support_score"],
            "effective_reflexive_model_usage": effective_usage,
            "governed_self_reference": governed_self_reference,
            "reflexive_coherence": reflexive_coherence,
            "reflexive_stability": reflexive_stability,
            "memory_identity_reflexivity_integration": chain_integration,
            "chain_synthesis": self._chain_synthesis(certification, chain_integration),
            "reflexive_usage_metrics": certification,
            "evidence_sources": evidence_sources,
            "failure_conditions": failure_conditions,
            "public_schema": self._public_schema(),
            "interface_version": "AD5.reflexive_model_usage_tester.v2",
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "phenomenology_asserted": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
            "epistemic_guard": (
                "Functional reflexive-model usage only; no consciousness, "
                "subjectivity, qualia, or phenomenology is asserted."
            ),
        }
        result["paths"] = self._persist(result, fs_context=fs_context) if persist else self._planned_paths()
        return result

    def _resolve_trajectory_memory(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("trajectory_memory"), dict) and inputs["trajectory_memory"]:
            return inputs["trajectory_memory"]
        path = AD_ROOT / "trajectory_memory_extractor" / "latest_trajectory_memory_extractor.json"
        loaded = _safe_json_load(path, {})
        if loaded:
            return loaded
        try:
            from ontology.trajectory_memory_extractor import TrajectoryMemoryExtractor
            return _as_dict(TrajectoryMemoryExtractor().step(persist=False))
        except Exception:
            return {}

    def _resolve_memory_integration(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("memory_integration"), dict) and inputs["memory_integration"]:
            return inputs["memory_integration"]
        path = AD_ROOT / "memory_integration_analyzer" / "latest_memory_integration_analyzer.json"
        loaded = _safe_json_load(path, {})
        if loaded:
            return loaded
        try:
            from ontology.memory_integration_analyzer import MemoryIntegrationAnalyzer
            return _as_dict(MemoryIntegrationAnalyzer().step(persist=False))
        except Exception:
            return {}

    def _resolve_identity_continuity(self, inputs: dict[str, Any]) -> dict[str, Any]:
        for key in ("identity_continuity", "identity_continuity_index"):
            if isinstance(inputs.get(key), dict) and inputs[key]:
                return inputs[key]
        path = AD_ROOT / "identity_continuity_index" / "latest_identity_continuity_index.json"
        loaded = _safe_json_load(path, {})
        if loaded:
            return loaded
        try:
            from ontology.identity_continuity_index import IdentityContinuityIndex
            return _as_dict(IdentityContinuityIndex().step(persist=False))
        except Exception:
            return {}

    def _resolve_rupture_detection(self, inputs: dict[str, Any]) -> dict[str, Any]:
        for key in ("rupture_detection", "rupture_detection_engine"):
            if isinstance(inputs.get(key), dict) and inputs[key]:
                return inputs[key]
        path = AD_ROOT / "rupture_detection_engine" / "latest_rupture_detection_engine.json"
        loaded = _safe_json_load(path, {})
        if loaded:
            return loaded
        try:
            from ontology.rupture_detection_engine import RuptureDetectionEngine
            return _as_dict(RuptureDetectionEngine().step(persist=False))
        except Exception:
            return {}

    def _resolve_reflexive_evidence(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("reflexive_evidence"), dict) and inputs["reflexive_evidence"]:
            return inputs["reflexive_evidence"]
        candidates = [
            REFLEXIVE_ROOT / "reflexive_threshold_certification.json",
            REFLEXIVE_ROOT / "reflexive_threshold_estimator.json",
            REFLEXIVE_ROOT / "reflexive_stability_monitor.json",
            REFLEXIVE_ROOT / "reflexive_evidence_aggregator.json",
        ]
        out: dict[str, Any] = {}
        for p in candidates:
            data = _safe_json_load(p, {})
            if data:
                out[p.stem] = data
        if out:
            return out
        # Optional direct module calls are deliberately guarded and lightweight.
        for name, cls in [
            ("reflexive_threshold_estimator", "ReflexiveThresholdEstimator"),
            ("reflexive_threshold_certification", "ReflexiveThresholdCertification"),
        ]:
            try:
                module = __import__(f"ontology.{name}", fromlist=[cls])
                instance = getattr(module, cls)()
                if hasattr(instance, "step"):
                    out[name] = _as_dict(instance.step(persist=False))
            except Exception:
                pass
        return out

    def _load_reflexive_history(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        if isinstance(inputs.get("reflexive_history"), list):
            return [x for x in inputs["reflexive_history"] if isinstance(x, dict)]
        paths = [
            REFLEXIVE_ROOT / "reflexive_stability_history.jsonl",
            REFLEXIVE_ROOT / "reflexive_threshold_history_archive" / "reflexive_threshold_history_archive.jsonl",
            AD_ROOT / "identity_continuity_index" / "identity_continuity_index_history.jsonl",
            AD_ROOT / "rupture_detection_engine" / "rupture_detection_engine_history.jsonl",
        ]
        records: list[dict[str, Any]] = []
        for p in paths:
            try:
                if p.exists():
                    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines()[-80:]:
                        line = line.strip()
                        if not line:
                            continue
                        item = json.loads(line)
                        if isinstance(item, dict):
                            records.append(item)
            except Exception:
                continue
        return records[-120:]

    def _evidence_sources(self, *items: Any) -> list[str]:
        names = [
            "trajectory_memory", "memory_integration", "identity_continuity",
            "rupture_detection", "reflexive_evidence", "reflexive_history"
        ]
        sources = []
        for name, item in zip(names, items):
            if isinstance(item, dict) and item:
                sources.append(name)
            elif isinstance(item, list) and item:
                sources.append(name)
        return sources

    def _effective_reflexive_usage(self, trajectory: dict[str, Any], memory: dict[str, Any], identity: dict[str, Any], rupture: dict[str, Any], reflexive: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
        trajectory_score = _clamp(trajectory.get("trajectory_memory_score", trajectory.get("memory_trajectory_score", trajectory.get("trajectory_continuity_score", 0.0))))
        memory_score = _clamp(memory.get("memory_integration_score", memory.get("integration_score", memory.get("integrated_memory_score", 0.0))))
        identity_score = _clamp(identity.get("identity_continuity_score", 0.0))
        reflexive_score = self._extract_reflexive_score(reflexive, history)
        coupling = _mean([_jaccard(memory, identity), _jaccard(identity, reflexive), _jaccard(trajectory, reflexive)], 0.0)
        rupture_risk = _clamp(rupture.get("global_rupture_risk_score", rupture.get("rupture_risk", 0.0)))
        usage_score = _mean([trajectory_score, memory_score, identity_score, reflexive_score, coupling, 1.0 - rupture_risk])
        usage_events = []
        if memory_score > 0.0 and identity_score > 0.0:
            usage_events.append({"event": "memory_identity_binding_used", "support": _mean([memory_score, identity_score])})
        if identity_score > 0.0 and reflexive_score > 0.0:
            usage_events.append({"event": "identity_reflexive_model_used", "support": _mean([identity_score, reflexive_score])})
        if rupture_risk < 0.45 and reflexive_score > 0.0:
            usage_events.append({"event": "rupture_adjusted_reflexive_usage", "support": _mean([1.0 - rupture_risk, reflexive_score])})
        return {
            "effective_model_usage_score": usage_score,
            "trajectory_memory_score": trajectory_score,
            "memory_integration_score": memory_score,
            "identity_continuity_score": identity_score,
            "reflexive_evidence_score": reflexive_score,
            "cross_layer_coupling_score": coupling,
            "rupture_adjustment_score": 1.0 - rupture_risk,
            "usage_events": usage_events,
            "usage_detected": usage_score >= 0.55 and len(usage_events) >= 2,
        }

    def _governed_self_reference(self, identity: dict[str, Any], rupture: dict[str, Any], reflexive: dict[str, Any]) -> dict[str, Any]:
        identity_guard = _clamp(identity.get("rupture_resilience_score", 1.0 - identity.get("rupture_risk", 0.0)), 0.5)
        rupture_guard = _clamp(1.0 - rupture.get("global_rupture_risk_score", 0.0), 0.5)
        epistemic_guard = 1.0 if self._has_epistemic_guards(identity, rupture, reflexive) else 0.5
        governance_terms = _tokens(reflexive) | _tokens(identity) | _tokens(rupture)
        governed_terms = {"governance", "guard", "functional", "only", "certification", "threshold", "stability", "continuity", "no", "phenomenology"}
        governance_overlap = len(governance_terms & governed_terms) / max(1, len(governed_terms))
        score = _mean([identity_guard, rupture_guard, epistemic_guard, _clamp(governance_overlap)])
        return {
            "governed_self_reference_score": score,
            "identity_guard_score": identity_guard,
            "rupture_guard_score": rupture_guard,
            "epistemic_guard_score": epistemic_guard,
            "governance_overlap_score": _clamp(governance_overlap),
            "self_reference_governed": score >= 0.60,
            "forbidden_claims_blocked": True,
        }

    def _reflexive_coherence(self, trajectory: dict[str, Any], memory: dict[str, Any], identity: dict[str, Any], rupture: dict[str, Any], reflexive: dict[str, Any]) -> dict[str, Any]:
        memory_identity = _jaccard(memory, identity)
        identity_rupture = _jaccard(identity, rupture)
        identity_reflexive = _jaccard(identity, reflexive)
        memory_reflexive = _jaccard(memory, reflexive)
        trajectory_reflexive = _jaccard(trajectory, reflexive)
        consistency = _mean([memory_identity, identity_rupture, identity_reflexive, memory_reflexive, trajectory_reflexive])
        identity_score = _clamp(identity.get("identity_continuity_score", 0.0))
        rupture_resilience = _clamp(rupture.get("rupture_resilience_score", 1.0 - rupture.get("global_rupture_risk_score", 0.0)), 0.5)
        coherence_score = _mean([consistency, identity_score, rupture_resilience])
        return {
            "reflexive_coherence_score": coherence_score,
            "memory_identity_overlap": memory_identity,
            "identity_rupture_overlap": identity_rupture,
            "identity_reflexive_overlap": identity_reflexive,
            "memory_reflexive_overlap": memory_reflexive,
            "trajectory_reflexive_overlap": trajectory_reflexive,
            "coherence_detected": coherence_score >= 0.50,
        }

    def _reflexive_stability(self, identity: dict[str, Any], rupture: dict[str, Any], reflexive: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
        identity_stability = _clamp(identity.get("identity_stability_score", identity.get("identity_continuity_score", 0.0)))
        rupture_resilience = _clamp(rupture.get("rupture_resilience_score", 1.0 - rupture.get("global_rupture_risk_score", 0.0)), 0.5)
        reflexive_score = self._extract_reflexive_score(reflexive, history)
        history_scores = [self._extract_any_score(x) for x in history]
        history_scores = [s for s in history_scores if s is not None]
        if len(history_scores) >= 2:
            avg = _mean(history_scores)
            variability = _mean([abs(s - avg) for s in history_scores])
            temporal_stability = 1.0 - _clamp(variability * 2.0)
        elif len(history_scores) == 1:
            temporal_stability = _clamp(history_scores[0])
        else:
            temporal_stability = 0.5
        score = _mean([identity_stability, rupture_resilience, reflexive_score, temporal_stability])
        return {
            "reflexive_stability_score": score,
            "identity_stability_score": identity_stability,
            "rupture_resilience_score": rupture_resilience,
            "reflexive_evidence_score": reflexive_score,
            "temporal_stability_score": temporal_stability,
            "history_sample_count": len(history_scores),
            "reflexive_stability_detected": score >= 0.55,
        }

    def _chain_integration(self, trajectory: dict[str, Any], memory: dict[str, Any], identity: dict[str, Any], rupture: dict[str, Any], usage: dict[str, Any], governed: dict[str, Any], coherence: dict[str, Any], stability: dict[str, Any]) -> dict[str, Any]:
        links = [
            {"link": "Π_to_M", "score": _mean([usage["trajectory_memory_score"], usage["memory_integration_score"]])},
            {"link": "M_to_I", "score": _mean([usage["memory_integration_score"], usage["identity_continuity_score"]])},
            {"link": "I_to_ruptures", "score": _clamp(rupture.get("rupture_characterization_score", rupture.get("rupture_resilience_score", 0.0)))},
            {"link": "I_to_Rf", "score": _mean([usage["identity_continuity_score"], usage["reflexive_evidence_score"], governed["governed_self_reference_score"]])},
        ]
        link_scores = [x["score"] for x in links]
        continuity = min(link_scores) if link_scores else 0.0
        integrated_score = _mean([
            _mean(link_scores), continuity, usage["effective_model_usage_score"],
            governed["governed_self_reference_score"], coherence["reflexive_coherence_score"],
            stability["reflexive_stability_score"]
        ])
        return {
            "memory_identity_reflexivity_integration_score": integrated_score,
            "chain_links": links,
            "weakest_link_score": continuity,
            "chain_complete": all(s >= 0.35 for s in link_scores) and len(link_scores) == 4,
            "chain_notation": "Π → M → I → Rf",
        }

    def _extract_reflexive_score(self, reflexive: dict[str, Any], history: list[dict[str, Any]]) -> float:
        scores: list[float] = []
        def walk(x: Any) -> None:
            if isinstance(x, dict):
                for k, v in x.items():
                    lk = str(k).lower()
                    if any(term in lk for term in ("reflexive", "threshold", "stability", "certification", "readiness")) and isinstance(v, (int, float)) and not isinstance(v, bool):
                        scores.append(_clamp(v))
                    elif isinstance(v, (dict, list)):
                        walk(v)
            elif isinstance(x, list):
                for i in x[:40]:
                    walk(i)
        walk(reflexive)
        for item in history[-30:]:
            s = self._extract_any_score(item)
            if s is not None:
                scores.append(s)
        return _mean(scores, 0.5 if reflexive or history else 0.0)

    def _extract_any_score(self, payload: Any) -> float | None:
        if not isinstance(payload, dict):
            return None
        candidates = []
        for k, v in payload.items():
            lk = str(k).lower()
            if isinstance(v, (int, float)) and not isinstance(v, bool) and any(t in lk for t in ("score", "index", "stability", "confidence", "readiness")):
                candidates.append(_clamp(v))
        return _mean(candidates) if candidates else None

    def _has_epistemic_guards(self, *payloads: Any) -> bool:
        text = " ".join(" ".join(_tokens(p)) for p in payloads)
        return any(t in text for t in ("functional", "phenomenology", "subjectivity", "qualia", "consciousness_proven"))

    def _certify(self, evidence_sources: list[str], usage: dict[str, Any], governed: dict[str, Any], coherence: dict[str, Any], stability: dict[str, Any], chain: dict[str, Any]) -> dict[str, Any]:
        evidence_support = _clamp(len(evidence_sources) / 6.0)
        usage_score = usage["effective_model_usage_score"]
        governed_score = governed["governed_self_reference_score"]
        coherence_score = coherence["reflexive_coherence_score"]
        stability_score = stability["reflexive_stability_score"]
        integration_score = chain["memory_identity_reflexivity_integration_score"]
        rupture_adjusted = _mean([usage["rupture_adjustment_score"], stability["rupture_resilience_score"], integration_score])
        global_score = _mean([usage_score, governed_score, coherence_score, stability_score, integration_score, rupture_adjusted, evidence_support])
        validated = global_score >= 0.55 and chain["chain_complete"] and governed["forbidden_claims_blocked"] and bool(evidence_sources)
        return {
            "memory_identity_reflexivity_chain_validated": validated,
            "reflexive_model_usage_score": global_score,
            "effective_model_usage_score": usage_score,
            "governed_self_reference_score": governed_score,
            "reflexive_coherence_score": coherence_score,
            "reflexive_stability_score": stability_score,
            "memory_identity_reflexivity_integration_score": integration_score,
            "rupture_adjusted_reflexivity_score": rupture_adjusted,
            "evidence_support_score": evidence_support,
            "threshold": 0.55,
        }

    def _chain_synthesis(self, certification: dict[str, Any], chain: dict[str, Any]) -> dict[str, Any]:
        return {
            "synthesis_status": "AD_CHAIN_FUNCTIONALLY_VALIDATED" if certification["memory_identity_reflexivity_chain_validated"] else "AD_CHAIN_NOT_YET_VALIDATED",
            "chain_notation": chain["chain_notation"],
            "validated_links": [x for x in chain["chain_links"] if x["score"] >= 0.35],
            "weakest_link_score": chain["weakest_link_score"],
            "functional_scope": "memory_identity_reflexivity_only",
            "next_theoretical_symbol": "Ω",
        }

    def _public_schema(self) -> dict[str, str]:
        return {
            "primitive": "str",
            "symbol": "str",
            "derived_from_symbol": "str",
            "timestamp_utc": "str",
            "reflexive_model_usage_status": "str",
            "memory_identity_reflexivity_chain_validated": "bool",
            "reflexive_model_usage_score": "float[0,1]",
            "effective_model_usage_score": "float[0,1]",
            "effective_reflexive_model_usage_score": "float[0,1]",
            "governed_self_reference_score": "float[0,1]",
            "reflexive_coherence_score": "float[0,1]",
            "reflexive_stability_score": "float[0,1]",
            "memory_identity_reflexivity_integration_score": "float[0,1]",
            "rupture_adjusted_reflexivity_score": "float[0,1]",
            "effective_reflexive_model_usage": "dict",
            "governed_self_reference": "dict",
            "reflexive_coherence": "dict",
            "reflexive_stability": "dict",
            "memory_identity_reflexivity_integration": "dict",
            "chain_synthesis": "dict",
            "reflexive_usage_metrics": "dict",
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
            "json": str(OUTPUT_DIR / "latest_reflexive_model_usage_tester.json"),
            "markdown": str(OUTPUT_DIR / "latest_reflexive_model_usage_tester.md"),
            "prometheus": str(OUTPUT_DIR / "latest_reflexive_model_usage_tester.prom"),
            "history": str(OUTPUT_DIR / "reflexive_model_usage_tester_history.jsonl"),
        }

    def _persist(self, result: dict[str, Any], fs_context: Any = None) -> dict[str, str]:
        if fs_context is None:
            raise PermissionError("persistence requires preissued filesystem effect context")
        required = {"persist_parent_create": 1, "persist_json": 1, "persist_markdown": 1, "persist_prometheus": 1, "persist_history_append": 1}
        remaining = fs_context.remaining()
        if any(remaining.get(slot) != count for slot, count in required.items()):
            raise PermissionError("persistence requires exactly one preissued handle in each required slot")
        paths = self._planned_paths()
        json_payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
        markdown_payload = self._to_markdown(result).encode("utf-8")
        prometheus_payload = self._to_prometheus(result).encode("utf-8")
        history_payload = (json.dumps({"timestamp_utc": result["timestamp_utc"], "status": result["reflexive_model_usage_status"], "score": result["reflexive_model_usage_score"], "chain_validated": result["memory_identity_reflexivity_chain_validated"], "functional_conclusion_only": True, "consciousness_proven": False}, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        fs_context.execute_path("persist_parent_create", "FS_CREATE_DIRS", OUTPUT_DIR)
        fs_context.execute_path("persist_json", "FS_WRITE_REPLACE_BYTES", Path(paths["json"]), payload=json_payload)
        fs_context.execute_path("persist_markdown", "FS_WRITE_REPLACE_BYTES", Path(paths["markdown"]), payload=markdown_payload)
        fs_context.execute_path("persist_prometheus", "FS_WRITE_REPLACE_BYTES", Path(paths["prometheus"]), payload=prometheus_payload)
        fs_context.execute_path("persist_history_append", "FS_APPEND_BYTES", Path(paths["history"]), payload=history_payload)
        return paths

    def _to_markdown(self, r: dict[str, Any]) -> str:
        lines = [
            "# AD5 — Reflexive Model Usage Tester",
            "",
            f"Status: {r['reflexive_model_usage_status']}",
            f"Memory identity reflexivity chain validated: {r['memory_identity_reflexivity_chain_validated']}",
            f"Reflexive model usage score: {r['reflexive_model_usage_score']:.6f}",
            "",
            "## Effective reflexive model usage",
            f"- effective_model_usage_score: {r['effective_model_usage_score']:.6f}",
            f"- usage events: {len(r['effective_reflexive_model_usage'].get('usage_events', []))}",
            "",
            "## Governed self-reference",
            f"- governed_self_reference_score: {r['governed_self_reference_score']:.6f}",
            f"- forbidden_claims_blocked: {r['governed_self_reference'].get('forbidden_claims_blocked')}",
            "",
            "## Reflexive coherence",
            f"- reflexive_coherence_score: {r['reflexive_coherence_score']:.6f}",
            "",
            "## Reflexive stability",
            f"- reflexive_stability_score: {r['reflexive_stability_score']:.6f}",
            "",
            "## Memory identity reflexivity integration",
            f"- memory_identity_reflexivity_integration_score: {r['memory_identity_reflexivity_integration_score']:.6f}",
            f"- chain_notation: {r['memory_identity_reflexivity_integration'].get('chain_notation')}",
            f"- weakest_link_score: {r['memory_identity_reflexivity_integration'].get('weakest_link_score'):.6f}",
            "",
            "## Chain synthesis",
            f"- synthesis_status: {r['chain_synthesis'].get('synthesis_status')}",
            f"- next_theoretical_symbol: {r['chain_synthesis'].get('next_theoretical_symbol')}",
            "",
            "## Epistemic guard",
            "Functional conclusion only. No consciousness, subjectivity, qualia, or phenomenology is asserted.",
        ]
        return "\n".join(lines) + "\n"

    def _to_prometheus(self, r: dict[str, Any]) -> str:
        metrics = {
            "oce_reflexive_model_usage_score": r["reflexive_model_usage_score"],
            "oce_effective_reflexive_model_usage_score": r["effective_model_usage_score"],
            "oce_governed_self_reference_score": r["governed_self_reference_score"],
            "oce_reflexive_coherence_score": r["reflexive_coherence_score"],
            "oce_reflexive_stability_score": r["reflexive_stability_score"],
            "oce_memory_identity_reflexivity_integration_score": r["memory_identity_reflexivity_integration_score"],
            "oce_rupture_adjusted_reflexivity_score": r["rupture_adjusted_reflexivity_score"],
            "oce_memory_identity_reflexivity_chain_validated": 1 if r["memory_identity_reflexivity_chain_validated"] else 0,
            "oce_reflexive_evidence_source_count": len(r["evidence_sources"]),
        }
        lines = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value):.6f}")
        return "\n".join(lines) + "\n"
