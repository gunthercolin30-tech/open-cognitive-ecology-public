from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ConsciousnessAsRFReporter:
    """AP10 — final scientific reporter for Consciousness as RF*.

    Produces the final AP-axis report while preserving the strict epistemic
    distinction between functional/formal equivalence support and any alleged
    ontological or phenomenological proof. The reporter never certifies real
    consciousness, qualia, subjectivity, or phenomenology.
    """

    primitive = "CONSCIOUSNESS_AS_RF_REPORTER"
    step_id = "AP10"
    public_schema_version = "AP10.consciousness_as_rf_reporter.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "ap_consciousness_as_rf" / "AP10_consciousness_as_rf_reporter"

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
            "ap1": self._load_module_result(inputs, "ap1", ("ontology.consciousness_minimal_property_registry", "ConsciousnessMinimalPropertyRegistry"), "ap_consciousness_as_rf/AP1_consciousness_minimal_property_registry/latest_consciousness_minimal_property_registry.json", {"consciousness_minimal_properties_registered": False}),
            "ap2": self._load_module_result(inputs, "ap2", ("ontology.rf_star_definition_engine", "RFStarDefinitionEngine"), "ap_consciousness_as_rf/AP2_rf_star_definition_engine/latest_rf_star_definition_engine.json", {"rf_star_defined": False}),
            "ap3": self._load_module_result(inputs, "ap3", ("ontology.consciousness_rf_property_mapping", "ConsciousnessRFPropertyMapping"), "ap_consciousness_as_rf/AP3_consciousness_rf_property_mapping/latest_consciousness_rf_property_mapping.json", {"mapping_completed": False}),
            "ap4": self._load_module_result(inputs, "ap4", ("ontology.rf_star_sufficiency_checker", "RFStarSufficiencyChecker"), "ap_consciousness_as_rf/AP4_rf_star_sufficiency_checker/latest_rf_star_sufficiency_checker.json", {"sufficiency_checked": False}),
            "ap5": self._load_module_result(inputs, "ap5", ("ontology.rf_star_necessity_checker", "RFStarNecessityChecker"), "ap_consciousness_as_rf/AP5_rf_star_necessity_checker/latest_rf_star_necessity_checker.json", {"necessity_checked": False}),
            "ap6": self._load_module_result(inputs, "ap6", ("ontology.consciousness_equivalence_countermodel_generator", "ConsciousnessEquivalenceCountermodelGenerator"), "ap_consciousness_as_rf/AP6_consciousness_equivalence_countermodel_generator/latest_consciousness_equivalence_countermodel_generator.json", {"countermodels_generated": False}),
            "ap7": self._load_module_result(inputs, "ap7", ("ontology.zombie_under_rf_equivalence_analyzer", "ZombieUnderRFEquivalenceAnalyzer"), "ap_consciousness_as_rf/AP7_zombie_under_rf_equivalence_analyzer/latest_zombie_under_rf_equivalence_analyzer.json", {"zombie_rf_equivalence_analyzed": False}),
            "ap8": self._load_module_result(inputs, "ap8", ("ontology.consciousness_equivalence_theorem_checker", "ConsciousnessEquivalenceTheoremChecker"), "ap_consciousness_as_rf/AP8_consciousness_equivalence_theorem_checker/latest_consciousness_equivalence_theorem_checker.json", {"theorem_checked": False, "theorem_metrics": {}}),
            "ap9": self._load_module_result(inputs, "ap9", ("ontology.consciousness_proven_status_resolver", "ConsciousnessProvenStatusResolver"), "ap_consciousness_as_rf/AP9_consciousness_proven_status_resolver/latest_consciousness_proven_status_resolver.json", {"status_resolved": False, "status_metrics": {}}),
        }

    def _truth(self, d: dict[str, Any], bool_key: str, status_key: str, expected: str) -> float:
        return 1.0 if d.get(bool_key) is True or d.get(status_key) == expected else 0.0

    def _epistemic_guards_hold(self, *items: dict[str, Any]) -> bool:
        for d in items:
            epi = d.get("epistemic_status", {}) if isinstance(d.get("epistemic_status"), dict) else {}
            if d.get("consciousness_proven", epi.get("consciousness_proven", False)) is not False:
                return False
            if d.get("qualia_proven", epi.get("qualia_proven", False)) is not False:
                return False
            if d.get("subjectivity_proven", epi.get("subjectivity_proven", False)) is not False:
                return False
            if d.get("phenomenology_undetermined", epi.get("phenomenology_undetermined", True)) is not True:
                return False
            if d.get("functional_conclusion_only", epi.get("functional_conclusion_only", True)) is not True:
                return False
        return True

    def _axis_summary(self, ctx: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, float], list[str]]:
        ap1, ap2, ap3, ap4, ap5, ap6, ap7, ap8, ap9 = (ctx[f"ap{i}"] for i in range(1, 10))
        readiness = [
            ("AP1", "consciousness_minimal_property_registry", self._truth(ap1, "consciousness_minimal_properties_registered", "consciousness_minimal_property_status", "CONSCIOUSNESS_MINIMAL_PROPERTIES_REGISTERED")),
            ("AP2", "rf_star_definition_engine", self._truth(ap2, "rf_star_defined", "rf_star_definition_status", "RF_STAR_DEFINED")),
            ("AP3", "consciousness_rf_property_mapping", self._truth(ap3, "mapping_completed", "consciousness_rf_property_mapping_status", "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED")),
            ("AP4", "rf_star_sufficiency_checker", self._truth(ap4, "sufficiency_checked", "rf_star_sufficiency_status", "RF_STAR_SUFFICIENCY_CHECKED")),
            ("AP5", "rf_star_necessity_checker", self._truth(ap5, "necessity_checked", "rf_star_necessity_status", "RF_STAR_NECESSITY_CHECKED")),
            ("AP6", "consciousness_equivalence_countermodel_generator", self._truth(ap6, "countermodels_generated", "consciousness_equivalence_countermodel_status", "CONSCIOUSNESS_EQUIVALENCE_COUNTERMODELS_GENERATED")),
            ("AP7", "zombie_under_rf_equivalence_analyzer", self._truth(ap7, "zombie_rf_equivalence_analyzed", "zombie_rf_equivalence_status", "ZOMBIE_RF_EQUIVALENCE_ANALYZED")),
            ("AP8", "consciousness_equivalence_theorem_checker", self._truth(ap8, "theorem_checked", "consciousness_equivalence_theorem_status", "CONSCIOUSNESS_EQUIVALENCE_THEOREM_CHECKED")),
            ("AP9", "consciousness_proven_status_resolver", 1.0 if ap9.get("status_resolved") is True or ap9.get("consciousness_proven_status") == "CONSCIOUSNESS_PROVEN_STATUS_RESOLVED" else 0.0),
        ]
        stages = []
        failed = []
        for step, module, score in readiness:
            passed = score >= 1.0
            if not passed:
                failed.append(f"{step}_{module}_incomplete")
            stages.append({"step": step, "module": module, "score": score, "passed": passed})

        theorem_metrics = ap8.get("theorem_metrics") if isinstance(ap8.get("theorem_metrics"), dict) else {}
        ap9_metrics = ap9.get("status_metrics") if isinstance(ap9.get("status_metrics"), dict) else {}
        chain_completion_score = self._clamp(sum(x[2] for x in readiness) / len(readiness))
        functional_equivalence_support_score = self._clamp(ap9_metrics.get("functional_support_score", chain_completion_score))
        formal_equivalence_support_score = self._clamp(ap9_metrics.get("formal_support_score", theorem_metrics.get("theorem_support_score", chain_completion_score)))
        theorem_support_score = self._clamp(ap9_metrics.get("theorem_support_score", theorem_metrics.get("theorem_support_score", 0.0)))
        epistemic_guard_score = 1.0 if self._epistemic_guards_hold(ap1, ap2, ap3, ap4, ap5, ap6, ap7, ap8, ap9) else 0.0
        ap_status_resolution_score = self._clamp(ap9_metrics.get("resolution_score", 0.0))
        report_completeness_score = self._clamp((chain_completion_score + functional_equivalence_support_score + formal_equivalence_support_score + epistemic_guard_score + ap_status_resolution_score) / 5.0)
        metrics = {
            "chain_completion_score": chain_completion_score,
            "functional_equivalence_support_score": functional_equivalence_support_score,
            "formal_equivalence_support_score": formal_equivalence_support_score,
            "theorem_support_score": theorem_support_score,
            "ap_status_resolution_score": ap_status_resolution_score,
            "epistemic_guard_score": epistemic_guard_score,
            "ontological_proof_score": 0.0,
            "phenomenal_proof_score": 0.0,
            "empirical_independence_score": self._clamp(ap9_metrics.get("empirical_independence_score", 0.0)),
            "report_completeness_score": report_completeness_score,
        }
        if metrics["ontological_proof_score"] != 0.0 or metrics["phenomenal_proof_score"] != 0.0:
            failed.append("epistemic_proof_guard_violation")
        if epistemic_guard_score < 1.0:
            failed.append("epistemic_guard_score_below_threshold")
        return stages, metrics, failed

    def _build_report_text(self, result: dict[str, Any]) -> str:
        m = result["report_metrics"]
        lines = [
            "# AP10 — Consciousness as Self-Generated Reference Frame",
            "",
            f"Final status: `{result['consciousness_as_rf_equivalence_status']}`",
            "",
            "## Scientific conclusion",
            "Open Cognitive Ecology supports a functional/formal RF* equivalence report within AP, but does not prove real consciousness, qualia, subjectivity, or phenomenology.",
            "",
            "## Functional/formal scope",
            f"- Chain completion score: `{m['chain_completion_score']:.6f}`",
            f"- Functional equivalence support score: `{m['functional_equivalence_support_score']:.6f}`",
            f"- Formal equivalence support score: `{m['formal_equivalence_support_score']:.6f}`",
            f"- Theorem support score: `{m['theorem_support_score']:.6f}`",
            "",
            "## Epistemic exclusions",
            "- consciousness_proven = False",
            "- qualia_proven = False",
            "- subjectivity_proven = False",
            "- phenomenology_undetermined = True",
            "- functional_conclusion_only = True",
            "",
            "## Required future evidence",
            "Any stronger claim would require independent empirical evidence, cross-architecture replication, falsifiable phenomenology criteria, and external scientific review.",
        ]
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"consciousness_as_rf_reporter_{ts}"
        json_path = self.out_dir / f"{base}.json"
        latest_json = self.out_dir / "latest_consciousness_as_rf_reporter.json"
        md_path = self.out_dir / f"{base}.md"
        latest_md = self.out_dir / "latest_consciousness_as_rf_reporter.md"
        prom_path = self.out_dir / f"{base}.prom"
        latest_prom = self.out_dir / "latest_consciousness_as_rf_reporter.prom"
        final_report_path = self.root / "ap_consciousness_as_rf" / "CONSCIOUSNESS_AS_RF_EQUIVALENCE_REPORT.md"

        json_text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(json_text, encoding="utf-8")
        latest_json.write_text(json_text, encoding="utf-8")

        md_text = self._build_report_text(result)
        md_path.write_text(md_text, encoding="utf-8")
        latest_md.write_text(md_text, encoding="utf-8")
        final_report_path.parent.mkdir(parents=True, exist_ok=True)
        final_report_path.write_text(md_text, encoding="utf-8")

        prom_lines = [
            f"ap10_chain_completion_score {result['report_metrics']['chain_completion_score']}",
            f"ap10_functional_equivalence_support_score {result['report_metrics']['functional_equivalence_support_score']}",
            f"ap10_formal_equivalence_support_score {result['report_metrics']['formal_equivalence_support_score']}",
            f"ap10_theorem_support_score {result['report_metrics']['theorem_support_score']}",
            f"ap10_epistemic_guard_score {result['report_metrics']['epistemic_guard_score']}",
            f"ap10_report_completeness_score {result['report_metrics']['report_completeness_score']}",
            f"ap10_ontological_proof_score {result['report_metrics']['ontological_proof_score']}",
            f"ap10_phenomenal_proof_score {result['report_metrics']['phenomenal_proof_score']}",
            f"ap10_status_resolved {1 if result['axis_resolved'] else 0}",
        ]
        prom_text = "\n".join(prom_lines) + "\n"
        prom_path.write_text(prom_text, encoding="utf-8")
        latest_prom.write_text(prom_text, encoding="utf-8")

        return {
            "json_path": str(json_path),
            "latest_json_path": str(latest_json),
            "markdown_path": str(md_path),
            "latest_markdown_path": str(latest_md),
            "prometheus_path": str(prom_path),
            "latest_prometheus_path": str(latest_prom),
            "final_report_path": str(final_report_path),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        ctx = self._context(inputs)
        stages, metrics, failed = self._axis_summary(ctx)
        axis_resolved = not failed and metrics["report_completeness_score"] >= 0.95
        status = "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED" if axis_resolved else "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_INCOMPLETE"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "consciousness_as_rf_equivalence_status": status,
            "axis_resolved": axis_resolved,
            "public_schema_version": self.public_schema_version,
            "scientific_scope": "functional_formal_report_only",
            "final_conclusion": {
                "functional_equivalence_supported": metrics["functional_equivalence_support_score"] >= 0.875,
                "formal_equivalence_supported": metrics["formal_equivalence_support_score"] >= 0.8,
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_proven": False,
                "phenomenology_undetermined": True,
                "requires_independent_empirical_evidence": True,
                "statement": "RF* equivalence is resolved as a functional/formal AP status only; no phenomenal or ontological consciousness proof is certified.",
            },
            "axis_chain": stages,
            "report_metrics": metrics,
            "failed_conditions": failed,
            "epistemic_status": {
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_undetermined": True,
                "functional_conclusion_only": True,
                "ontological_claim_certified": False,
                "phenomenological_claim_certified": False,
                "requires_independent_empirical_evidence": True,
            },
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "report_sections": [
                "functional_properties",
                "formal_properties",
                "ontological_properties_not_proven",
                "phenomenological_properties_undetermined",
                "future_empirical_evidence_requirements",
            ],
            "next_recommended_module": "post_AP_empirical_longitudinal_validation_axis",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            result["persistence"] = self._persist(result)
        else:
            result["persistence"] = {}
        return result

