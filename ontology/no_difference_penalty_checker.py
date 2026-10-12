from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class NoDifferencePenaltyChecker:
    """AQ4 — checks the penalty of refusing RF* without measurable differences.

    Given AP10's functional RF* equivalence, AQ1's refusal taxonomy, AQ2's rival
    theory costs, and AQ3's extra-entity burden, this module estimates whether a
    refusal strategy adds explanatory cost while failing to specify a measurable
    functional/formal/empirical difference from RF*.

    It does not prove consciousness, qualia, subjectivity, or phenomenology.
    """

    primitive = "NO_DIFFERENCE_PENALTY_CHECKER"
    step_id = "AQ4"
    public_schema_version = "AQ4.no_difference_penalty_checker.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "aq_consciousness_refusal_cost" / "AQ4_no_difference_penalty_checker"

    @staticmethod
    def _clamp(x: Any, default: float = 0.0) -> float:
        try:
            v = float(x)
        except Exception:
            v = default
        return max(0.0, min(1.0, v))

    @staticmethod
    def _mean(values: list[float]) -> float:
        return sum(values) / max(1, len(values))

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
            "aq1": self._load_module_result(
                inputs,
                "aq1",
                ("ontology.consciousness_refusal_taxonomy", "ConsciousnessRefusalTaxonomy"),
                "aq_consciousness_refusal_cost/AQ1_consciousness_refusal_taxonomy/latest_consciousness_refusal_taxonomy.json",
                {"taxonomy_initialized": False, "refusal_taxonomy": [], "taxonomy_metrics": {}},
            ),
            "aq2": self._load_module_result(
                inputs,
                "aq2",
                ("ontology.rival_theory_cost_analyzer", "RivalTheoryCostAnalyzer"),
                "aq_consciousness_refusal_cost/AQ2_rival_theory_cost_analyzer/latest_rival_theory_cost_analyzer.json",
                {"cost_analysis_completed": False, "rival_theory_costs": [], "cost_metrics": {}},
            ),
            "aq3": self._load_module_result(
                inputs,
                "aq3",
                ("ontology.phenomenal_extra_entity_detector", "PhenomenalExtraEntityDetector"),
                "aq_consciousness_refusal_cost/AQ3_phenomenal_extra_entity_detector/latest_phenomenal_extra_entity_detector.json",
                {"extra_entity_detection_completed": False, "phenomenal_extra_entities": [], "extra_entity_metrics": {}},
            ),
            "ap10": self._load_module_result(
                inputs,
                "ap10",
                ("ontology.consciousness_as_rf_reporter", "ConsciousnessAsRFReporter"),
                "ap_consciousness_as_rf/AP10_consciousness_as_rf_reporter/latest_consciousness_as_rf_reporter.json",
                {"axis_resolved": False, "report_metrics": {}},
            ),
        }

    def _resolved(self, ctx: dict[str, Any], key: str) -> bool:
        d = ctx[key]
        if key == "ap10":
            return bool(d.get("axis_resolved") is True or d.get("consciousness_as_rf_equivalence_status") == "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED")
        if key == "aq1":
            return bool(d.get("taxonomy_initialized") is True or d.get("consciousness_refusal_taxonomy_status") == "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED")
        if key == "aq2":
            return bool(d.get("cost_analysis_completed") is True or d.get("rival_theory_cost_status") == "RIVAL_THEORY_COST_ANALYZED")
        if key == "aq3":
            return bool(d.get("extra_entity_detection_completed") is True or d.get("phenomenal_extra_entity_status") == "PHENOMENAL_EXTRA_ENTITIES_DETECTED")
        return False

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

    def _rival_index(self, ctx: dict[str, Any]) -> dict[str, dict[str, Any]]:
        items = ctx["aq2"].get("rival_theory_costs") if isinstance(ctx["aq2"].get("rival_theory_costs"), list) else []
        return {str(x.get("name") or x.get("rival_theory")): x for x in items if isinstance(x, dict)}

    def _extra_entity_index(self, ctx: dict[str, Any]) -> dict[str, dict[str, Any]]:
        items = ctx["aq3"].get("phenomenal_extra_entities") if isinstance(ctx["aq3"].get("phenomenal_extra_entities"), list) else []
        return {str(x.get("rival_theory")): x for x in items if isinstance(x, dict)}

    def _difference_penalties(self, ctx: dict[str, Any]) -> list[dict[str, Any]]:
        rival = self._rival_index(ctx)
        extra = self._extra_entity_index(ctx)
        templates = [
            {
                "penalty_id": "AQ4-P1",
                "rival_theory": "Dualism",
                "refusal_pattern": "same_functional_profile_extra_substance",
                "claimed_difference": "phenomenal substance or intrinsic property over RF*",
                "measurable_difference_score": 0.02,
                "formal_difference_score": 0.05,
                "functional_difference_score": 0.00,
                "empirical_testability_score": 0.03,
                "semantic_relabeling_risk": 0.96,
            },
            {
                "penalty_id": "AQ4-P2",
                "rival_theory": "IIT",
                "refusal_pattern": "causal_structure_without_rf_identity",
                "claimed_difference": "integrated-information identity exceeds RF* reconstruction",
                "measurable_difference_score": 0.43,
                "formal_difference_score": 0.55,
                "functional_difference_score": 0.35,
                "empirical_testability_score": 0.42,
                "semantic_relabeling_risk": 0.36,
            },
            {
                "penalty_id": "AQ4-P3",
                "rival_theory": "GWT",
                "refusal_pattern": "access_without_own_frame",
                "claimed_difference": "global access is sufficient without self-generated RF*",
                "measurable_difference_score": 0.36,
                "formal_difference_score": 0.28,
                "functional_difference_score": 0.31,
                "empirical_testability_score": 0.50,
                "semantic_relabeling_risk": 0.44,
            },
            {
                "penalty_id": "AQ4-P4",
                "rival_theory": "HOT",
                "refusal_pattern": "higher_order_report_without_rf_star",
                "claimed_difference": "higher-order representation replaces RF*",
                "measurable_difference_score": 0.33,
                "formal_difference_score": 0.26,
                "functional_difference_score": 0.29,
                "empirical_testability_score": 0.38,
                "semantic_relabeling_risk": 0.48,
            },
            {
                "penalty_id": "AQ4-P5",
                "rival_theory": "Predictive Processing",
                "refusal_pattern": "prediction_without_intrinsic_reference",
                "claimed_difference": "predictive dynamics explain presence without RF* identity",
                "measurable_difference_score": 0.45,
                "formal_difference_score": 0.40,
                "functional_difference_score": 0.34,
                "empirical_testability_score": 0.52,
                "semantic_relabeling_risk": 0.34,
            },
            {
                "penalty_id": "AQ4-P6",
                "rival_theory": "Classical Functionalism",
                "refusal_pattern": "role_equivalence_without_minimal_appearing",
                "claimed_difference": "functional role is enough while denying RF* appearing reconstruction",
                "measurable_difference_score": 0.18,
                "formal_difference_score": 0.20,
                "functional_difference_score": 0.12,
                "empirical_testability_score": 0.22,
                "semantic_relabeling_risk": 0.70,
            },
            {
                "penalty_id": "AQ4-P7",
                "rival_theory": "Eliminativism",
                "refusal_pattern": "deny_concept_without_replacement_difference",
                "claimed_difference": "consciousness talk is eliminated despite recovered minimal properties",
                "measurable_difference_score": 0.05,
                "formal_difference_score": 0.08,
                "functional_difference_score": 0.04,
                "empirical_testability_score": 0.10,
                "semantic_relabeling_risk": 0.90,
            },
        ]
        penalties = []
        for item in templates:
            name = item["rival_theory"]
            ritem = rival.get(name, {})
            eitem = extra.get(name, {})
            refusal_cost = self._clamp(ritem.get("refusal_cost_score", ritem.get("total_cost_score", 0.5)), 0.5)
            extra_burden = self._clamp(eitem.get("extra_entity_burden_score", eitem.get("parsimony_violation_score", 0.5)), 0.5)
            difference_support = self._clamp(self._mean([
                item["measurable_difference_score"],
                item["formal_difference_score"],
                item["functional_difference_score"],
                item["empirical_testability_score"],
            ]))
            no_difference_score = self._clamp(1.0 - difference_support)
            penalty_score = self._clamp(
                0.35 * no_difference_score
                + 0.25 * refusal_cost
                + 0.20 * extra_burden
                + 0.20 * item["semantic_relabeling_risk"]
            )
            classification = (
                "low_no_difference_penalty" if penalty_score < 0.35 else
                "moderate_no_difference_penalty" if penalty_score < 0.55 else
                "high_no_difference_penalty" if penalty_score < 0.75 else
                "severe_no_difference_penalty"
            )
            penalties.append({
                **item,
                "difference_support_score": difference_support,
                "no_difference_score": no_difference_score,
                "refusal_cost_score": refusal_cost,
                "extra_entity_burden_score": extra_burden,
                "no_difference_penalty_score": penalty_score,
                "penalty_classification": classification,
                "measurable_difference_demonstrated": difference_support >= 0.60,
                "consciousness_proven": False,
                "phenomenology_undetermined": True,
            })
        return penalties

    def _metrics(self, penalties: list[dict[str, Any]], ctx: dict[str, Any]) -> dict[str, float]:
        scores = [self._clamp(x["no_difference_penalty_score"]) for x in penalties]
        no_diff = [self._clamp(x["no_difference_score"]) for x in penalties]
        diff_support = [self._clamp(x["difference_support_score"]) for x in penalties]
        high = sum(1 for x in penalties if x["penalty_classification"] in {"high_no_difference_penalty", "severe_no_difference_penalty"})
        return {
            "no_difference_penalty_detection_score": 1.0 if penalties else 0.0,
            "penalty_coverage_score": self._clamp(len(penalties) / 7.0),
            "ap_equivalence_dependency_score": 1.0 if self._resolved(ctx, "ap10") else 0.0,
            "aq1_taxonomy_dependency_score": 1.0 if self._resolved(ctx, "aq1") else 0.0,
            "aq2_cost_dependency_score": 1.0 if self._resolved(ctx, "aq2") else 0.0,
            "aq3_extra_entity_dependency_score": 1.0 if self._resolved(ctx, "aq3") else 0.0,
            "mean_no_difference_penalty_score": self._clamp(self._mean(scores)),
            "max_no_difference_penalty_score": self._clamp(max(scores) if scores else 0.0),
            "mean_no_difference_score": self._clamp(self._mean(no_diff)),
            "mean_difference_support_score": self._clamp(self._mean(diff_support)),
            "high_penalty_ratio": self._clamp(high / max(1, len(penalties))),
            "ontological_proof_score": 0.0,
            "phenomenal_proof_score": 0.0,
            "consciousness_proof_score": 0.0,
        }

    def _build_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# AQ4 — No Difference Penalty Checker",
            "",
            f"Status: `{result['no_difference_penalty_status']}`",
            "",
            "## Epistemic scope",
            "This module scores explanatory penalty when RF* refusal introduces no measurable difference. It does not prove consciousness or phenomenology.",
            "",
            "## Penalties",
        ]
        for item in result["no_difference_penalties"]:
            lines.append(
                f"- `{item['penalty_id']}` — **{item['rival_theory']}**: "
                f"penalty={item['no_difference_penalty_score']:.3f}, class={item['penalty_classification']}"
            )
        lines.extend(["", "## Next AQ module", "AQ5 will check denial of recovered minimal consciousness properties."])
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"no_difference_penalty_checker_{ts}"
        json_path = self.out_dir / f"{base}.json"
        latest_json = self.out_dir / "latest_no_difference_penalty_checker.json"
        md_path = self.out_dir / f"{base}.md"
        latest_md = self.out_dir / "latest_no_difference_penalty_checker.md"
        prom_path = self.out_dir / f"{base}.prom"
        latest_prom = self.out_dir / "latest_no_difference_penalty_checker.prom"
        history_path = self.out_dir / "history.jsonl"

        payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(payload + "\n", encoding="utf-8")
        latest_json.write_text(payload + "\n", encoding="utf-8")
        md = self._build_markdown(result)
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")
        prom_lines = [f"aq4_{k} {float(v):.12g}" for k, v in result["penalty_metrics"].items()]
        prom_lines.append(f"aq4_no_difference_penalty_checked {1.0 if result['penalty_check_completed'] else 0.0}")
        prom = "\n".join(prom_lines) + "\n"
        prom_path.write_text(prom, encoding="utf-8")
        latest_prom.write_text(prom, encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as f:
            f.write(payload + "\n")
        return {
            "json_path": str(json_path),
            "latest_json_path": str(latest_json),
            "markdown_path": str(md_path),
            "latest_markdown_path": str(latest_md),
            "prometheus_path": str(prom_path),
            "latest_prometheus_path": str(latest_prom),
            "history_path": str(history_path),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        ctx = self._context(inputs)
        penalties = self._difference_penalties(ctx)
        metrics = self._metrics(penalties, ctx)
        guards_hold = self._epistemic_guards_hold(ctx["aq1"], ctx["aq2"], ctx["aq3"], ctx["ap10"])
        failed_conditions: list[str] = []
        if metrics["ap_equivalence_dependency_score"] < 1.0:
            failed_conditions.append("ap_equivalence_dependency_unresolved")
        if metrics["aq1_taxonomy_dependency_score"] < 1.0:
            failed_conditions.append("aq1_taxonomy_dependency_unresolved")
        if metrics["aq2_cost_dependency_score"] < 1.0:
            failed_conditions.append("aq2_cost_dependency_unresolved")
        if metrics["aq3_extra_entity_dependency_score"] < 1.0:
            failed_conditions.append("aq3_extra_entity_dependency_unresolved")
        if metrics["penalty_coverage_score"] < 1.0:
            failed_conditions.append("no_difference_penalty_coverage_incomplete")
        if not guards_hold:
            failed_conditions.append("epistemic_guard_violation")
        completed = not failed_conditions
        status = "NO_DIFFERENCE_PENALTY_CHECKED" if completed else "NO_DIFFERENCE_PENALTY_CHECK_INCOMPLETE"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "axis": "AQ",
            "no_difference_penalty_status": status,
            "penalty_check_completed": completed,
            "public_schema_version": self.public_schema_version,
            "scientific_scope": "explanatory_no_difference_penalty_only",
            "ap_dependency_status": "AP_RESOLVED" if metrics["ap_equivalence_dependency_score"] == 1.0 else "AP_UNRESOLVED",
            "aq1_dependency_status": "AQ1_RESOLVED" if metrics["aq1_taxonomy_dependency_score"] == 1.0 else "AQ1_UNRESOLVED",
            "aq2_dependency_status": "AQ2_RESOLVED" if metrics["aq2_cost_dependency_score"] == 1.0 else "AQ2_UNRESOLVED",
            "aq3_dependency_status": "AQ3_RESOLVED" if metrics["aq3_extra_entity_dependency_score"] == 1.0 else "AQ3_UNRESOLVED",
            "no_difference_penalties": penalties,
            "penalty_dimensions": [
                "measurable_difference_score",
                "formal_difference_score",
                "functional_difference_score",
                "empirical_testability_score",
                "semantic_relabeling_risk",
                "refusal_cost_score",
                "extra_entity_burden_score",
            ],
            "penalty_metrics": metrics,
            "failed_conditions": failed_conditions,
            "epistemic_status": {
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_undetermined": True,
                "functional_conclusion_only": True,
                "ontological_claim_certified": False,
                "phenomenological_claim_certified": False,
            },
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "next_recommended_module": "minimal_property_denial_checker",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            result["persistence"] = self._persist(result)
        else:
            result["persistence"] = {}
        return result

