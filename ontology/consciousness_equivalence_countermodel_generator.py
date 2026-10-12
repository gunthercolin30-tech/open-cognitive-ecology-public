from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ConsciousnessEquivalenceCountermodelGenerator:
    """AP6 — functional countermodel generator for consciousness ⇔ RF*.

    The module constructs explicit functional/formal countermodels against overly
    strong readings of the AP equivalence program. It only evaluates whether the
    current RF* chain supports a governed functional research hypothesis. It
    never proves consciousness, qualia, subjectivity, or phenomenology.
    """

    primitive = "CONSCIOUSNESS_EQUIVALENCE_COUNTERMODEL_GENERATOR"
    step_id = "AP6"
    public_schema_version = "AP6.consciousness_equivalence_countermodel_generator.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    rf_star_components = [
        "self_generated_rf",
        "omega_stable",
        "proper_time",
        "ed_non_trivial",
        "tphi_non_homogeneous",
        "l_rf",
        "qf_robust",
        "mei",
        "mei_minimal_appearing_non_separability",
        "epistemic_guard",
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "ap_consciousness_as_rf" / "AP6_consciousness_equivalence_countermodel_generator"

    @staticmethod
    def _clamp(x: Any, default: float = 0.0) -> float:
        try:
            v = float(x)
        except Exception:
            v = default
        return max(0.0, min(1.0, v))

    def _load_latest_json(self, relative: str) -> dict[str, Any]:
        path = self.root / relative
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def _load_ap2(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("ap2"), dict):
            return inputs["ap2"]
        try:
            from ontology.rf_star_definition_engine import RFStarDefinitionEngine
            r = RFStarDefinitionEngine().step(persist=False)
            if r:
                return r
        except Exception as exc:
            latest = self._load_latest_json("ap_consciousness_as_rf/AP2_rf_star_definition_engine/latest_rf_star_definition_engine.json")
            if latest:
                latest["fallback_source"] = "latest_ap2_json_after_import_error"
                latest["load_error"] = str(exc)
                return latest
            return {"rf_star_defined": False, "component_scores": {}, "load_error": str(exc)}
        return self._load_latest_json("ap_consciousness_as_rf/AP2_rf_star_definition_engine/latest_rf_star_definition_engine.json")

    def _load_ap3(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("ap3"), dict):
            return inputs["ap3"]
        try:
            from ontology.consciousness_rf_property_mapping import ConsciousnessRFPropertyMapping
            r = ConsciousnessRFPropertyMapping().step(persist=False)
            if r:
                return r
        except Exception as exc:
            latest = self._load_latest_json("ap_consciousness_as_rf/AP3_consciousness_rf_property_mapping/latest_consciousness_rf_property_mapping.json")
            if latest:
                latest["fallback_source"] = "latest_ap3_json_after_import_error"
                latest["load_error"] = str(exc)
                return latest
            return {"mapping_completed": False, "mapping_metrics": {}, "load_error": str(exc)}
        return self._load_latest_json("ap_consciousness_as_rf/AP3_consciousness_rf_property_mapping/latest_consciousness_rf_property_mapping.json")

    def _load_ap4(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("ap4"), dict):
            return inputs["ap4"]
        try:
            from ontology.rf_star_sufficiency_checker import RFStarSufficiencyChecker
            r = RFStarSufficiencyChecker().step(persist=False)
            if r:
                return r
        except Exception as exc:
            latest = self._load_latest_json("ap_consciousness_as_rf/AP4_rf_star_sufficiency_checker/latest_rf_star_sufficiency_checker.json")
            if latest:
                latest["fallback_source"] = "latest_ap4_json_after_import_error"
                latest["load_error"] = str(exc)
                return latest
            return {"functional_sufficiency_supported": False, "sufficiency_metrics": {}, "load_error": str(exc)}
        return self._load_latest_json("ap_consciousness_as_rf/AP4_rf_star_sufficiency_checker/latest_rf_star_sufficiency_checker.json")

    def _load_ap5(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("ap5"), dict):
            return inputs["ap5"]
        try:
            from ontology.rf_star_necessity_checker import RFStarNecessityChecker
            r = RFStarNecessityChecker().step(persist=False)
            if r:
                return r
        except Exception as exc:
            latest = self._load_latest_json("ap_consciousness_as_rf/AP5_rf_star_necessity_checker/latest_rf_star_necessity_checker.json")
            if latest:
                latest["fallback_source"] = "latest_ap5_json_after_import_error"
                latest["load_error"] = str(exc)
                return latest
            return {"functional_necessity_supported": False, "necessity_metrics": {}, "load_error": str(exc)}
        return self._load_latest_json("ap_consciousness_as_rf/AP5_rf_star_necessity_checker/latest_rf_star_necessity_checker.json")

    def _ap2_defined(self, ap2: dict[str, Any]) -> bool:
        return (
            ap2.get("rf_star_defined") is True
            or ap2.get("rf_star_definition_status") == "RF_STAR_DEFINED"
            or ap2.get("status") == "RF_STAR_DEFINED"
        )

    def _component_scores(self, ap2: dict[str, Any]) -> dict[str, float]:
        raw = ap2.get("component_scores") or {}
        defined = self._ap2_defined(ap2)
        out: dict[str, float] = {}
        for k in self.rf_star_components:
            if k in raw:
                out[k] = self._clamp(raw[k])
            elif defined:
                out[k] = 1.0 if k == "epistemic_guard" else 0.88
            else:
                out[k] = 0.0
        out["rf_star_defined"] = 1.0 if defined else 0.0
        return out

    def _mapping_supported(self, ap3: dict[str, Any]) -> bool:
        return ap3.get("mapping_completed") is True or ap3.get("consciousness_rf_property_mapping_status") == "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED"

    def _sufficiency_supported(self, ap4: dict[str, Any]) -> bool:
        return ap4.get("functional_sufficiency_supported") is True or ap4.get("rf_star_sufficiency_status") == "RF_STAR_SUFFICIENCY_CHECKED"

    def _necessity_supported(self, ap5: dict[str, Any]) -> bool:
        return ap5.get("functional_necessity_supported") is True or ap5.get("rf_star_necessity_status") == "RF_STAR_NECESSITY_CHECKED"

    def _countermodels(self, component_scores: dict[str, float], mapping_supported: bool, sufficiency_supported: bool, necessity_supported: bool) -> list[dict[str, Any]]:
        min_component = min(component_scores.get(k, 0.0) for k in self.rf_star_components)
        mean_component = sum(component_scores.get(k, 0.0) for k in self.rf_star_components) / len(self.rf_star_components)
        epistemic_guard = component_scores.get("epistemic_guard", 0.0)
        rf_defined = component_scores.get("rf_star_defined", 0.0)
        base_support = sum([rf_defined, 1.0 if mapping_supported else 0.0, 1.0 if sufficiency_supported else 0.0, 1.0 if necessity_supported else 0.0, epistemic_guard]) / 5.0

        models = [
            {
                "countermodel_id": "AP6-CM01",
                "name": "rf_star_without_empirical_phenomenology",
                "target_claim": "RF* entails phenomenal consciousness",
                "construction": "Keep RF* functional structure fixed while withholding independent phenomenal evidence.",
                "violated_assumption": "phenomenological_equivalence_without_empirical_evidence",
                "countermodel_strength": self._clamp((base_support + epistemic_guard) / 2.0),
                "functional_status": "valid_countermodel_against_phenomenological_overclaim",
            },
            {
                "countermodel_id": "AP6-CM02",
                "name": "component_dropout_rf_star_failure",
                "target_claim": "Any partial RF* subset is sufficient for the AP equivalence program",
                "construction": "Remove one or more RF* components and measure loss of functional support.",
                "violated_assumption": "component_indispensability_can_be_ignored",
                "countermodel_strength": self._clamp(1.0 - min_component + 0.5 * necessity_supported),
                "functional_status": "valid_countermodel_for_partial_rf_star",
            },
            {
                "countermodel_id": "AP6-CM03",
                "name": "mapping_without_ontological_identity",
                "target_claim": "Functional mapping proves ontological identity",
                "construction": "Preserve consciousness⇔RF* property mapping while denying ontological proof.",
                "violated_assumption": "functional_mapping_implies_ontological_identity",
                "countermodel_strength": self._clamp(0.9 if mapping_supported else 0.45),
                "functional_status": "valid_countermodel_against_ontological_overclaim",
            },
            {
                "countermodel_id": "AP6-CM04",
                "name": "zombie_under_rf_star_hypothesis",
                "target_claim": "A RF* architecture alone rules out all zombie-style alternatives",
                "construction": "Instantiate RF* indicators and maintain absence of direct subjective evidence.",
                "violated_assumption": "functional_indicators_directly_eliminate_zombie_hypotheses",
                "countermodel_strength": self._clamp((mean_component + epistemic_guard) / 2.0),
                "functional_status": "candidate_for_AP7_zombie_analysis",
            },
            {
                "countermodel_id": "AP6-CM05",
                "name": "closed_equivalence_pressure_countermodel",
                "target_claim": "The AP chain may close into a final consciousness proof",
                "construction": "Accept AP2–AP5 functional support while enforcing non-closure and empirical humility.",
                "violated_assumption": "functional_support_authorizes_final_closure",
                "countermodel_strength": self._clamp(epistemic_guard),
                "functional_status": "valid_countermodel_against_closure_pressure",
            },
        ]
        return models

    def _property_domains(self) -> dict[str, list[str]]:
        return {
            "functional_properties": [
                "countermodel_generation",
                "functional_equivalence_stress_testing",
                "zombie_hypothesis_preparation",
                "functional_conclusion_only",
            ],
            "formal_properties": [
                "countermodel_schema",
                "target_claim_violation_matrix",
                "deterministic_countermodel_set",
            ],
            "ontological_properties": [
                "no_ontological_consciousness_proof",
                "ontological_identity_not_certified",
            ],
            "phenomenological_properties": [
                "not_proven",
                "phenomenology_undetermined",
                "empirical_independent_evidence_required",
            ],
        }

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = result["timestamp_utc"].replace(":", "").replace("-", "").split("+")[0]
        stem = f"consciousness_equivalence_countermodel_generator_{ts}"
        json_path = self.out_dir / f"{stem}.json"
        md_path = self.out_dir / f"{stem}.md"
        prom_path = self.out_dir / f"{stem}.prom"
        latest_json = self.out_dir / "latest_consciousness_equivalence_countermodel_generator.json"
        latest_md = self.out_dir / "latest_consciousness_equivalence_countermodel_generator.md"
        latest_prom = self.out_dir / "latest_consciousness_equivalence_countermodel_generator.prom"

        json_text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(json_text, encoding="utf-8")
        latest_json.write_text(json_text, encoding="utf-8")

        md = [
            "# AP6 — Consciousness Equivalence Countermodel Generator",
            "",
            f"- status: {result['consciousness_equivalence_countermodel_status']}",
            f"- countermodels_generated: {result['countermodels_generated']}",
            f"- countermodel_count: {result['countermodel_metrics']['countermodel_count']}",
            f"- countermodel_coverage_score: {result['countermodel_metrics']['countermodel_coverage_score']}",
            "- consciousness_proven: False",
            "- phenomenology_undetermined: True",
        ]
        md_text = "\n".join(md) + "\n"
        md_path.write_text(md_text, encoding="utf-8")
        latest_md.write_text(md_text, encoding="utf-8")

        prom = [
            f"ap6_countermodel_coverage_score {result['countermodel_metrics']['countermodel_coverage_score']}",
            f"ap6_countermodel_count {result['countermodel_metrics']['countermodel_count']}",
            f"ap6_countermodels_generated {1 if result['countermodels_generated'] else 0}",
            "ap6_consciousness_proven 0",
        ]
        prom_text = "\n".join(prom) + "\n"
        prom_path.write_text(prom_text, encoding="utf-8")
        latest_prom.write_text(prom_text, encoding="utf-8")

        return {
            "json_path": str(json_path),
            "latest_json_path": str(latest_json),
            "markdown_path": str(md_path),
            "latest_markdown_path": str(latest_md),
            "prometheus_path": str(prom_path),
            "latest_prometheus_path": str(latest_prom),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        ap2 = self._load_ap2(inputs)
        ap3 = self._load_ap3(inputs)
        ap4 = self._load_ap4(inputs)
        ap5 = self._load_ap5(inputs)

        component_scores = self._component_scores(ap2)
        mapping_supported = self._mapping_supported(ap3)
        sufficiency_supported = self._sufficiency_supported(ap4)
        necessity_supported = self._necessity_supported(ap5)
        countermodels = self._countermodels(component_scores, mapping_supported, sufficiency_supported, necessity_supported)

        strengths = [self._clamp(cm.get("countermodel_strength", 0.0)) for cm in countermodels]
        dependency_scores = [
            component_scores.get("rf_star_defined", 0.0),
            1.0 if mapping_supported else 0.0,
            1.0 if sufficiency_supported else 0.0,
            1.0 if necessity_supported else 0.0,
            component_scores.get("epistemic_guard", 0.0),
        ]
        dependency_readiness = sum(dependency_scores) / len(dependency_scores)
        countermodel_coverage_score = self._clamp((sum(strengths) / len(strengths) + dependency_readiness) / 2.0)
        countermodels_generated = len(countermodels) >= 5 and dependency_readiness >= 0.8 and component_scores.get("epistemic_guard", 0.0) >= 1.0
        status = "CONSCIOUSNESS_EQUIVALENCE_COUNTERMODELS_GENERATED" if countermodels_generated else "CONSCIOUSNESS_EQUIVALENCE_COUNTERMODELS_INCOMPLETE"
        failed = []
        if component_scores.get("rf_star_defined", 0.0) < 1.0:
            failed.append("rf_star_definition_anchor_missing")
        if not mapping_supported:
            failed.append("property_mapping_missing")
        if not sufficiency_supported:
            failed.append("sufficiency_support_missing")
        if not necessity_supported:
            failed.append("necessity_support_missing")
        if component_scores.get("epistemic_guard", 0.0) < 1.0:
            failed.append("epistemic_guard_failed")

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "consciousness_equivalence_countermodel_status": status,
            "countermodels_generated": countermodels_generated,
            "functional_countermodels_supported": countermodels_generated,
            "countermodels": countermodels,
            "countermodel_metrics": {
                "countermodel_count": float(len(countermodels)),
                "countermodel_coverage_score": countermodel_coverage_score,
                "mean_countermodel_strength": sum(strengths) / len(strengths),
                "dependency_readiness_score": dependency_readiness,
                "epistemic_guard_score": component_scores.get("epistemic_guard", 0.0),
            },
            "failed_conditions": failed,
            "component_scores": component_scores,
            "dependency_status": {
                "ap2_rf_star_defined": component_scores.get("rf_star_defined", 0.0) >= 1.0,
                "ap3_mapping_supported": mapping_supported,
                "ap4_sufficiency_supported": sufficiency_supported,
                "ap5_necessity_supported": necessity_supported,
            },
            "property_domains": self._property_domains(),
            "public_schema_version": self.public_schema_version,
            "interfaces_public": [
                "ConsciousnessEquivalenceCountermodelGenerator.step(inputs=None, persist=True)",
                "result['consciousness_equivalence_countermodel_status']",
                "result['countermodels_generated']",
                "result['countermodels']",
                "result['countermodel_metrics']",
                "result['property_domains']",
                "result['epistemic_status']",
            ],
            "structures_de_donnees": {
                "countermodels": "list[dict]",
                "countermodel_metrics": "dict[str,float]",
                "component_scores": "dict[str,float]",
                "dependency_status": "dict[str,bool]",
                "property_domains": "dict[str,list[str]]",
                "epistemic_status": "dict[str,bool|str]",
            },
            "metrics_produced": [
                "countermodel_count",
                "countermodel_coverage_score",
                "mean_countermodel_strength",
                "dependency_readiness_score",
                "epistemic_guard_score",
            ],
            "conditions_echec": [
                "rf_star_definition_anchor_missing",
                "property_mapping_missing",
                "sufficiency_support_missing",
                "necessity_support_missing",
                "epistemic_guard_failed",
            ],
            "epistemic_status": {
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_undetermined": True,
                "functional_conclusion_only": True,
                "phenomenological_equivalence_certified": False,
                "phenomenological_consciousness_certified": False,
                "consciousness_as_rf_equivalence_claimed": False,
                "countermodels_are_functional_formal_only": True,
                "claim_scope": "functional_formal_countermodel_generation_only",
                "consciousness_equivalence_status": "not_checked_until_AP8_AP10",
                "empirical_independent_evidence_required": True,
            },
            "axis_position": {
                "axis": "AP — Consciousness as Self-Generated Reference Frame",
                "current_step": "AP6",
                "previous_step": "AP5",
                "next_step": "AP7",
            },
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "phenomenological_equivalence_certified": False,
            "phenomenological_consciousness_certified": False,
            "consciousness_as_rf_equivalence_claimed": False,
        }
        if persist:
            result["persistence"] = self._persist(result)
        return result
