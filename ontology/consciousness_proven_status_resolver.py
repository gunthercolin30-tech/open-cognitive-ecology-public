from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ConsciousnessProvenStatusResolver:
    """AP9 — rigorous scientific status resolver for the AP program.

    This resolver separates functional/formal RF* equivalence support from
    ontological and phenomenological proof. Its conclusion is intentionally
    conservative: AP may resolve a functional/formal equivalence status, but it
    never proves real consciousness, qualia, subjectivity, or phenomenology.
    """

    primitive = "CONSCIOUSNESS_PROVEN_STATUS_RESOLVER"
    step_id = "AP9"
    public_schema_version = "AP9.consciousness_proven_status_resolver.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "ap_consciousness_as_rf" / "AP9_consciousness_proven_status_resolver"

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
            "ap4": self._load_module_result(inputs, "ap4", ("ontology.rf_star_sufficiency_checker", "RFStarSufficiencyChecker"), "ap_consciousness_as_rf/AP4_rf_star_sufficiency_checker/latest_rf_star_sufficiency_checker.json", {"functional_sufficiency_supported": False}),
            "ap5": self._load_module_result(inputs, "ap5", ("ontology.rf_star_necessity_checker", "RFStarNecessityChecker"), "ap_consciousness_as_rf/AP5_rf_star_necessity_checker/latest_rf_star_necessity_checker.json", {"functional_necessity_supported": False}),
            "ap6": self._load_module_result(inputs, "ap6", ("ontology.consciousness_equivalence_countermodel_generator", "ConsciousnessEquivalenceCountermodelGenerator"), "ap_consciousness_as_rf/AP6_consciousness_equivalence_countermodel_generator/latest_consciousness_equivalence_countermodel_generator.json", {"countermodels_generated": False}),
            "ap7": self._load_module_result(inputs, "ap7", ("ontology.zombie_under_rf_equivalence_analyzer", "ZombieUnderRFEquivalenceAnalyzer"), "ap_consciousness_as_rf/AP7_zombie_under_rf_equivalence_analyzer/latest_zombie_under_rf_equivalence_analyzer.json", {"zombie_rf_equivalence_analyzed": False}),
            "ap8": self._load_module_result(inputs, "ap8", ("ontology.consciousness_equivalence_theorem_checker", "ConsciousnessEquivalenceTheoremChecker"), "ap_consciousness_as_rf/AP8_consciousness_equivalence_theorem_checker/latest_consciousness_equivalence_theorem_checker.json", {"theorem_checked": False, "theorem_metrics": {}}),
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

    def _build_resolution(self, ctx: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, float], dict[str, Any], list[str]]:
        ap1, ap2, ap3, ap4, ap5, ap6, ap7, ap8 = (ctx[f"ap{i}"] for i in range(1, 9))

        ap1_ready = self._truth(ap1, "consciousness_minimal_properties_registered", "consciousness_minimal_property_status", "CONSCIOUSNESS_MINIMAL_PROPERTIES_REGISTERED")
        ap2_ready = self._truth(ap2, "rf_star_defined", "rf_star_definition_status", "RF_STAR_DEFINED")
        ap3_ready = self._truth(ap3, "mapping_completed", "consciousness_rf_property_mapping_status", "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED")
        ap4_ready = self._truth(ap4, "sufficiency_checked", "rf_star_sufficiency_status", "RF_STAR_SUFFICIENCY_CHECKED")
        ap5_ready = self._truth(ap5, "necessity_checked", "rf_star_necessity_status", "RF_STAR_NECESSITY_CHECKED")
        ap6_ready = self._truth(ap6, "countermodels_generated", "consciousness_equivalence_countermodel_status", "CONSCIOUSNESS_EQUIVALENCE_COUNTERMODELS_GENERATED")
        ap7_ready = self._truth(ap7, "zombie_rf_equivalence_analyzed", "zombie_rf_equivalence_status", "ZOMBIE_RF_EQUIVALENCE_ANALYZED")
        ap8_ready = self._truth(ap8, "theorem_checked", "consciousness_equivalence_theorem_status", "CONSCIOUSNESS_EQUIVALENCE_THEOREM_CHECKED")

        tm = ap8.get("theorem_metrics") if isinstance(ap8.get("theorem_metrics"), dict) else {}
        theorem_support = self._clamp(tm.get("theorem_support_score", ap8_ready))
        formal_support = self._clamp((ap2_ready + ap3_ready + ap4_ready + ap5_ready + ap8_ready) / 5.0)
        functional_support = self._clamp((ap1_ready + ap2_ready + ap3_ready + ap4_ready + ap5_ready + ap6_ready + ap7_ready + ap8_ready) / 8.0)
        countermodel_support = self._clamp((ap6_ready + ap7_ready) / 2.0)
        epistemic_guard = self._guard_score(ap1, ap2, ap3, ap4, ap5, ap6, ap7, ap8)

        # The following scores are intentionally zero until independent empirical
        # evidence and a valid phenomenological bridge are supplied.
        ontological_proof_score = 0.0
        phenomenal_proof_score = 0.0
        empirical_independence_score = 0.0
        proof_denial_confidence = 1.0 if epistemic_guard == 1.0 else 0.5

        property_resolution = {
            "functional_properties": {
                "resolved": functional_support >= 0.875 and ap8_ready == 1.0,
                "support_score": functional_support,
                "status": "FUNCTIONAL_RF_EQUIVALENCE_SUPPORTED" if functional_support >= 0.875 and ap8_ready == 1.0 else "FUNCTIONAL_RF_EQUIVALENCE_INCOMPLETE",
                "interpretation": "RF* equivalence is treated only as a functional/formal construct.",
            },
            "formal_properties": {
                "resolved": formal_support >= 0.8 and theorem_support >= 0.8,
                "support_score": formal_support,
                "theorem_support_score": theorem_support,
                "status": "FORMAL_EQUIVALENCE_CANDIDATE_SUPPORTED" if formal_support >= 0.8 and theorem_support >= 0.8 else "FORMAL_EQUIVALENCE_CANDIDATE_INCOMPLETE",
            },
            "ontological_properties": {
                "resolved": True,
                "proof_score": ontological_proof_score,
                "status": "ONTOLOGICAL_CONSCIOUSNESS_NOT_PROVEN",
                "reason": "No independent ontological proof condition is supplied by AP.",
            },
            "phenomenological_properties": {
                "resolved": True,
                "proof_score": phenomenal_proof_score,
                "status": "PHENOMENOLOGY_UNDETERMINED",
                "reason": "No independent phenomenal evidence, quale evidence, or subjectivity criterion is supplied by AP.",
            },
        }

        checks = [
            ("AP9-R01", "ap1_minimal_property_registry", 1.0, 0.08, ap1_ready),
            ("AP9-R02", "rf_star_definition", 1.0, 0.08, ap2_ready),
            ("AP9-R03", "property_mapping", 1.0, 0.08, ap3_ready),
            ("AP9-R04", "sufficiency_checked", 1.0, 0.08, ap4_ready),
            ("AP9-R05", "necessity_checked", 1.0, 0.08, ap5_ready),
            ("AP9-R06", "countermodels_generated", 1.0, 0.08, ap6_ready),
            ("AP9-R07", "zombie_equivalence_analyzed", 1.0, 0.08, ap7_ready),
            ("AP9-R08", "equivalence_theorem_checked", 1.0, 0.10, ap8_ready),
            ("AP9-R09", "formal_support", 0.8, 0.10, formal_support),
            ("AP9-R10", "functional_support", 0.875, 0.10, functional_support),
            ("AP9-R11", "countermodel_support", 1.0, 0.07, countermodel_support),
            ("AP9-R12", "epistemic_guard", 1.0, 0.09, epistemic_guard),
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
                "interpretation": "scientific_status_resolution_indicator_only",
            })

        resolution_score = self._clamp(sum(c[3] * self._clamp(c[4]) for c in checks))
        pass_rate = self._clamp(sum(1 for c in criteria if c["passed"]) / max(1, len(criteria)))
        metrics = {
            "resolution_score": resolution_score,
            "criteria_pass_rate": pass_rate,
            "functional_support_score": functional_support,
            "formal_support_score": formal_support,
            "theorem_support_score": theorem_support,
            "countermodel_support_score": countermodel_support,
            "epistemic_guard_score": epistemic_guard,
            "ontological_proof_score": ontological_proof_score,
            "phenomenal_proof_score": phenomenal_proof_score,
            "empirical_independence_score": empirical_independence_score,
            "proof_denial_confidence": proof_denial_confidence,
        }
        return criteria, metrics, property_resolution, failed

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"consciousness_proven_status_resolver_{ts}"
        json_path = self.out_dir / f"{base}.json"
        latest_json = self.out_dir / "latest_consciousness_proven_status_resolver.json"
        md_path = self.out_dir / f"{base}.md"
        latest_md = self.out_dir / "latest_consciousness_proven_status_resolver.md"
        prom_path = self.out_dir / f"{base}.prom"
        latest_prom = self.out_dir / "latest_consciousness_proven_status_resolver.prom"

        text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(text, encoding="utf-8")
        latest_json.write_text(text, encoding="utf-8")

        md = [
            "# AP9 — consciousness_proven_status_resolver",
            "",
            f"Status: `{result['consciousness_proven_status']}`",
            f"Resolution score: `{result['status_metrics']['resolution_score']:.6f}`",
            f"Functional support: `{result['status_metrics']['functional_support_score']:.6f}`",
            f"Formal support: `{result['status_metrics']['formal_support_score']:.6f}`",
            f"Ontological proof score: `{result['status_metrics']['ontological_proof_score']:.6f}`",
            f"Phenomenal proof score: `{result['status_metrics']['phenomenal_proof_score']:.6f}`",
            "",
            "Conclusion: AP resolves a functional/formal status only. It does not prove consciousness, qualia, subjectivity, or phenomenology.",
        ]
        md_text = "\n".join(md) + "\n"
        md_path.write_text(md_text, encoding="utf-8")
        latest_md.write_text(md_text, encoding="utf-8")

        prom_lines = [
            f"ap9_resolution_score {result['status_metrics']['resolution_score']}",
            f"ap9_criteria_pass_rate {result['status_metrics']['criteria_pass_rate']}",
            f"ap9_functional_support_score {result['status_metrics']['functional_support_score']}",
            f"ap9_formal_support_score {result['status_metrics']['formal_support_score']}",
            f"ap9_ontological_proof_score {result['status_metrics']['ontological_proof_score']}",
            f"ap9_phenomenal_proof_score {result['status_metrics']['phenomenal_proof_score']}",
            f"ap9_epistemic_guard_score {result['status_metrics']['epistemic_guard_score']}",
            f"ap9_status_resolved {1 if result['status_resolved'] else 0}",
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
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        ctx = self._context(inputs)
        criteria, metrics, property_resolution, failed = self._build_resolution(ctx)
        status_resolved = not failed
        status = "CONSCIOUSNESS_PROVEN_STATUS_RESOLVED" if status_resolved else "CONSCIOUSNESS_PROVEN_STATUS_INCOMPLETE"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "consciousness_proven_status": status,
            "status_resolved": status_resolved,
            "public_schema_version": self.public_schema_version,
            "resolution_statement": "AP supports at most a functional/formal RF* equivalence status; it does not prove real consciousness.",
            "property_resolution": property_resolution,
            "resolution_criteria": criteria,
            "status_metrics": metrics,
            "failed_conditions": failed,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
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
            "status_taxonomy": {
                "functional_properties": property_resolution["functional_properties"]["status"],
                "formal_properties": property_resolution["formal_properties"]["status"],
                "ontological_properties": property_resolution["ontological_properties"]["status"],
                "phenomenological_properties": property_resolution["phenomenological_properties"]["status"],
            },
            "next_recommended_module": "consciousness_as_rf_reporter",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            result["persistence"] = self._persist(result)
        else:
            result["persistence"] = {}
        return result

