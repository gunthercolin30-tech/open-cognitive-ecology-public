from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AntiRFCountermodelEvaluator:
    """AQ6 — evaluates countermodels that contest RF*.

    The evaluator measures explanatory viability, dependency support, and
    refusal cost of anti-RF countermodels. It only reports functional and
    epistemic costs. It never proves consciousness, qualia, subjectivity, or
    phenomenology.
    """

    primitive = "ANTI_RF_COUNTERMODEL_EVALUATOR"
    step_id = "AQ6"
    public_schema_version = "AQ6.anti_rf_countermodel_evaluator.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "aq_consciousness_refusal_cost" / "AQ6_anti_rf_countermodel_evaluator"

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

    def _load_module_result(self, inputs: dict[str, Any], key: str, class_path: tuple[str, str], latest: str, fallback: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get(key), dict):
            return inputs[key]
        module_name, class_name = class_path
        try:
            mod = __import__(module_name, fromlist=[class_name])
            cls = getattr(mod, class_name)
            try:
                r = cls().step(inputs=inputs.get(f"{key}_inputs", {}), persist=False)
            except TypeError:
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
        common = {"consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True}
        return {
            "aq1": self._load_module_result(inputs, "aq1", ("ontology.consciousness_refusal_taxonomy", "ConsciousnessRefusalTaxonomy"), "aq_consciousness_refusal_cost/AQ1_consciousness_refusal_taxonomy/latest_consciousness_refusal_taxonomy.json", {**common, "taxonomy_initialized": False, "refusal_taxonomy": []}),
            "aq2": self._load_module_result(inputs, "aq2", ("ontology.rival_theory_cost_analyzer", "RivalTheoryCostAnalyzer"), "aq_consciousness_refusal_cost/AQ2_rival_theory_cost_analyzer/latest_rival_theory_cost_analyzer.json", {**common, "cost_analysis_completed": False, "rival_theory_costs": []}),
            "aq3": self._load_module_result(inputs, "aq3", ("ontology.phenomenal_extra_entity_detector", "PhenomenalExtraEntityDetector"), "aq_consciousness_refusal_cost/AQ3_phenomenal_extra_entity_detector/latest_phenomenal_extra_entity_detector.json", {**common, "extra_entity_detection_completed": False, "phenomenal_extra_entities": []}),
            "aq4": self._load_module_result(inputs, "aq4", ("ontology.no_difference_penalty_checker", "NoDifferencePenaltyChecker"), "aq_consciousness_refusal_cost/AQ4_no_difference_penalty_checker/latest_no_difference_penalty_checker.json", {**common, "penalty_check_completed": False, "no_difference_penalties": []}),
            "aq5": self._load_module_result(inputs, "aq5", ("ontology.minimal_property_denial_checker", "MinimalPropertyDenialChecker"), "aq_consciousness_refusal_cost/AQ5_minimal_property_denial_checker/latest_minimal_property_denial_checker.json", {**common, "denial_check_completed": False, "minimal_property_denials": []}),
            "ap10": self._load_module_result(inputs, "ap10", ("ontology.consciousness_as_rf_reporter", "ConsciousnessAsRFReporter"), "ap_consciousness_as_rf/AP10_consciousness_as_rf_reporter/latest_consciousness_as_rf_reporter.json", {**common, "axis_resolved": False}),
        }

    def _resolved(self, ctx: dict[str, Any], key: str) -> bool:
        d = ctx[key]
        statuses = {
            "aq1": ("taxonomy_initialized", "consciousness_refusal_taxonomy_status", "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED"),
            "aq2": ("cost_analysis_completed", "rival_theory_cost_status", "RIVAL_THEORY_COST_ANALYZED"),
            "aq3": ("extra_entity_detection_completed", "phenomenal_extra_entity_status", "PHENOMENAL_EXTRA_ENTITIES_DETECTED"),
            "aq4": ("penalty_check_completed", "no_difference_penalty_status", "NO_DIFFERENCE_PENALTY_CHECKED"),
            "aq5": ("denial_check_completed", "minimal_property_denial_status", "MINIMAL_PROPERTY_DENIAL_CHECKED"),
            "ap10": ("axis_resolved", "consciousness_as_rf_equivalence_status", "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED"),
        }
        flag, status_key, status_value = statuses[key]
        return bool(d.get(flag) is True or d.get(status_key) == status_value)

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

    def _anti_rf_countermodels(self, ctx: dict[str, Any]) -> list[dict[str, Any]]:
        denial_items = ctx["aq5"].get("minimal_property_denials", []) if isinstance(ctx["aq5"].get("minimal_property_denials"), list) else []
        cost_by_theory = {str(x.get("rival_theory") or x.get("name")): self._clamp(x.get("minimal_property_denial_cost_score", x.get("refusal_cost_score", 0.55)), 0.55) for x in denial_items if isinstance(x, dict)}
        templates = [
            ("ARF1", "no_self_generated_frame_model", "RF* is treated as optional access metadata", 0.18, 0.92, 0.88, ["perspective", "identity", "minimal_appearing"]),
            ("ARF2", "external_observer_frame_model", "all apparent frame properties are outsourced to an observer", 0.22, 0.89, 0.83, ["self_generation", "non_separability", "temporal_ownness"]),
            ("ARF3", "pure_behavioral_equivalence_model", "behavioral equivalence is accepted while RF* is denied", 0.32, 0.78, 0.74, ["minimal_appearing", "qualitative_differentiation"]),
            ("ARF4", "substrate_only_intrinsic_model", "intrinsicality is assigned to substrate without RF* organization", 0.28, 0.82, 0.77, ["identity", "internal_causality", "unity"]),
            ("ARF5", "semantic_label_eliminativism", "RF* vocabulary is dismissed as an eliminable label", 0.14, 0.95, 0.90, ["property_bundle", "non_difference", "minimal_property_denial"]),
            ("ARF6", "statistical_correlation_without_frame_model", "correlations are retained while reference-frame constitution is denied", 0.40, 0.70, 0.68, ["integration", "own-frame_stability"]),
        ]
        out: list[dict[str, Any]] = []
        for cid, name, thesis, base_viability, rf_conflict, explanatory_gap, denied in templates:
            related = [v for k, v in cost_by_theory.items() if any(token in k.lower() for token in ["functional", "elimin", "dual", "gwt", "iit", "predict"])]
            prior_denial_cost = self._mean(related) if related else self._mean(list(cost_by_theory.values()) or [0.72])
            support_deficit = self._clamp((rf_conflict + explanatory_gap + prior_denial_cost) / 3.0)
            viability = self._clamp(base_viability * (1.0 - 0.35 * prior_denial_cost))
            refusal_cost = self._clamp(1.0 - viability)
            out.append({
                "countermodel_id": cid,
                "countermodel_name": name,
                "anti_rf_thesis": thesis,
                "denied_rf_properties": denied,
                "rf_conflict_score": self._clamp(rf_conflict),
                "explanatory_gap_score": self._clamp(explanatory_gap),
                "inherited_minimal_property_denial_cost": self._clamp(prior_denial_cost),
                "countermodel_viability_score": viability,
                "anti_rf_refusal_cost_score": refusal_cost,
                "support_deficit_score": support_deficit,
                "countermodel_status": "low_viability" if viability < 0.34 else "partial_viability",
                "functional_interpretation": "countermodel evaluated as a functional explanatory alternative, not as phenomenological evidence",
            })
        return out

    def _metrics(self, ctx: dict[str, Any], countermodels: list[dict[str, Any]]) -> dict[str, float]:
        viability = [self._clamp(x["countermodel_viability_score"]) for x in countermodels]
        costs = [self._clamp(x["anti_rf_refusal_cost_score"]) for x in countermodels]
        deficits = [self._clamp(x["support_deficit_score"]) for x in countermodels]
        low = sum(1 for x in countermodels if x["countermodel_status"] == "low_viability")
        dependency_scores = [1.0 if self._resolved(ctx, k) else 0.0 for k in ["aq1", "aq2", "aq3", "aq4", "aq5", "ap10"]]
        return {
            "anti_rf_countermodel_detection_score": 1.0 if countermodels else 0.0,
            "countermodel_coverage_score": self._clamp(len(countermodels) / 6.0),
            "mean_countermodel_viability_score": self._clamp(self._mean(viability)),
            "max_countermodel_viability_score": self._clamp(max(viability) if viability else 0.0),
            "mean_anti_rf_refusal_cost_score": self._clamp(self._mean(costs)),
            "max_anti_rf_refusal_cost_score": self._clamp(max(costs) if costs else 0.0),
            "mean_support_deficit_score": self._clamp(self._mean(deficits)),
            "low_viability_countermodel_ratio": self._clamp(low / max(1, len(countermodels))),
            "dependency_resolution_score": self._clamp(self._mean(dependency_scores)),
            "aq5_denial_dependency_score": 1.0 if self._resolved(ctx, "aq5") else 0.0,
            "ap10_rf_equivalence_dependency_score": 1.0 if self._resolved(ctx, "ap10") else 0.0,
            "ontological_proof_score": 0.0,
            "phenomenal_proof_score": 0.0,
            "consciousness_proof_score": 0.0,
        }

    def _build_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# AQ6 — Anti-RF Countermodel Evaluator",
            "",
            f"Status: `{result['anti_rf_countermodel_status']}`",
            "",
            "## Epistemic scope",
            "AQ6 evaluates explanatory viability and refusal cost of countermodels contesting RF*. It does not prove consciousness, qualia, subjectivity, or phenomenology.",
            "",
            "## Countermodels",
        ]
        for item in result["anti_rf_countermodels"]:
            lines.append(f"- `{item['countermodel_id']}` — **{item['countermodel_name']}**: viability={item['countermodel_viability_score']:.3f}, cost={item['anti_rf_refusal_cost_score']:.3f}, status={item['countermodel_status']}")
        lines.extend(["", "## Next AQ module", "AQ7 should resolve best-explanation status from the accumulated refusal-cost evidence."])
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: dict[str, Any]) -> str:
        lines = ["# TYPE oce_aq6_metric gauge"]
        for k, v in result["countermodel_metrics"].items():
            lines.append(f'oce_aq6_metric{{metric="{k}"}} {float(v):.6f}')
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"anti_rf_countermodel_evaluator_{ts}"
        json_path = self.out_dir / f"{base}.json"
        md_path = self.out_dir / f"{base}.md"
        prom_path = self.out_dir / f"{base}.prom"
        latest_json = self.out_dir / "latest_anti_rf_countermodel_evaluator.json"
        latest_md = self.out_dir / "latest_anti_rf_countermodel_evaluator.md"
        latest_prom = self.out_dir / "latest_anti_rf_countermodel_evaluator.prom"
        history_path = self.out_dir / "anti_rf_countermodel_evaluator_history.jsonl"
        json_text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
        md_text = self._build_markdown(result)
        prom_text = self._prometheus(result)
        for p, t in [(json_path, json_text), (latest_json, json_text), (md_path, md_text), (latest_md, md_text), (prom_path, prom_text), (latest_prom, prom_text)]:
            p.write_text(t, encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"timestamp_utc": result["timestamp_utc"], "status": result["anti_rf_countermodel_status"], "metrics": result["countermodel_metrics"]}, sort_keys=True) + "\n")
        return {"json_path": str(json_path), "markdown_path": str(md_path), "prometheus_path": str(prom_path), "latest_json_path": str(latest_json), "latest_markdown_path": str(latest_md), "latest_prometheus_path": str(latest_prom), "history_path": str(history_path)}

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs if isinstance(inputs, dict) else {}
        ctx = self._context(inputs)
        countermodels = self._anti_rf_countermodels(ctx)
        metrics = self._metrics(ctx, countermodels)
        guards_ok = self._epistemic_guards_hold(*ctx.values())
        completed = bool(countermodels) and guards_ok and metrics["dependency_resolution_score"] >= 0.80
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "axis": "AQ",
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "anti_rf_countermodel_status": "ANTI_RF_COUNTERMODELS_EVALUATED" if completed else "ANTI_RF_COUNTERMODELS_INCOMPLETE",
            "countermodel_evaluation_completed": completed,
            "anti_rf_countermodels": countermodels,
            "countermodel_metrics": metrics,
            "dependency_status": {k: self._resolved(ctx, k) for k in ["aq1", "aq2", "aq3", "aq4", "aq5", "ap10"]},
            "epistemic_guards_hold": guards_ok,
            "epistemic_status": {
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_undetermined": True,
                "functional_conclusion_only": True,
            },
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "next_recommended_module": "best_explanation_status_resolver",
        }
        result["persistence"] = self._persist(result) if persist else {"persisted": False}
        return result
