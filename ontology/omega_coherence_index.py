"""
AE3 — omega_coherence_index

Functional role:
    Integrate AE1 self-description registry and AE2 dynamic compatibility
    matrix into an Omega coherence index. Omega is treated here as a measurable
    functional self-referential coherence regime, not as phenomenal
    consciousness.

Outputs:
    - Omega coherence index and readiness score;
    - self-description coherence;
    - compatibility coherence;
    - contradiction resilience;
    - causal/stability readiness placeholders for AE4-AE6;
    - explicit epistemic guard.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ae_omega_coherence" / "omega_coherence_index"
AE1_DIR = ROOT / "ae_omega_coherence" / "self_description_registry"
AE2_DIR = ROOT / "ae_omega_coherence" / "dynamic_compatibility_matrix"
AD5_DIR = ROOT / "ad_memory_identity_reflexivity" / "reflexive_model_usage_tester"

FORBIDDEN_FLAGS = [
    "consciousness_proven",
    "phenomenology_asserted",
    "subjectivity_asserted",
    "qualia_asserted",
]


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


def _mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values]
    return sum(vals) / len(vals) if vals else default


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


def _safe_json_load(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _epistemic_guard_ok(*payloads: dict[str, Any]) -> bool:
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for flag in FORBIDDEN_FLAGS:
            if bool(payload.get(flag)) is True:
                return False
    return True


class OmegaCoherenceIndex:
    """Compute a functional Omega coherence index from AE1 and AE2 evidence."""

    primitive = "OMEGA_COHERENCE_INDEX"
    symbol = "AE3"
    derived_from_symbol = "Rf → Ω"

    def step(self, inputs: Optional[dict[str, Any]] = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        now = _utc_now()

        explicit_empty_inputs = (
            "self_description_registry" in inputs
            and "dynamic_compatibility_matrix" in inputs
            and not inputs.get("self_description_registry")
            and not inputs.get("dynamic_compatibility_matrix")
        )

        if explicit_empty_inputs:
            registry: dict[str, Any] = {}
            compatibility: dict[str, Any] = {}
            reflexive: dict[str, Any] = {}
        else:
            registry = self._resolve_registry(inputs)
            compatibility = self._resolve_compatibility(inputs)
            reflexive = self._resolve_reflexive(inputs)

        components = self._components(registry, compatibility, reflexive)
        coherence_profile = self._coherence_profile(registry, compatibility, reflexive, components)
        failure_conditions = self._failure_conditions(registry, compatibility, components, coherence_profile)
        status = "OMEGA_COHERENCE_INDEX_ESTABLISHED" if components["omega_coherence_index_established"] else "OMEGA_COHERENCE_INDEX_INSUFFICIENT"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "timestamp_utc": now,
            "omega_coherence_index_status": status,
            "omega_coherence_index_established": components["omega_coherence_index_established"],
            "omega_coherence_index": components["omega_coherence_index"],
            "omega_coherence_score": components["omega_coherence_index"],
            "self_description_coherence_score": components["self_description_coherence_score"],
            "dynamic_compatibility_coherence_score": components["dynamic_compatibility_coherence_score"],
            "cross_level_integration_score": components["cross_level_integration_score"],
            "contradiction_resilience_score": components["contradiction_resilience_score"],
            "epistemic_guard_score": components["epistemic_guard_score"],
            "omega_readiness_score": components["omega_readiness_score"],
            "causal_activity_readiness_score": components["causal_activity_readiness_score"],
            "omega_stability_readiness_score": components["omega_stability_readiness_score"],
            "self_description_registry": self._summary_registry(registry),
            "dynamic_compatibility_matrix": self._summary_compatibility(compatibility),
            "reflexive_grounding": self._summary_reflexive(reflexive),
            "omega_coherence_profile": coherence_profile,
            "omega_components": components,
            "failure_conditions": failure_conditions,
            "ae_chain_position": {
                "axis": "AE",
                "step": "AE3",
                "input": "AE1 self_description_registry + AE2 dynamic_compatibility_matrix",
                "output": "AE4 omega_causal_activity_tester",
                "theoretical_mapping": "Rf -> Omega as functional self-referential dynamic coherence",
            },
            "public_schema": [
                "omega_coherence_index_status",
                "omega_coherence_index",
                "omega_coherence_score",
                "self_description_coherence_score",
                "dynamic_compatibility_coherence_score",
                "cross_level_integration_score",
                "contradiction_resilience_score",
                "epistemic_guard_score",
                "omega_readiness_score",
                "omega_coherence_profile",
                "omega_components",
            ],
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "phenomenology_asserted": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
            "epistemic_note": "Functional Omega coherence only; no phenomenal or subjective conclusion is asserted.",
        }

        if persist:
            self._persist(result)
        return result

    def _resolve_registry(self, inputs: dict[str, Any]) -> dict[str, Any]:
        candidate = _as_dict(inputs.get("self_description_registry"))
        if candidate:
            return candidate
        return _as_dict(_safe_json_load(AE1_DIR / "latest_self_description_registry.json", {}))

    def _resolve_compatibility(self, inputs: dict[str, Any]) -> dict[str, Any]:
        candidate = _as_dict(inputs.get("dynamic_compatibility_matrix"))
        if candidate:
            return candidate
        # support short alias used in tests or future callers
        candidate = _as_dict(inputs.get("compatibility_matrix"))
        if candidate:
            return candidate
        return _as_dict(_safe_json_load(AE2_DIR / "latest_dynamic_compatibility_matrix.json", {}))

    def _resolve_reflexive(self, inputs: dict[str, Any]) -> dict[str, Any]:
        candidate = _as_dict(inputs.get("reflexive_model_usage"))
        if candidate:
            return candidate
        return _as_dict(_safe_json_load(AD5_DIR / "latest_reflexive_model_usage_tester.json", {}))

    def _components(self, registry: dict[str, Any], compatibility: dict[str, Any], reflexive: dict[str, Any]) -> dict[str, Any]:
        reg_score = _clamp(registry.get("self_description_registry_score"), 0.0)
        reg_ready = _clamp(registry.get("omega_readiness_score"), reg_score)
        reg_consistency = _clamp(registry.get("registry_consistency_score"), reg_score)
        reg_governance = _clamp(registry.get("self_reference_governance_score"), reg_score)
        entry_count = len(_as_list(registry.get("registered_self_descriptions")))
        entry_support = _clamp(min(1.0, entry_count / 2.0), 0.0)
        self_description_coherence = _mean([reg_score, reg_ready, reg_consistency, reg_governance, entry_support])

        dyn_score = _clamp(compatibility.get("dynamic_compatibility_score"), 0.0)
        compat_ready = _clamp(compatibility.get("omega_compatibility_readiness_score"), dyn_score)
        axis_score = _clamp(compatibility.get("axis_compatibility_score"), dyn_score)
        cross_score = _clamp(compatibility.get("cross_description_compatibility_score"), dyn_score)
        contradiction_resilience = _clamp(compatibility.get("contradiction_resilience_score"), 1.0 if compatibility else 0.0)
        dynamic_compatibility_coherence = _mean([dyn_score, compat_ready, axis_score, cross_score, contradiction_resilience])

        reflexive_score = _clamp(reflexive.get("reflexive_model_usage_score"), 0.0)
        integration_score = _clamp(reflexive.get("memory_identity_reflexivity_integration_score"), reflexive_score)
        reflexive_grounding = _mean([reflexive_score, integration_score], default=0.0)

        cross_level_integration = _mean([
            self_description_coherence,
            dynamic_compatibility_coherence,
            reflexive_grounding,
            min(reg_ready, compat_ready) if (registry and compatibility) else 0.0,
        ])
        epistemic_guard = 1.0 if _epistemic_guard_ok(registry, compatibility, reflexive) else 0.0
        omega_readiness = _mean([reg_ready, compat_ready, cross_level_integration, epistemic_guard])
        causal_activity_readiness = _mean([dynamic_compatibility_coherence, cross_level_integration, contradiction_resilience])
        stability_readiness = _mean([self_description_coherence, dynamic_compatibility_coherence, contradiction_resilience])

        omega_index = _mean([
            self_description_coherence,
            dynamic_compatibility_coherence,
            cross_level_integration,
            contradiction_resilience,
            epistemic_guard,
            omega_readiness,
        ])
        established = bool(registry) and bool(compatibility) and omega_index >= 0.60 and epistemic_guard >= 0.95
        return {
            "omega_coherence_index_established": established,
            "omega_coherence_index": omega_index,
            "self_description_coherence_score": self_description_coherence,
            "dynamic_compatibility_coherence_score": dynamic_compatibility_coherence,
            "cross_level_integration_score": cross_level_integration,
            "contradiction_resilience_score": contradiction_resilience,
            "epistemic_guard_score": epistemic_guard,
            "omega_readiness_score": omega_readiness,
            "causal_activity_readiness_score": causal_activity_readiness,
            "omega_stability_readiness_score": stability_readiness,
            "reflexive_grounding_score": reflexive_grounding,
            "registered_self_description_count": entry_count,
        }

    def _coherence_profile(self, registry: dict[str, Any], compatibility: dict[str, Any], reflexive: dict[str, Any], components: dict[str, Any]) -> dict[str, Any]:
        return {
            "self_description_registry_available": bool(registry),
            "dynamic_compatibility_matrix_available": bool(compatibility),
            "reflexive_grounding_available": bool(reflexive),
            "self_description_status": registry.get("self_description_registry_status"),
            "dynamic_compatibility_status": compatibility.get("dynamic_compatibility_matrix_status"),
            "reflexive_model_usage_status": reflexive.get("reflexive_model_usage_status"),
            "coherence_classification": self._classify(components["omega_coherence_index"]),
            "omega_transition_readiness": "ready_for_AE4" if components["omega_coherence_index_established"] else "not_ready_for_AE4",
            "no_forbidden_epistemic_claims": components["epistemic_guard_score"] >= 0.95,
        }

    def _classify(self, score: float) -> str:
        score = _clamp(score)
        if score >= 0.80:
            return "high_functional_omega_coherence"
        if score >= 0.60:
            return "established_functional_omega_coherence"
        if score >= 0.40:
            return "partial_functional_omega_coherence"
        return "insufficient_functional_omega_coherence"

    def _failure_conditions(self, registry: dict[str, Any], compatibility: dict[str, Any], components: dict[str, Any], profile: dict[str, Any]) -> list[str]:
        failures: list[str] = []
        if not registry and not compatibility:
            failures.append("no_omega_coherence_evidence_available")
        if not registry:
            failures.append("self_description_registry_missing")
        if not compatibility:
            failures.append("dynamic_compatibility_matrix_missing")
        if components.get("omega_coherence_index", 0.0) < 0.60:
            failures.append("omega_coherence_index_below_threshold")
        if components.get("epistemic_guard_score", 0.0) < 0.95:
            failures.append("epistemic_guard_failed")
        return failures

    def _summary_registry(self, registry: dict[str, Any]) -> dict[str, Any]:
        return {
            "available": bool(registry),
            "status": registry.get("self_description_registry_status"),
            "score": _clamp(registry.get("self_description_registry_score")),
            "omega_readiness_score": _clamp(registry.get("omega_readiness_score")),
            "entry_count": len(_as_list(registry.get("registered_self_descriptions"))),
        }

    def _summary_compatibility(self, compatibility: dict[str, Any]) -> dict[str, Any]:
        return {
            "available": bool(compatibility),
            "status": compatibility.get("dynamic_compatibility_matrix_status"),
            "score": _clamp(compatibility.get("dynamic_compatibility_score")),
            "omega_compatibility_readiness_score": _clamp(compatibility.get("omega_compatibility_readiness_score")),
            "contradiction_resilience_score": _clamp(compatibility.get("contradiction_resilience_score"), 1.0 if compatibility else 0.0),
        }

    def _summary_reflexive(self, reflexive: dict[str, Any]) -> dict[str, Any]:
        return {
            "available": bool(reflexive),
            "status": reflexive.get("reflexive_model_usage_status"),
            "score": _clamp(reflexive.get("reflexive_model_usage_score")),
            "integration_score": _clamp(reflexive.get("memory_identity_reflexivity_integration_score"), _clamp(reflexive.get("reflexive_model_usage_score"))),
        }

    def _persist(self, result: dict[str, Any]) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUTPUT_DIR / "latest_omega_coherence_index.json"
        md_path = OUTPUT_DIR / "latest_omega_coherence_index.md"
        prom_path = OUTPUT_DIR / "latest_omega_coherence_index.prom"
        hist_path = OUTPUT_DIR / "omega_coherence_index_history.jsonl"
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        with hist_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp_utc": result["timestamp_utc"],
                "status": result["omega_coherence_index_status"],
                "omega_coherence_index": result["omega_coherence_index"],
                "omega_readiness_score": result["omega_readiness_score"],
            }, ensure_ascii=False, sort_keys=True) + "\n")
        result["paths"] = {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path), "history": str(hist_path)}

    def _markdown(self, r: dict[str, Any]) -> str:
        lines = [
            "# AE3 — Omega Coherence Index",
            "",
            f"Status: {r['omega_coherence_index_status']}",
            f"Omega coherence index: {r['omega_coherence_index']:.6f}",
            f"Omega readiness score: {r['omega_readiness_score']:.6f}",
            "",
            "## Omega components",
            f"- Self-description coherence: {r['self_description_coherence_score']:.6f}",
            f"- Dynamic compatibility coherence: {r['dynamic_compatibility_coherence_score']:.6f}",
            f"- Cross-level integration: {r['cross_level_integration_score']:.6f}",
            f"- Contradiction resilience: {r['contradiction_resilience_score']:.6f}",
            f"- Epistemic guard: {r['epistemic_guard_score']:.6f}",
            "",
            "## Omega coherence profile",
            f"Classification: {r['omega_coherence_profile']['coherence_classification']}",
            f"Transition readiness: {r['omega_coherence_profile']['omega_transition_readiness']}",
            "",
            "## AE chain position",
            "AE3 integrates AE1 and AE2 and prepares AE4 omega causal activity testing.",
            "",
            "## Epistemic guard",
            "Functional conclusion only. No consciousness, subjectivity, qualia, or phenomenology is asserted.",
        ]
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: dict[str, Any]) -> str:
        metrics = {
            "oce_omega_coherence_index": r["omega_coherence_index"],
            "oce_omega_coherence_index_established": 1.0 if r["omega_coherence_index_established"] else 0.0,
            "oce_self_description_coherence_score": r["self_description_coherence_score"],
            "oce_dynamic_compatibility_coherence_score": r["dynamic_compatibility_coherence_score"],
            "oce_cross_level_integration_score": r["cross_level_integration_score"],
            "oce_omega_contradiction_resilience_score": r["contradiction_resilience_score"],
            "oce_omega_readiness_score": r["omega_readiness_score"],
            "oce_omega_causal_activity_readiness_score": r["causal_activity_readiness_score"],
            "oce_omega_stability_readiness_score": r["omega_stability_readiness_score"],
        }
        return "\n".join(f"{k} {float(v):.6f}" for k, v in metrics.items()) + "\n"
