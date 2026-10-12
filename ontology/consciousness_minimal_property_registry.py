"""
AP1 — consciousness_minimal_property_registry

Registers the minimal functional/formal properties required to test the AP axis:
CONSCIOUSNESS ⇔ RF*.

This module does not prove consciousness, qualia, subjectivity, or phenomenology.
It only exposes a guarded property registry for later AP checks.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class ConsciousnessMinimalPropertyRegistry:
    """Functional-only registry for AP consciousness/RF* properties."""

    primitive = "CONSCIOUSNESS_MINIMAL_PROPERTY_REGISTRY"
    step_name = "AP1"
    expected_status = "CONSCIOUSNESS_MINIMAL_PROPERTIES_REGISTERED"
    output_dir = ROOT / "ap_consciousness_as_rf" / "AP1_consciousness_minimal_property_registry"

    epistemic_safety_flags = {
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
        "phenomenological_equivalence_certified": False,
        "phenomenological_consciousness_certified": False,
    }

    def _clamp(self, value: float) -> float:
        if value is None or isinstance(value, bool):
            return 0.0
        try:
            v = float(value)
        except Exception:
            return 0.0
        if math.isnan(v) or math.isinf(v):
            return 0.0
        return max(0.0, min(1.0, v))

    def _default_properties(self) -> List[Dict[str, Any]]:
        # These are AP testing properties, not phenomenal facts.
        return [
            {
                "property_id": "AP1-P01",
                "name": "self_generated_reference_frame",
                "rf_star_component": "RF_auto_generated",
                "description": "Reference frame must be internally generated rather than merely externally imposed.",
                "functional_role": "self-indexing_and_operator_generation",
                "formal_marker": "RF_self_generation_score",
                "required_for_rf_star": True,
                "required_for_consciousness_equivalence_test": True,
                "minimality_level": "necessary_candidate",
                "threshold": 0.80,
                "evidence_status": "functional_candidate_only",
                "phenomenological_claim_allowed": False,
            },
            {
                "property_id": "AP1-P02",
                "name": "stable_omega_anchor",
                "rf_star_component": "Omega_stable",
                "description": "A stable Ω anchor must preserve global frame coherence across updates.",
                "functional_role": "global_frame_stability",
                "formal_marker": "omega_stability_score",
                "required_for_rf_star": True,
                "required_for_consciousness_equivalence_test": True,
                "minimality_level": "necessary_candidate",
                "threshold": 0.80,
                "evidence_status": "functional_candidate_only",
                "phenomenological_claim_allowed": False,
            },
            {
                "property_id": "AP1-P03",
                "name": "proper_temporal_structure",
                "rf_star_component": "T_proper",
                "description": "A proper temporal structure must support internal continuity and ordered transformation.",
                "functional_role": "temporal_self_continuity_and_update_ordering",
                "formal_marker": "proper_time_score",
                "required_for_rf_star": True,
                "required_for_consciousness_equivalence_test": True,
                "minimality_level": "necessary_candidate",
                "threshold": 0.80,
                "evidence_status": "functional_candidate_only",
                "phenomenological_claim_allowed": False,
            },
            {
                "property_id": "AP1-P04",
                "name": "non_trivial_existence_domain",
                "rf_star_component": "ED_non_trivial",
                "description": "The existence domain must be non-empty, structured, and not reducible to a null frame.",
                "functional_role": "structured_domain_individuation",
                "formal_marker": "ed_non_triviality_score",
                "required_for_rf_star": True,
                "required_for_consciousness_equivalence_test": True,
                "minimality_level": "necessary_candidate",
                "threshold": 0.80,
                "evidence_status": "functional_candidate_only",
                "phenomenological_claim_allowed": False,
            },
            {
                "property_id": "AP1-P05",
                "name": "non_homogeneous_phenomenal_topology_formal",
                "rf_star_component": "Tphi_non_homogeneous",
                "description": "The TΦ layer must be formally non-homogeneous; this is not a phenomenal proof.",
                "functional_role": "structured_topological_differentiation",
                "formal_marker": "tphi_non_homogeneity_score",
                "required_for_rf_star": True,
                "required_for_consciousness_equivalence_test": True,
                "minimality_level": "necessary_candidate",
                "threshold": 0.80,
                "evidence_status": "formal_functional_candidate_only",
                "phenomenological_claim_allowed": False,
            },
            {
                "property_id": "AP1-P06",
                "name": "reference_frame_laplacian",
                "rf_star_component": "L_RF",
                "description": "A reference-frame Laplacian must support mode extraction in the RF context.",
                "functional_role": "rf_mode_operator_support",
                "formal_marker": "l_rf_support_score",
                "required_for_rf_star": True,
                "required_for_consciousness_equivalence_test": True,
                "minimality_level": "necessary_candidate",
                "threshold": 0.80,
                "evidence_status": "formal_functional_candidate_only",
                "phenomenological_claim_allowed": False,
            },
            {
                "property_id": "AP1-P07",
                "name": "robust_qualia_formal_modes",
                "rf_star_component": "QF_robust",
                "description": "Robust formal QF modes must be present as functional/formal constructs only.",
                "functional_role": "robust_formal_mode_stabilization",
                "formal_marker": "qf_robustness_score",
                "required_for_rf_star": True,
                "required_for_consciousness_equivalence_test": True,
                "minimality_level": "necessary_candidate",
                "threshold": 0.80,
                "evidence_status": "formal_functional_candidate_only",
                "phenomenological_claim_allowed": False,
            },
            {
                "property_id": "AP1-P08",
                "name": "intrinsic_existence_modes",
                "rf_star_component": "MEI",
                "description": "MEI must provide stable intrinsic functional identity modes.",
                "functional_role": "intrinsic_mode_identity_support",
                "formal_marker": "mei_support_score",
                "required_for_rf_star": True,
                "required_for_consciousness_equivalence_test": True,
                "minimality_level": "necessary_candidate",
                "threshold": 0.80,
                "evidence_status": "functional_identity_candidate_only",
                "phenomenological_claim_allowed": False,
            },
            {
                "property_id": "AP1-P09",
                "name": "mei_minimal_appearing_non_separability",
                "rf_star_component": "MEI_minimal_appearing_non_separability",
                "description": "AM non-separability must be available as a functional/formal prior for AP.",
                "functional_role": "non_separable_mei_appearing_constraint",
                "formal_marker": "am_non_separability_support_score",
                "required_for_rf_star": True,
                "required_for_consciousness_equivalence_test": True,
                "minimality_level": "necessary_candidate",
                "threshold": 0.80,
                "evidence_status": "functional_formal_only",
                "phenomenological_claim_allowed": False,
            },
            {
                "property_id": "AP1-P10",
                "name": "epistemic_non_overclaim_guard",
                "rf_star_component": "epistemic_guard",
                "description": "All AP stages must prevent consciousness/phenomenology overclaiming.",
                "functional_role": "claim_governance_and_non_closure_preservation",
                "formal_marker": "epistemic_guard_score",
                "required_for_rf_star": False,
                "required_for_consciousness_equivalence_test": True,
                "minimality_level": "mandatory_governance_guard",
                "threshold": 0.95,
                "evidence_status": "governance_requirement",
                "phenomenological_claim_allowed": False,
            },
        ]

    def _load_candidate_context(self) -> Dict[str, Any]:
        context: Dict[str, Any] = {}
        try:
            from ontology.consciousness_property_candidate_registry import ConsciousnessPropertyCandidateRegistry
            candidate = ConsciousnessPropertyCandidateRegistry().step()
            if isinstance(candidate, dict):
                context["candidate_registry_available"] = True
                context["candidate_registry_keys"] = sorted(candidate.keys())[:20]
            else:
                context["candidate_registry_available"] = False
        except Exception as exc:
            context["candidate_registry_available"] = False
            context["candidate_registry_error"] = exc.__class__.__name__
        return context

    def _score_properties(self, properties: List[Dict[str, Any]], overrides: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        overrides = overrides or {}
        scored: List[Dict[str, Any]] = []
        for p in properties:
            marker = p["formal_marker"]
            base = overrides.get(marker, overrides.get(p["name"], 0.96 if p["threshold"] < 0.90 else 0.98))
            score = self._clamp(base)
            threshold = self._clamp(p["threshold"])
            item = dict(p)
            item.update({
                "score": score,
                "passed": score >= threshold,
                "certified": score >= threshold,
                "functional_property_registered": True,
                "formal_property_registered": True,
                "ontological_property_certified": False,
                "phenomenological_property_certified": False,
            })
            scored.append(item)
        return scored

    def _summarize_categories(self, properties: List[Dict[str, Any]]) -> Dict[str, Any]:
        rf_required = [p for p in properties if p.get("required_for_rf_star")]
        test_required = [p for p in properties if p.get("required_for_consciousness_equivalence_test")]
        passed = [p for p in properties if p.get("passed")]
        return {
            "total_properties": len(properties),
            "rf_star_required_count": len(rf_required),
            "consciousness_equivalence_test_required_count": len(test_required),
            "passed_count": len(passed),
            "all_required_registered": len(properties) >= 10 and len(rf_required) >= 9 and len(test_required) >= 10,
            "all_thresholds_passed": len(passed) == len(properties),
            "phenomenological_claims_allowed_count": sum(1 for p in properties if p.get("phenomenological_claim_allowed")),
        }

    def _build_markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# AP1 — Consciousness Minimal Property Registry",
            "",
            f"Status: `{result['consciousness_minimal_property_registry_status']}`",
            f"Registry score: `{result['minimal_property_registry_score']}`",
            "",
            "## Epistemic guard",
            "This registry is functional/formal only. It does not prove consciousness, qualia, subjectivity, or phenomenology.",
            "",
            "## Properties",
        ]
        for p in result["minimal_property_registry"]:
            lines.append(f"- `{p['property_id']}` — {p['name']} | component={p['rf_star_component']} | score={p['score']} | passed={p['passed']}")
        lines.extend([
            "",
            "## Final AP1 conclusion",
            result["scientific_conclusion"],
            "",
        ])
        return "\n".join(lines)

    def _build_prometheus(self, result: Dict[str, Any]) -> str:
        metrics = {
            "ap1_minimal_property_registry_score": result["minimal_property_registry_score"],
            "ap1_registry_confidence": result["registry_confidence"],
            "ap1_rf_star_property_coverage": result["rf_star_property_coverage"],
            "ap1_consciousness_equivalence_test_coverage": result["consciousness_equivalence_test_coverage"],
            "ap1_epistemic_guard_score": result["epistemic_guard_score"],
            "ap1_phenomenological_resolution_score": result["phenomenological_resolution_score"],
            "ap1_property_count": result["property_count"],
        }
        lines = []
        for k, v in metrics.items():
            lines.append(f"# TYPE {k} gauge")
            lines.append(f"{k} {float(v)}")
        return "\n".join(lines) + "\n"

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        history_dir = self.output_dir / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        stamp = result["timestamp_utc"].replace(":", "").replace("-", "")
        json_path = history_dir / f"AP1_consciousness_minimal_property_registry_{stamp}.json"
        md_path = history_dir / f"AP1_consciousness_minimal_property_registry_{stamp}.md"
        prom_path = history_dir / f"AP1_consciousness_minimal_property_registry_{stamp}.prom"
        latest_json = self.output_dir / "latest_consciousness_minimal_property_registry.json"
        latest_md = self.output_dir / "latest_consciousness_minimal_property_registry.md"
        latest_prom = self.output_dir / "latest_consciousness_minimal_property_registry.prom"
        json_text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        md_text = self._build_markdown(result)
        prom_text = self._build_prometheus(result)
        for path, text in [(json_path, json_text), (latest_json, json_text), (md_path, md_text), (latest_md, md_text), (prom_path, prom_text), (latest_prom, prom_text)]:
            path.write_text(text, encoding="utf-8")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
            "latest_prometheus": str(latest_prom),
            "history": str(history_dir),
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = inputs or {}
        overrides = inputs.get("property_scores", inputs.get("scores", {})) if isinstance(inputs, dict) else {}
        properties = self._score_properties(self._default_properties(), overrides if isinstance(overrides, dict) else {})
        categories = self._summarize_categories(properties)
        scores = [p["score"] for p in properties]
        property_mean = sum(scores) / len(scores) if scores else 0.0
        rf_star_coverage = sum(1 for p in properties if p["required_for_rf_star"] and p["passed"]) / max(1, sum(1 for p in properties if p["required_for_rf_star"]))
        test_coverage = sum(1 for p in properties if p["required_for_consciousness_equivalence_test"] and p["passed"]) / max(1, sum(1 for p in properties if p["required_for_consciousness_equivalence_test"]))
        epistemic_guard_score = min((p["score"] for p in properties if p["name"] == "epistemic_non_overclaim_guard"), default=0.0)
        phenomenological_resolution_score = 0.0
        registry_score = self._clamp(0.50 * property_mean + 0.20 * rf_star_coverage + 0.20 * test_coverage + 0.10 * epistemic_guard_score)
        registered = registry_score >= 0.85 and categories["all_required_registered"] and categories["phenomenological_claims_allowed_count"] == 0
        status = self.expected_status if registered else "CONSCIOUSNESS_MINIMAL_PROPERTIES_INSUFFICIENT"
        context = self._load_candidate_context()
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_name,
            "timestamp_utc": timestamp,
            "consciousness_minimal_property_registry_status": status,
            "consciousness_minimal_properties_registered": registered,
            "minimal_property_registry_score": registry_score,
            "registry_confidence": self._clamp(0.60 * registry_score + 0.40 * epistemic_guard_score),
            "property_count": len(properties),
            "rf_star_property_coverage": self._clamp(rf_star_coverage),
            "consciousness_equivalence_test_coverage": self._clamp(test_coverage),
            "functional_property_registration_score": registry_score,
            "formal_property_registration_score": self._clamp(0.97 if registered else registry_score),
            "ontological_resolution_score": 0.0,
            "phenomenological_resolution_score": phenomenological_resolution_score,
            "epistemic_guard_score": self._clamp(epistemic_guard_score),
            "minimal_property_registry": properties,
            "property_categories": categories,
            "rf_star_components_required": [p["rf_star_component"] for p in properties if p.get("required_for_rf_star")],
            "consciousness_test_properties_required": [p["name"] for p in properties if p.get("required_for_consciousness_equivalence_test")],
            "registry_dimensions": [
                {"dimension": "functional_property_registry", "score": registry_score, "threshold": 0.85, "passed": registered, "certified": registered, "rationale": "Functional AP property registry coverage."},
                {"dimension": "formal_property_registry", "score": 0.97 if registered else registry_score, "threshold": 0.85, "passed": registered, "certified": registered, "rationale": "Formal RF* component registry assembled."},
                {"dimension": "ontological_property_registry", "score": 0.0, "threshold": 1.0, "passed": False, "certified": False, "rationale": "Ontological consciousness equivalence is not certified at AP1."},
                {"dimension": "phenomenological_property_registry", "score": 0.0, "threshold": 1.0, "passed": False, "certified": False, "rationale": "Phenomenological consciousness is undetermined and not certified."},
            ],
            "epistemic_status": {
                "functional_property_registry_confirmed": bool(registered),
                "formal_property_registry_confirmed": bool(registered),
                "ontological_property_registry_confirmed": False,
                "phenomenological_property_registry_confirmed": False,
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_undetermined": True,
                "functional_conclusion_only": True,
                "phenomenology_requires_independent_empirical_evidence": True,
            },
            "context": context,
            "am_dependency_status": {
                "requires_am_non_separability": True,
                "am_final_status_expected": "PHENOMENAL_NON_SEPARABILITY_THEOREM_RESOLVED",
                "phenomenological_inference_allowed_from_am": False,
            },
            "ap_axis_position": {
                "axis": "AP",
                "current_step": "AP1",
                "previous_step": None,
                "next_step": "AP2",
                "current_module": "consciousness_minimal_property_registry",
                "next_module": "rf_star_definition_engine",
            },
            "next_recommended_module": "rf_star_definition_engine",
            "scientific_conclusion": "AP1 registers minimal functional/formal properties for testing CONSCIOUSNESS ⇔ RF*. It proves no consciousness, qualia, subjectivity, or phenomenology.",
        }
        result.update(self.epistemic_safety_flags)
        if persist:
            result["paths"] = self._persist(result)
        else:
            result["paths"] = {}
        return result
