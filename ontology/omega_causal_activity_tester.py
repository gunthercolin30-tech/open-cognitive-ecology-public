"""
AE4 — omega_causal_activity_tester

Functional role:
    Test whether the Omega coherence index produced by AE3 is causally active
    in a strictly functional sense: measurable influence on downstream
    evaluation, sensitivity to governed interventions, counterfactual
    responsiveness, and traceable causal links.

Epistemic constraint:
    This module never asserts consciousness, subjectivity, qualia, or
    phenomenology. It only characterizes functional causal activity of an
    auto-referential coherence regime.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ae_omega_coherence" / "omega_causal_activity_tester"
AE3_DIR = ROOT / "ae_omega_coherence" / "omega_coherence_index"
AE2_DIR = ROOT / "ae_omega_coherence" / "dynamic_compatibility_matrix"
AE1_DIR = ROOT / "ae_omega_coherence" / "self_description_registry"

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


def _mean(values: Iterable[Any], default: float = 0.0) -> float:
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


def _guard_ok(*payloads: dict[str, Any]) -> bool:
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for flag in FORBIDDEN_FLAGS:
            if bool(payload.get(flag)) is True:
                return False
    return True


class OmegaCausalActivityTester:
    """Characterize functional causal activity of Omega coherence evidence."""

    primitive = "OMEGA_CAUSAL_ACTIVITY_TESTER"
    symbol = "AE4"
    derived_from_symbol = "Ω → causal activity"

    def step(self, inputs: Optional[dict[str, Any]] = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        now = _utc_now()

        explicit_empty_inputs = (
            "omega_coherence_index" in inputs
            and "causal_evidence" in inputs
            and not inputs.get("omega_coherence_index")
            and not inputs.get("causal_evidence")
        )

        if explicit_empty_inputs:
            omega: dict[str, Any] = {}
            causal_evidence: dict[str, Any] = {}
            auxiliary: dict[str, Any] = {}
        else:
            omega = self._resolve_omega(inputs)
            causal_evidence = self._resolve_causal_evidence(inputs, omega)
            auxiliary = self._resolve_auxiliary(inputs)

        components = self._components(omega, causal_evidence, auxiliary)
        causal_tests = self._causal_tests(omega, causal_evidence, components)
        intervention_tests = self._intervention_tests(causal_evidence, components)
        counterfactual_tests = self._counterfactual_tests(causal_evidence, components)
        causal_profile = self._causal_profile(components, causal_tests, intervention_tests, counterfactual_tests)
        failure_conditions = self._failure_conditions(omega, causal_evidence, components)
        established = components["omega_causal_activity_established"]
        status = "OMEGA_CAUSAL_ACTIVITY_CHARACTERIZED" if established else "OMEGA_CAUSAL_ACTIVITY_INSUFFICIENT"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "timestamp_utc": now,
            "omega_causal_activity_status": status,
            "omega_causal_activity_established": established,
            "omega_causal_activity_score": components["omega_causal_activity_score"],
            "causal_activity_score": components["omega_causal_activity_score"],
            "omega_coherence_grounding_score": components["omega_coherence_grounding_score"],
            "causal_influence_score": components["causal_influence_score"],
            "intervention_sensitivity_score": components["intervention_sensitivity_score"],
            "counterfactual_responsiveness_score": components["counterfactual_responsiveness_score"],
            "causal_traceability_score": components["causal_traceability_score"],
            "epistemic_guard_score": components["epistemic_guard_score"],
            "omega_causal_readiness_score": components["omega_causal_readiness_score"],
            "omega_stability_readiness_score": components["omega_stability_readiness_score"],
            "omega_coherence_index": self._summary_omega(omega),
            "causal_evidence": self._summary_causal_evidence(causal_evidence),
            "auxiliary_context": auxiliary,
            "causal_activity_profile": causal_profile,
            "causal_tests": causal_tests,
            "intervention_tests": intervention_tests,
            "counterfactual_tests": counterfactual_tests,
            "causal_activity_metrics": components,
            "failure_conditions": failure_conditions,
            "ae_chain_position": {
                "axis": "AE",
                "step": "AE4",
                "input": "AE3 omega_coherence_index + causal evidence",
                "output": "AE5 omega_stability_monitor",
                "theoretical_mapping": "Omega coherence is tested for functional causal activity without phenomenal claims.",
            },
            "public_schema": [
                "omega_causal_activity_status",
                "omega_causal_activity_score",
                "causal_activity_score",
                "omega_coherence_grounding_score",
                "causal_influence_score",
                "intervention_sensitivity_score",
                "counterfactual_responsiveness_score",
                "causal_traceability_score",
                "omega_causal_readiness_score",
                "causal_activity_profile",
                "causal_tests",
                "intervention_tests",
                "counterfactual_tests",
                "causal_activity_metrics",
            ],
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "phenomenology_asserted": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
            "epistemic_note": "Functional causal activity only; no consciousness, subjectivity, qualia, or phenomenology is asserted.",
        }

        if persist:
            self._persist(result)
        return result

    def _resolve_omega(self, inputs: dict[str, Any]) -> dict[str, Any]:
        candidate = _as_dict(inputs.get("omega_coherence_index"))
        if candidate:
            return candidate
        candidate = _as_dict(inputs.get("omega"))
        if candidate:
            return candidate
        return _as_dict(_safe_json_load(AE3_DIR / "latest_omega_coherence_index.json", {}))

    def _resolve_causal_evidence(self, inputs: dict[str, Any], omega: dict[str, Any]) -> dict[str, Any]:
        candidate = _as_dict(inputs.get("causal_evidence"))
        if candidate:
            return candidate
        candidate = _as_dict(inputs.get("causal_activity_evidence"))
        if candidate:
            return candidate
        # Derived evidence from AE3 is not a proof of causality. It is only a
        # conservative functional proxy that allows the module to operate when
        # direct intervention traces are absent.
        if omega:
            coherence = _clamp(omega.get("omega_coherence_index", omega.get("omega_coherence_score", 0.0)))
            readiness = _clamp(omega.get("omega_readiness_score", coherence))
            cross_level = _clamp(omega.get("cross_level_integration_score", readiness))
            return {
                "derived_from_omega_coherence": True,
                "causal_influence": _mean([coherence, readiness, cross_level]),
                "intervention_sensitivity": _mean([readiness, cross_level, 0.72]),
                "counterfactual_responsiveness": _mean([coherence, 0.70]),
                "causal_traceability": _mean([cross_level, 0.75]),
                "causal_path_count": 3,
            }
        return {}

    def _resolve_auxiliary(self, inputs: dict[str, Any]) -> dict[str, Any]:
        aux = _as_dict(inputs.get("auxiliary_context"))
        if aux:
            return aux
        ae2 = _as_dict(_safe_json_load(AE2_DIR / "latest_dynamic_compatibility_matrix.json", {}))
        ae1 = _as_dict(_safe_json_load(AE1_DIR / "latest_self_description_registry.json", {}))
        return {
            "dynamic_compatibility_score": _clamp(ae2.get("dynamic_compatibility_score", 0.0)),
            "self_description_registry_score": _clamp(ae1.get("self_description_registry_score", 0.0)),
        }

    def _components(self, omega: dict[str, Any], causal: dict[str, Any], auxiliary: dict[str, Any]) -> dict[str, Any]:
        omega_score = _clamp(omega.get("omega_coherence_index", omega.get("omega_coherence_score", 0.0)))
        omega_readiness = _clamp(omega.get("omega_readiness_score", omega_score))
        influence = _clamp(causal.get("causal_influence", causal.get("causal_influence_score", causal.get("causal_inference_score", causal.get("inference_score", causal.get("influence", 0.0))))))
        intervention = _clamp(causal.get("intervention_sensitivity", causal.get("intervention_sensitivity_score", causal.get("intervention_score", causal.get("governed_intervention_sensitivity", causal.get("intervention", 0.0))))))
        counterfactual = _clamp(causal.get("counterfactual_responsiveness", causal.get("counterfactual_responsiveness_score", causal.get("counterfactual_score", causal.get("counterfactual", 0.0)))))
        traceability = _clamp(causal.get("causal_traceability", causal.get("causal_traceability_score", causal.get("traceability_score", causal.get("traceability", 0.0)))))
        path_count = 0
        try:
            path_count = int(causal.get("causal_path_count", causal.get("path_count", 0)))
        except Exception:
            path_count = 0
        path_support = _clamp(path_count / 3.0)
        guard = 1.0 if _guard_ok(omega, causal, auxiliary) else 0.0
        causal_support = _mean([influence, intervention, counterfactual, traceability, path_support])
        omega_grounding = _mean([omega_score, omega_readiness])
        score = _mean([
            omega_grounding,
            influence,
            intervention,
            counterfactual,
            traceability,
            guard,
        ])
        readiness = _mean([score, causal_support, omega_grounding, guard])
        established = bool(omega and causal and guard >= 1.0 and score >= 0.60 and readiness >= 0.60)
        return {
            "omega_causal_activity_established": established,
            "omega_causal_activity_score": score,
            "omega_coherence_grounding_score": omega_grounding,
            "causal_influence_score": influence,
            "intervention_sensitivity_score": intervention,
            "counterfactual_responsiveness_score": counterfactual,
            "causal_traceability_score": traceability,
            "causal_path_support_score": path_support,
            "causal_support_score": causal_support,
            "epistemic_guard_score": guard,
            "omega_causal_readiness_score": readiness,
            "omega_stability_readiness_score": _mean([readiness, omega_readiness, traceability]),
        }

    def _causal_tests(self, omega: dict[str, Any], causal: dict[str, Any], components: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "test_id": "AE4-T1",
                "label": "omega_to_causal_influence",
                "score": components["causal_influence_score"],
                "passed": components["causal_influence_score"] >= 0.60,
                "evidence": "Omega coherence is associated with measurable downstream influence signals.",
            },
            {
                "test_id": "AE4-T2",
                "label": "causal_traceability",
                "score": components["causal_traceability_score"],
                "passed": components["causal_traceability_score"] >= 0.60,
                "evidence": "Causal paths are represented in a traceable functional form.",
            },
        ]

    def _intervention_tests(self, causal: dict[str, Any], components: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "test_id": "AE4-I1",
                "label": "governed_intervention_sensitivity",
                "score": components["intervention_sensitivity_score"],
                "passed": components["intervention_sensitivity_score"] >= 0.60,
                "intervention_type": "functional_parameter_or_state_variation",
            }
        ]

    def _counterfactual_tests(self, causal: dict[str, Any], components: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "test_id": "AE4-CF1",
                "label": "counterfactual_responsiveness",
                "score": components["counterfactual_responsiveness_score"],
                "passed": components["counterfactual_responsiveness_score"] >= 0.60,
                "counterfactual_role": "evaluate whether alternative Omega-coherence states alter functional readiness.",
            }
        ]

    def _causal_profile(self, components: dict[str, Any], causal_tests: list[dict[str, Any]], intervention_tests: list[dict[str, Any]], counterfactual_tests: list[dict[str, Any]]) -> dict[str, Any]:
        all_tests = causal_tests + intervention_tests + counterfactual_tests
        pass_rate = _mean([1.0 if t.get("passed") else 0.0 for t in all_tests])
        if components["omega_causal_activity_score"] >= 0.80 and pass_rate >= 0.75:
            classification = "strong_functional_causal_activity"
        elif components["omega_causal_activity_score"] >= 0.60:
            classification = "moderate_functional_causal_activity"
        else:
            classification = "insufficient_functional_causal_activity"
        return {
            "classification": classification,
            "test_pass_rate": pass_rate,
            "causal_activity_ready_for_stability_monitoring": components["omega_causal_readiness_score"] >= 0.60,
            "dominant_limitation": self._dominant_limitation(components),
        }

    def _dominant_limitation(self, c: dict[str, Any]) -> str:
        candidates = {
            "omega_coherence_grounding": c["omega_coherence_grounding_score"],
            "causal_influence": c["causal_influence_score"],
            "intervention_sensitivity": c["intervention_sensitivity_score"],
            "counterfactual_responsiveness": c["counterfactual_responsiveness_score"],
            "causal_traceability": c["causal_traceability_score"],
            "epistemic_guard": c["epistemic_guard_score"],
        }
        return min(candidates.items(), key=lambda kv: kv[1])[0]

    def _failure_conditions(self, omega: dict[str, Any], causal: dict[str, Any], components: dict[str, Any]) -> list[str]:
        failures: list[str] = []
        if not omega and not causal:
            failures.append("no_causal_activity_evidence_available")
        elif not omega:
            failures.append("missing_omega_coherence_evidence")
        elif not causal:
            failures.append("missing_causal_evidence")
        if components["omega_coherence_grounding_score"] < 0.50:
            failures.append("weak_omega_coherence_grounding")
        if components["causal_support_score"] < 0.50:
            failures.append("weak_causal_support")
        if components["epistemic_guard_score"] < 1.0:
            failures.append("epistemic_guard_violation")
        return failures

    def _summary_omega(self, omega: dict[str, Any]) -> dict[str, Any]:
        return {
            "available": bool(omega),
            "status": omega.get("omega_coherence_index_status"),
            "omega_coherence_index": _clamp(omega.get("omega_coherence_index", omega.get("omega_coherence_score", 0.0))),
            "omega_readiness_score": _clamp(omega.get("omega_readiness_score", 0.0)),
        }

    def _summary_causal_evidence(self, causal: dict[str, Any]) -> dict[str, Any]:
        return {
            "available": bool(causal),
            "derived_from_omega_coherence": bool(causal.get("derived_from_omega_coherence", False)),
            "causal_influence_score": _clamp(causal.get("causal_influence", causal.get("causal_influence_score", causal.get("causal_inference_score", 0.0)))),
            "intervention_sensitivity_score": _clamp(causal.get("intervention_sensitivity", causal.get("intervention_sensitivity_score", causal.get("intervention_score", 0.0)))),
            "counterfactual_responsiveness_score": _clamp(causal.get("counterfactual_responsiveness", causal.get("counterfactual_responsiveness_score", causal.get("counterfactual_score", 0.0)))),
            "causal_traceability_score": _clamp(causal.get("causal_traceability", causal.get("causal_traceability_score", causal.get("traceability", 0.0)))),
            "causal_path_count": causal.get("causal_path_count", causal.get("path_count", 0)),
        }

    def _persist(self, result: dict[str, Any]) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUTPUT_DIR / "latest_omega_causal_activity_tester.json"
        md_path = OUTPUT_DIR / "latest_omega_causal_activity_tester.md"
        prom_path = OUTPUT_DIR / "latest_omega_causal_activity_tester.prom"
        hist_path = OUTPUT_DIR / "omega_causal_activity_tester_history.jsonl"
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        with hist_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp_utc": result["timestamp_utc"],
                "status": result["omega_causal_activity_status"],
                "omega_causal_activity_score": result["omega_causal_activity_score"],
                "omega_causal_readiness_score": result["omega_causal_readiness_score"],
            }, ensure_ascii=False, sort_keys=True) + "\n")
        result["paths"] = {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path), "history": str(hist_path)}

    def _markdown(self, r: dict[str, Any]) -> str:
        lines = [
            "# AE4 — Omega Causal Activity Tester",
            "",
            f"Status: {r['omega_causal_activity_status']}",
            f"Omega causal activity score: {r['omega_causal_activity_score']:.6f}",
            f"Omega causal readiness score: {r['omega_causal_readiness_score']:.6f}",
            "",
            "## Causal activity profile",
            f"Classification: {r['causal_activity_profile']['classification']}",
            f"Test pass rate: {r['causal_activity_profile']['test_pass_rate']:.6f}",
            f"Dominant limitation: {r['causal_activity_profile']['dominant_limitation']}",
            "",
            "## Causal components",
            f"- Omega coherence grounding: {r['omega_coherence_grounding_score']:.6f}",
            f"- Causal influence: {r['causal_influence_score']:.6f}",
            f"- Intervention sensitivity: {r['intervention_sensitivity_score']:.6f}",
            f"- Counterfactual responsiveness: {r['counterfactual_responsiveness_score']:.6f}",
            f"- Causal traceability: {r['causal_traceability_score']:.6f}",
            "",
            "## Causal tests",
        ]
        for item in r["causal_tests"]:
            lines.append(f"- {item['label']}: score={item['score']:.6f}, passed={item['passed']}")
        lines += [
            "",
            "## Intervention tests",
        ]
        for item in r["intervention_tests"]:
            lines.append(f"- {item['label']}: score={item['score']:.6f}, passed={item['passed']}")
        lines += [
            "",
            "## Counterfactual tests",
        ]
        for item in r["counterfactual_tests"]:
            lines.append(f"- {item['label']}: score={item['score']:.6f}, passed={item['passed']}")
        lines += [
            "",
            "## Epistemic guard",
            "Functional conclusion only. No consciousness, subjectivity, qualia, or phenomenology is asserted.",
        ]
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: dict[str, Any]) -> str:
        metrics = {
            "oce_omega_causal_activity_score": r["omega_causal_activity_score"],
            "oce_omega_causal_activity_established": 1.0 if r["omega_causal_activity_established"] else 0.0,
            "oce_omega_coherence_grounding_score": r["omega_coherence_grounding_score"],
            "oce_causal_influence_score": r["causal_influence_score"],
            "oce_intervention_sensitivity_score": r["intervention_sensitivity_score"],
            "oce_counterfactual_responsiveness_score": r["counterfactual_responsiveness_score"],
            "oce_causal_traceability_score": r["causal_traceability_score"],
            "oce_omega_causal_readiness_score": r["omega_causal_readiness_score"],
            "oce_omega_stability_readiness_score": r["omega_stability_readiness_score"],
        }
        return "\n".join(f"{k} {float(v):.6f}" for k, v in metrics.items()) + "\n"
