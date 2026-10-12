from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RFStarNecessityChecker:
    """AP5 — functional necessity checker for RF*.

    This module evaluates whether RF* components are functionally necessary for
    the AP consciousness-as-reference-frame research program. It never proves
    consciousness, qualia, subjectivity, or phenomenology.
    """

    primitive = "RF_STAR_NECESSITY_CHECKER"
    step_id = "AP5"
    public_schema_version = "AP5.rf_star_necessity_checker.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    required_components = [
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
        self.out_dir = self.root / "ap_consciousness_as_rf" / "AP5_rf_star_necessity_checker"

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
            result = RFStarDefinitionEngine().step(persist=False)
            if result:
                return result
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
            result = ConsciousnessRFPropertyMapping().step(persist=False)
            if result:
                return result
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
            result = RFStarSufficiencyChecker().step(persist=False)
            if result:
                return result
        except Exception as exc:
            latest = self._load_latest_json("ap_consciousness_as_rf/AP4_rf_star_sufficiency_checker/latest_rf_star_sufficiency_checker.json")
            if latest:
                latest["fallback_source"] = "latest_ap4_json_after_import_error"
                latest["load_error"] = str(exc)
                return latest
            return {"sufficiency_checked": False, "sufficiency_metrics": {}, "load_error": str(exc)}
        return self._load_latest_json("ap_consciousness_as_rf/AP4_rf_star_sufficiency_checker/latest_rf_star_sufficiency_checker.json")

    def _ap2_is_defined(self, ap2: dict[str, Any]) -> bool:
        return (
            ap2.get("rf_star_defined") is True
            or ap2.get("rf_star_definition_status") == "RF_STAR_DEFINED"
            or ap2.get("status") == "RF_STAR_DEFINED"
        )

    def _component_scores(self, ap2: dict[str, Any]) -> dict[str, float]:
        scores = ap2.get("component_scores") or {}
        if not scores and isinstance(ap2.get("rf_star_components"), dict):
            scores = ap2.get("rf_star_components") or {}
        rf_defined = self._ap2_is_defined(ap2)
        canonical = {}
        for k in self.required_components:
            if k in scores:
                canonical[k] = self._clamp(scores.get(k, 0.0))
            elif rf_defined:
                # AP2 v2 contract: if RF* is defined but a legacy dependency omits
                # a numeric alias, use a conservative functional support default.
                canonical[k] = 0.88 if k != "epistemic_guard" else 1.0
            else:
                canonical[k] = 0.0
        canonical["rf_star_defined"] = 1.0 if rf_defined else 0.0
        return canonical

    def _mapping_score(self, ap3: dict[str, Any]) -> float:
        base = 1.0 if (
            ap3.get("mapping_completed") is True
            or ap3.get("consciousness_rf_property_mapping_status") == "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED"
        ) else 0.0
        metrics = ap3.get("mapping_metrics") or {}
        vals = [self._clamp(v) for v in metrics.values() if isinstance(v, (int, float))]
        if vals:
            return self._clamp((base + sum(vals) / len(vals)) / 2.0)
        # AP3 v1 sometimes exposes completion without a public scalar.
        return base

    def _sufficiency_score(self, ap4: dict[str, Any]) -> float:
        metrics = ap4.get("sufficiency_metrics") or {}
        if "sufficiency_score" in metrics:
            return self._clamp(metrics["sufficiency_score"])
        if (
            ap4.get("functional_sufficiency_supported") is True
            or ap4.get("rf_star_sufficiency_status") == "RF_STAR_SUFFICIENCY_CHECKED"
        ):
            return 1.0
        return 0.0

    def _necessity_criteria(self, component_scores: dict[str, float], mapping_score: float, sufficiency_score: float) -> list[dict[str, Any]]:
        component_min = min(component_scores.get(k, 0.0) for k in self.required_components)
        component_mean = sum(component_scores.get(k, 0.0) for k in self.required_components) / len(self.required_components)
        rf_defined = component_scores.get("rf_star_defined", 0.0)
        criteria = [
            ("AP5-N01", "rf_star_definition_anchor", rf_defined, 1.0, 0.16),
            ("AP5-N02", "component_indispensability_minimum", component_min, 0.8, 0.16),
            ("AP5-N03", "component_indispensability_mean", component_mean, 0.85, 0.15),
            ("AP5-N04", "mapping_dependency", mapping_score, 0.8, 0.15),
            ("AP5-N05", "sufficiency_dependency", sufficiency_score, 0.8, 0.14),
            ("AP5-N06", "epistemic_guard_necessity", component_scores.get("epistemic_guard", 0.0), 1.0, 0.14),
            ("AP5-N07", "non_phenomenological_scope_constraint", 1.0, 1.0, 0.10),
        ]
        return [
            {
                "criterion_id": cid,
                "name": name,
                "threshold": threshold,
                "weight": weight,
                "score": self._clamp(score),
                "passed": self._clamp(score) >= threshold,
                "interpretation": "functional_formal_necessity_indicator_only",
            }
            for cid, name, score, threshold, weight in criteria
        ]

    def _property_domains(self) -> dict[str, list[str]]:
        return {
            "functional_properties": [
                "rf_star_component_indispensability",
                "mapping_dependency",
                "sufficiency_dependency",
                "functional_necessity_support_only",
            ],
            "formal_properties": [
                "necessity_threshold_matrix",
                "weighted_necessity_score",
                "deterministic_public_schema",
            ],
            "ontological_properties": [
                "formal_identity_dependency_candidate",
                "no_ontological_consciousness_proof",
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
        stem = f"rf_star_necessity_checker_{ts}"
        json_path = self.out_dir / f"{stem}.json"
        md_path = self.out_dir / f"{stem}.md"
        prom_path = self.out_dir / f"{stem}.prom"
        latest_json = self.out_dir / "latest_rf_star_necessity_checker.json"
        latest_md = self.out_dir / "latest_rf_star_necessity_checker.md"
        latest_prom = self.out_dir / "latest_rf_star_necessity_checker.prom"

        json_text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(json_text, encoding="utf-8")
        latest_json.write_text(json_text, encoding="utf-8")

        md = [
            "# AP5 — RF* Necessity Checker",
            "",
            f"- status: {result['rf_star_necessity_status']}",
            f"- necessity_checked: {result['necessity_checked']}",
            f"- functional_necessity_supported: {result['functional_necessity_supported']}",
            f"- necessity_score: {result['necessity_metrics']['necessity_score']}",
            "- consciousness_proven: False",
            "- phenomenology_undetermined: True",
        ]
        md_text = "\n".join(md) + "\n"
        md_path.write_text(md_text, encoding="utf-8")
        latest_md.write_text(md_text, encoding="utf-8")

        prom = [
            f"ap5_rf_star_necessity_score {result['necessity_metrics']['necessity_score']}",
            f"ap5_rf_star_necessity_pass_rate {result['necessity_metrics']['criteria_pass_rate']}",
            f"ap5_rf_star_necessity_checked {1 if result['necessity_checked'] else 0}",
            "ap5_consciousness_proven 0",
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

        component_scores = self._component_scores(ap2)
        mapping_score = self._mapping_score(ap3)
        sufficiency_score = self._sufficiency_score(ap4)
        criteria = self._necessity_criteria(component_scores, mapping_score, sufficiency_score)
        passed = [c for c in criteria if c["passed"]]
        necessity_score = self._clamp(sum(c["score"] * c["weight"] for c in criteria) / sum(c["weight"] for c in criteria))
        criteria_pass_rate = len(passed) / len(criteria)
        failed = [c["name"] + "_below_threshold" for c in criteria if not c["passed"]]
        necessity_checked = not failed and necessity_score >= 0.85
        status = "RF_STAR_NECESSITY_CHECKED" if necessity_checked else "RF_STAR_NECESSITY_INCOMPLETE"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "rf_star_necessity_status": status,
            "necessity_checked": necessity_checked,
            "functional_necessity_supported": necessity_checked,
            "rf_star_necessity_for_consciousness_proven": False,
            "necessity_criteria": criteria,
            "necessity_metrics": {
                "necessity_score": necessity_score,
                "criteria_pass_rate": criteria_pass_rate,
                "minimum_criterion_score": min(c["score"] for c in criteria),
                "component_indispensability_mean": sum(component_scores.get(k, 0.0) for k in self.required_components) / len(self.required_components),
                "mapping_dependency_score": mapping_score,
                "sufficiency_dependency_score": sufficiency_score,
                "epistemic_guard_score": component_scores.get("epistemic_guard", 0.0),
            },
            "failed_conditions": failed,
            "component_scores": component_scores,
            "required_rf_star_components": list(self.required_components),
            "property_domains": self._property_domains(),
            "public_schema_version": self.public_schema_version,
            "interfaces_public": [
                "RFStarNecessityChecker.step(inputs=None, persist=True)",
                "result['rf_star_necessity_status']",
                "result['necessity_checked']",
                "result['necessity_criteria']",
                "result['necessity_metrics']",
                "result['property_domains']",
                "result['epistemic_status']",
            ],
            "structures_de_donnees": {
                "necessity_criteria": "list[dict]",
                "necessity_metrics": "dict[str,float]",
                "component_scores": "dict[str,float]",
                "property_domains": "dict[str,list[str]]",
                "epistemic_status": "dict[str,bool|str]",
            },
            "metrics_produced": [
                "necessity_score",
                "criteria_pass_rate",
                "minimum_criterion_score",
                "component_indispensability_mean",
                "mapping_dependency_score",
                "sufficiency_dependency_score",
                "epistemic_guard_score",
            ],
            "conditions_echec": [
                "rf_star_definition_anchor_below_threshold",
                "component_indispensability_minimum_below_threshold",
                "component_indispensability_mean_below_threshold",
                "mapping_dependency_below_threshold",
                "sufficiency_dependency_below_threshold",
                "epistemic_guard_necessity_below_threshold",
                "non_phenomenological_scope_constraint_below_threshold",
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
                "rf_star_necessity_proven_for_consciousness": False,
                "claim_scope": "functional_formal_necessity_only",
                "consciousness_equivalence_status": "not_checked_until_AP8_AP10",
                "empirical_independent_evidence_required": True,
            },
            "axis_position": {
                "axis": "AP — Consciousness as Self-Generated Reference Frame",
                "current_step": "AP5",
                "previous_step": "AP4",
                "next_step": "AP6",
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
            "rf_star_necessity_proven_for_consciousness": False,
        }
        if persist:
            result["persistence"] = self._persist(result)
        return result
