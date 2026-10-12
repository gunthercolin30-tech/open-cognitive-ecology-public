from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ConsciousnessEquivalenceTheoremChecker:
    """AP8 — functional theorem checker for CONSCIOUSNESS ⇔ RF*.

    The module checks whether the AP2→AP7 functional chain supports a strictly
    formal/functional equivalence theorem candidate. It does not prove real
    consciousness, qualia, subjectivity, ontology, or phenomenology.
    """

    primitive = "CONSCIOUSNESS_EQUIVALENCE_THEOREM_CHECKER"
    step_id = "AP8"
    public_schema_version = "AP8.consciousness_equivalence_theorem_checker.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "ap_consciousness_as_rf" / "AP8_consciousness_equivalence_theorem_checker"

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
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _load_module_result(
        self,
        inputs: dict[str, Any],
        key: str,
        class_path: tuple[str, str],
        latest: str,
        fallback: dict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(inputs.get(key), dict):
            return inputs[key]
        module_name, class_name = class_path
        try:
            mod = __import__(module_name, fromlist=[class_name])
            cls = getattr(mod, class_name)
            r = cls().step(persist=False)
            if isinstance(r, dict) and r:
                return r
        except Exception as exc:
            latest_data = self._load_latest_json(latest)
            if latest_data:
                latest_data["fallback_source"] = f"latest_{key}_json_after_import_error"
                latest_data["load_error"] = str(exc)
                return latest_data
            d = dict(fallback)
            d["load_error"] = str(exc)
            return d
        return self._load_latest_json(latest) or fallback

    def _context(self, inputs: dict[str, Any]) -> dict[str, Any]:
        return {
            "ap2": self._load_module_result(inputs, "ap2", ("ontology.rf_star_definition_engine", "RFStarDefinitionEngine"), "ap_consciousness_as_rf/AP2_rf_star_definition_engine/latest_rf_star_definition_engine.json", {"rf_star_defined": False, "component_scores": {}}),
            "ap3": self._load_module_result(inputs, "ap3", ("ontology.consciousness_rf_property_mapping", "ConsciousnessRFPropertyMapping"), "ap_consciousness_as_rf/AP3_consciousness_rf_property_mapping/latest_consciousness_rf_property_mapping.json", {"mapping_completed": False, "mapping_metrics": {}}),
            "ap4": self._load_module_result(inputs, "ap4", ("ontology.rf_star_sufficiency_checker", "RFStarSufficiencyChecker"), "ap_consciousness_as_rf/AP4_rf_star_sufficiency_checker/latest_rf_star_sufficiency_checker.json", {"functional_sufficiency_supported": False, "sufficiency_metrics": {}}),
            "ap5": self._load_module_result(inputs, "ap5", ("ontology.rf_star_necessity_checker", "RFStarNecessityChecker"), "ap_consciousness_as_rf/AP5_rf_star_necessity_checker/latest_rf_star_necessity_checker.json", {"functional_necessity_supported": False, "necessity_metrics": {}}),
            "ap6": self._load_module_result(inputs, "ap6", ("ontology.consciousness_equivalence_countermodel_generator", "ConsciousnessEquivalenceCountermodelGenerator"), "ap_consciousness_as_rf/AP6_consciousness_equivalence_countermodel_generator/latest_consciousness_equivalence_countermodel_generator.json", {"countermodels_generated": False, "countermodel_metrics": {}}),
            "ap7": self._load_module_result(inputs, "ap7", ("ontology.zombie_under_rf_equivalence_analyzer", "ZombieUnderRFEquivalenceAnalyzer"), "ap_consciousness_as_rf/AP7_zombie_under_rf_equivalence_analyzer/latest_zombie_under_rf_equivalence_analyzer.json", {"zombie_rf_equivalence_analyzed": False, "zombie_analysis_metrics": {}}),
        }

    def _truth(self, d: dict[str, Any], bool_key: str, status_key: str, expected: str) -> float:
        return 1.0 if d.get(bool_key) is True or d.get(status_key) == expected else 0.0

    def _guard_score(self, *items: dict[str, Any]) -> float:
        ok = True
        for d in items:
            epi = d.get("epistemic_status", {}) if isinstance(d.get("epistemic_status"), dict) else {}
            ok = ok and d.get("consciousness_proven", epi.get("consciousness_proven", False)) is False
            ok = ok and d.get("qualia_proven", epi.get("qualia_proven", False)) is False
            ok = ok and d.get("subjectivity_proven", epi.get("subjectivity_proven", False)) is False
            ok = ok and d.get("phenomenology_undetermined", epi.get("phenomenology_undetermined", True)) is True
            ok = ok and d.get("functional_conclusion_only", epi.get("functional_conclusion_only", True)) is True
        return 1.0 if ok else 0.0

    def _build_theorem(self, ctx: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, float], list[str]]:
        ap2, ap3, ap4, ap5, ap6, ap7 = (ctx[f"ap{i}"] for i in range(2, 8))

        rf_star_definition = self._truth(ap2, "rf_star_defined", "rf_star_definition_status", "RF_STAR_DEFINED")
        property_mapping = self._truth(ap3, "mapping_completed", "consciousness_rf_property_mapping_status", "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED")
        sufficiency = self._truth(ap4, "functional_sufficiency_supported", "rf_star_sufficiency_status", "RF_STAR_SUFFICIENCY_CHECKED")
        necessity = self._truth(ap5, "functional_necessity_supported", "rf_star_necessity_status", "RF_STAR_NECESSITY_CHECKED")
        countermodels = self._truth(ap6, "countermodels_generated", "consciousness_equivalence_countermodel_status", "CONSCIOUSNESS_EQUIVALENCE_COUNTERMODELS_GENERATED")
        zombie_analysis = self._truth(ap7, "zombie_rf_equivalence_analyzed", "zombie_rf_equivalence_status", "ZOMBIE_RF_EQUIVALENCE_ANALYZED")
        epistemic_guard = self._guard_score(ap2, ap3, ap4, ap5, ap6, ap7)

        suff_score = self._clamp((ap4.get("sufficiency_metrics") or {}).get("sufficiency_score", sufficiency)) if isinstance(ap4.get("sufficiency_metrics"), dict) else sufficiency
        nec_score = self._clamp((ap5.get("necessity_metrics") or {}).get("necessity_score", necessity)) if isinstance(ap5.get("necessity_metrics"), dict) else necessity
        cm_score = self._clamp((ap6.get("countermodel_metrics") or {}).get("countermodel_coverage_score", countermodels)) if isinstance(ap6.get("countermodel_metrics"), dict) else countermodels
        zb_score = self._clamp((ap7.get("zombie_analysis_metrics") or {}).get("zombie_analysis_score", zombie_analysis)) if isinstance(ap7.get("zombie_analysis_metrics"), dict) else zombie_analysis

        checks = [
            ("AP8-T01", "rf_star_definition", 1.0, 0.13, rf_star_definition),
            ("AP8-T02", "consciousness_rf_property_mapping", 1.0, 0.13, property_mapping),
            ("AP8-T03", "functional_sufficiency", 0.8, 0.14, suff_score),
            ("AP8-T04", "functional_necessity", 0.8, 0.14, nec_score),
            ("AP8-T05", "countermodel_coverage", 0.8, 0.13, cm_score),
            ("AP8-T06", "zombie_rf_analysis", 0.8, 0.13, zb_score),
            ("AP8-T07", "biconditional_functional_support", 0.8, 0.10, min(suff_score, nec_score)),
            ("AP8-T08", "epistemic_guard", 1.0, 0.10, epistemic_guard),
        ]
        criteria: list[dict[str, Any]] = []
        failed: list[str] = []
        for cid, name, threshold, weight, score in checks:
            score = self._clamp(score)
            passed = score >= threshold
            if not passed:
                failed.append(f"{name}_below_threshold")
            criteria.append({
                "criterion_id": cid,
                "name": name,
                "threshold": threshold,
                "weight": weight,
                "score": score,
                "passed": passed,
                "interpretation": "functional_formal_theorem_indicator_only",
            })
        theorem_score = sum(c["score"] * c["weight"] for c in criteria)
        pass_rate = sum(1 for c in criteria if c["passed"]) / max(1, len(criteria))
        metrics = {
            "theorem_support_score": self._clamp(theorem_score),
            "criteria_pass_rate": self._clamp(pass_rate),
            "minimum_criterion_score": self._clamp(min(c["score"] for c in criteria)),
            "sufficiency_support_score": suff_score,
            "necessity_support_score": nec_score,
            "countermodel_coverage_score": cm_score,
            "zombie_analysis_score": zb_score,
            "epistemic_guard_score": epistemic_guard,
        }
        return criteria, metrics, failed

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"consciousness_equivalence_theorem_checker_{ts}"
        json_path = self.out_dir / f"{base}.json"
        latest_json = self.out_dir / "latest_consciousness_equivalence_theorem_checker.json"
        md_path = self.out_dir / f"{base}.md"
        latest_md = self.out_dir / "latest_consciousness_equivalence_theorem_checker.md"
        prom_path = self.out_dir / f"{base}.prom"
        latest_prom = self.out_dir / "latest_consciousness_equivalence_theorem_checker.prom"

        serializable = dict(result)
        serializable.pop("persistence", None)
        text = json.dumps(serializable, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text, encoding="utf-8")
        latest_json.write_text(text, encoding="utf-8")

        md = [
            "# AP8 — consciousness_equivalence_theorem_checker",
            "",
            f"Status: `{result['consciousness_equivalence_theorem_status']}`",
            f"Theorem support score: `{result['theorem_metrics']['theorem_support_score']:.6f}`",
            "",
            "Conclusion: functional/formal theorem check only. No consciousness, qualia, subjectivity, or phenomenology is proven.",
        ]
        md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        latest_md.write_text("\n".join(md) + "\n", encoding="utf-8")

        prom_lines = [
            f"ap8_theorem_support_score {result['theorem_metrics']['theorem_support_score']}",
            f"ap8_criteria_pass_rate {result['theorem_metrics']['criteria_pass_rate']}",
            f"ap8_epistemic_guard_score {result['theorem_metrics']['epistemic_guard_score']}",
            f"ap8_theorem_checked {1 if result['theorem_checked'] else 0}",
        ]
        prom_path.write_text("\n".join(prom_lines) + "\n", encoding="utf-8")
        latest_prom.write_text("\n".join(prom_lines) + "\n", encoding="utf-8")

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
        ctx = self._context(inputs)
        criteria, metrics, failed = self._build_theorem(ctx)
        theorem_checked = not failed
        status = "CONSCIOUSNESS_EQUIVALENCE_THEOREM_CHECKED" if theorem_checked else "CONSCIOUSNESS_EQUIVALENCE_THEOREM_INCOMPLETE"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "consciousness_equivalence_theorem_status": status,
            "theorem_checked": theorem_checked,
            "functional_theorem_supported": theorem_checked,
            "consciousness_as_rf_theorem_proven": False,
            "theorem_statement": "CONSCIOUSNESS ⇔ RF* is checked only as a functional/formal equivalence candidate.",
            "theorem_criteria": criteria,
            "theorem_metrics": metrics,
            "failed_conditions": failed,
            "property_domains": {
                "functional_properties": ["rf_star_functional_biconditional", "sufficiency_and_necessity_support", "countermodel_boundedness", "functional_theorem_candidate_only"],
                "formal_properties": ["criterion_threshold_matrix", "weighted_theorem_support_score", "deterministic_public_schema"],
                "ontological_properties": ["formal_identity_candidate", "no_ontological_consciousness_proof"],
                "phenomenological_properties": ["not_proven", "phenomenology_undetermined", "empirical_independent_evidence_required"],
            },
            "public_schema_version": self.public_schema_version,
            "interfaces_public": [
                "ConsciousnessEquivalenceTheoremChecker.step(inputs=None, persist=True)",
                "result['consciousness_equivalence_theorem_status']",
                "result['theorem_checked']",
                "result['theorem_criteria']",
                "result['theorem_metrics']",
                "result['property_domains']",
                "result['epistemic_status']",
            ],
            "structures_de_donnees": {
                "theorem_criteria": "list[dict]",
                "theorem_metrics": "dict[str,float]",
                "property_domains": "dict[str,list[str]]",
                "epistemic_status": "dict[str,bool|str]",
            },
            "metrics_produced": list(metrics.keys()),
            "conditions_echec": [
                "rf_star_definition_below_threshold",
                "consciousness_rf_property_mapping_below_threshold",
                "functional_sufficiency_below_threshold",
                "functional_necessity_below_threshold",
                "countermodel_coverage_below_threshold",
                "zombie_rf_analysis_below_threshold",
                "biconditional_functional_support_below_threshold",
                "epistemic_guard_below_threshold",
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
                "consciousness_as_rf_theorem_proven": False,
                "claim_scope": "functional_formal_theorem_check_only",
                "consciousness_equivalence_status": "not_resolved_until_AP9_AP10",
                "empirical_independent_evidence_required": True,
            },
            "axis_position": {
                "axis": "AP — Consciousness as Self-Generated Reference Frame",
                "current_step": "AP8",
                "previous_step": "AP7",
                "next_step": "AP9",
            },
            "timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
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
