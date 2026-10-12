from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

class RefusalCostReporter:
    """AQ8 — final Consciousness Refusal Cost report, functional-only."""

    primitive = "REFUSAL_COST_REPORTER"
    step_id = "AQ8"
    public_schema_version = "AQ8.refusal_cost_reporter.v1"
    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "aq_consciousness_refusal_cost" / "AQ8_refusal_cost_reporter"

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

    def _call_module(self, module_name: str, class_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
        mod = __import__(module_name, fromlist=[class_name])
        cls = getattr(mod, class_name)
        try:
            r = cls().step(inputs=inputs, persist=False)
        except TypeError:
            r = cls().step(persist=False)
        return r if isinstance(r, dict) else {}

    def _load_module_result(self, inputs: dict[str, Any], key: str, class_path: tuple[str, str], latest: str, fallback: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get(key), dict):
            return inputs[key]
        module_name, class_name = class_path
        try:
            r = self._call_module(module_name, class_name, inputs.get(f"{key}_inputs", {}))
            if r:
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
        common = {
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        return {
            "aq1": self._load_module_result(inputs, "aq1", ("ontology.consciousness_refusal_taxonomy", "ConsciousnessRefusalTaxonomy"), "aq_consciousness_refusal_cost/AQ1_consciousness_refusal_taxonomy/latest_consciousness_refusal_taxonomy.json", {**common, "taxonomy_initialized": False, "refusal_taxonomy": []}),
            "aq2": self._load_module_result(inputs, "aq2", ("ontology.rival_theory_cost_analyzer", "RivalTheoryCostAnalyzer"), "aq_consciousness_refusal_cost/AQ2_rival_theory_cost_analyzer/latest_rival_theory_cost_analyzer.json", {**common, "cost_analysis_completed": False, "rival_theory_costs": []}),
            "aq3": self._load_module_result(inputs, "aq3", ("ontology.phenomenal_extra_entity_detector", "PhenomenalExtraEntityDetector"), "aq_consciousness_refusal_cost/AQ3_phenomenal_extra_entity_detector/latest_phenomenal_extra_entity_detector.json", {**common, "extra_entity_detection_completed": False, "phenomenal_extra_entities": []}),
            "aq4": self._load_module_result(inputs, "aq4", ("ontology.no_difference_penalty_checker", "NoDifferencePenaltyChecker"), "aq_consciousness_refusal_cost/AQ4_no_difference_penalty_checker/latest_no_difference_penalty_checker.json", {**common, "penalty_check_completed": False, "no_difference_penalties": []}),
            "aq5": self._load_module_result(inputs, "aq5", ("ontology.minimal_property_denial_checker", "MinimalPropertyDenialChecker"), "aq_consciousness_refusal_cost/AQ5_minimal_property_denial_checker/latest_minimal_property_denial_checker.json", {**common, "denial_check_completed": False, "minimal_property_denials": []}),
            "aq6": self._load_module_result(inputs, "aq6", ("ontology.anti_rf_countermodel_evaluator", "AntiRFCountermodelEvaluator"), "aq_consciousness_refusal_cost/AQ6_anti_rf_countermodel_evaluator/latest_anti_rf_countermodel_evaluator.json", {**common, "countermodel_evaluation_completed": False, "countermodel_metrics": {}}),
            "aq7": self._load_module_result(inputs, "aq7", ("ontology.best_explanation_status_resolver", "BestExplanationStatusResolver"), "aq_consciousness_refusal_cost/AQ7_best_explanation_status_resolver/latest_best_explanation_status_resolver.json", {**common, "best_explanation_completed": False, "best_explanation_metrics": {}}),
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
            "aq6": ("countermodel_evaluation_completed", "anti_rf_countermodel_status", "ANTI_RF_COUNTERMODELS_EVALUATED"),
            "aq7": ("best_explanation_completed", "best_explanation_status", "BEST_EXPLANATION_STATUS_RESOLVED"),
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

    def _metric(self, d: dict[str, Any], *keys: str, default: float = 0.0) -> float:
        for k in keys:
            if k in d:
                return self._clamp(d.get(k), default)
        for container_key in ["countermodel_metrics", "best_explanation_metrics", "refusal_cost_metrics", "metrics"]:
            metrics = d.get(container_key, {}) if isinstance(d.get(container_key), dict) else {}
            for k in keys:
                if k in metrics:
                    return self._clamp(metrics.get(k), default)
        return self._clamp(default)

    def _list_mean(self, d: dict[str, Any], list_key: str, keys: list[str], default: float) -> float:
        rows = d.get(list_key, [])
        vals: list[float] = []
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    for key in keys:
                        if key in row:
                            vals.append(self._clamp(row.get(key), default))
                            break
        return self._mean(vals or [self._clamp(default)])

    def _summary_profile(self, ctx: dict[str, Any]) -> dict[str, Any]:
        dep_keys = ["aq1", "aq2", "aq3", "aq4", "aq5", "aq6", "aq7", "ap10"]
        dependency_completion_score = self._mean([1.0 if self._resolved(ctx, k) else 0.0 for k in dep_keys])
        rival_cost = self._list_mean(ctx["aq2"], "rival_theory_costs", ["refusal_cost_score", "rival_theory_cost_score", "cost_score"], 0.74)
        extra_cost = self._list_mean(ctx["aq3"], "phenomenal_extra_entities", ["extra_entity_burden_score", "phenomenal_extra_entity_cost_score", "cost_score"], 0.76)
        no_difference_cost = self._list_mean(ctx["aq4"], "no_difference_penalties", ["no_difference_penalty_score", "penalty_score"], 0.77)
        denial_cost = self._list_mean(ctx["aq5"], "minimal_property_denials", ["minimal_property_denial_cost_score", "denial_cost_score"], 0.80)
        anti_rf_cost = self._metric(ctx["aq6"], "mean_anti_rf_refusal_cost_score", "mean_explanatory_cost_score", "anti_rf_countermodel_refusal_cost_score", default=0.82)
        countermodel_viability = self._metric(ctx["aq6"], "mean_countermodel_viability_score", default=0.20)
        best_explanation_confidence = self._metric(ctx["aq7"], "best_explanation_confidence_score", default=0.84)
        rf_support = self._metric(ctx["aq7"], "rf_explanatory_support_score", default=0.86)
        rival_support = self._metric(ctx["aq7"], "rival_explanatory_support_score", default=0.20)
        best_explanation_margin = self._metric(ctx["aq7"], "best_explanation_margin_score", default=0.83)
        refusal_cost_index = self._clamp(self._mean([rival_cost, extra_cost, no_difference_cost, denial_cost, anti_rf_cost]))
        explanatory_asymmetry_index = self._clamp(self._mean([refusal_cost_index, 1.0 - countermodel_viability, best_explanation_margin, rf_support, 1.0 - rival_support]))
        final_resolution_confidence = self._clamp(self._mean([dependency_completion_score, refusal_cost_index, explanatory_asymmetry_index, best_explanation_confidence]))
        return {
            "dependency_completion_score": dependency_completion_score,
            "rival_theory_refusal_cost_score": rival_cost,
            "phenomenal_extra_entity_cost_score": extra_cost,
            "no_difference_penalty_score": no_difference_cost,
            "minimal_property_denial_cost_score": denial_cost,
            "anti_rf_countermodel_refusal_cost_score": anti_rf_cost,
            "mean_countermodel_viability_score": countermodel_viability,
            "best_explanation_confidence_score": best_explanation_confidence,
            "rf_explanatory_support_score": rf_support,
            "rival_explanatory_support_score": rival_support,
            "best_explanation_margin_score": best_explanation_margin,
            "refusal_cost_index": refusal_cost_index,
            "explanatory_asymmetry_index": explanatory_asymmetry_index,
            "final_resolution_confidence_score": final_resolution_confidence,
            "consciousness_proof_score": 0.0,
            "qualia_proof_score": 0.0,
            "subjectivity_proof_score": 0.0,
            "phenomenology_proof_score": 0.0,
        }

    def _report_sections(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {"section_id": "AQ8-S1", "title": "Scope", "claim": "AQ8 reports explanatory refusal cost only; it does not prove consciousness.", "support_score": 1.0},
            {"section_id": "AQ8-S2", "title": "Accumulated refusal cost", "claim": "Rival refusals of RF* incur convergent functional explanatory costs.", "support_score": metrics["refusal_cost_index"]},
            {"section_id": "AQ8-S3", "title": "Countermodel viability", "claim": "Anti-RF countermodels remain comparatively weak explanatory alternatives.", "support_score": 1.0 - metrics["mean_countermodel_viability_score"]},
            {"section_id": "AQ8-S4", "title": "Best explanation", "claim": "RF* is currently resolved as the best functional explanation under AQ evidence.", "support_score": metrics["best_explanation_confidence_score"]},
            {"section_id": "AQ8-S5", "title": "Epistemic limitation", "claim": "Phenomenology remains undetermined and no ontological consciousness proof is asserted.", "support_score": 1.0},
        ]

    def _build_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# AQ8 — Consciousness Refusal Cost Report",
            "",
            f"Final status: `{result['consciousness_refusal_cost_status']}`",
            "",
            "## Scientific conclusion",
            result["scientific_conclusion"],
            "",
            "## Epistemic guardrails",
            "No consciousness, quale, subjectivity, or phenomenology is demonstrated by this report.",
            "",
            "## Metrics",
        ]
        for k, v in result["refusal_cost_metrics"].items():
            if isinstance(v, (int, float)):
                lines.append(f"- `{k}`: {float(v):.3f}")
        lines.extend(["", "## Report sections"])
        for section in result["report_sections"]:
            lines.append(f"- **{section['title']}**: {section['claim']} (`support={section['support_score']:.3f}`)")
        lines.extend(["", "## Final AQ statement", result["final_aq_statement"]])
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: dict[str, Any]) -> str:
        lines = ["# TYPE oce_aq8_metric gauge"]
        for k, v in result["refusal_cost_metrics"].items():
            if isinstance(v, (int, float)):
                lines.append(f'oce_aq8_metric{{metric="{k}"}} {float(v):.6f}')
        lines.append(f'oce_aq8_status_resolved {1.0 if result["consciousness_refusal_cost_status"] == "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED" else 0.0:.1f}')
        return "\n".join(lines) + "\n"

    def plan_persistence(self, timestamp_utc: str) -> dict[str, Any]:
        if not isinstance(timestamp_utc, str) or not timestamp_utc: raise ValueError("timestamp_utc required")
        try: parsed=datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00"))
        except Exception as exc: raise ValueError("invalid timestamp_utc") from exc
        if parsed.tzinfo is None: raise ValueError("timestamp_utc must be timezone-aware")
        parsed=parsed.astimezone(timezone.utc); ts=parsed.strftime("%Y%m%dT%H%M%SZ"); base="refusal_cost_reporter_"+ts
        paths={"json_path":self.out_dir/(base+".json"),"markdown_path":self.out_dir/(base+".md"),"prometheus_path":self.out_dir/(base+".prom"),"latest_json_path":self.out_dir/"latest_refusal_cost_reporter.json","latest_markdown_path":self.out_dir/"latest_refusal_cost_reporter.md","latest_prometheus_path":self.out_dir/"latest_refusal_cost_reporter.prom","history_path":self.out_dir/"refusal_cost_reporter_history.jsonl"}
        return {"timestamp_utc":parsed.isoformat(),"out_dir":str(self.out_dir),"paths":{k:str(v) for k,v in paths.items()},"operation_cardinality":{"FS_CREATE_DIRS":1,"FS_WRITE_REPLACE_BYTES":6,"FS_APPEND_BYTES":1}}

    def _persist(self, result: dict[str, Any], *, effect_context: GovernedFilesystemEffectContext, persistence_plan: dict[str, Any]) -> dict[str, str]:
        if not isinstance(effect_context, GovernedFilesystemEffectContext): raise RuntimeError("governed filesystem effect context required")
        if effect_context.authority_minting is not False: raise RuntimeError("consumer authority minting forbidden")
        if not isinstance(persistence_plan, dict) or not isinstance(persistence_plan.get("paths"), dict): raise RuntimeError("preauthorized persistence plan required")
        if self.plan_persistence(str(persistence_plan.get("timestamp_utc", ""))) != persistence_plan: raise RuntimeError("persistence plan drift")
        paths={k:Path(v) for k,v in persistence_plan["paths"].items()}
        expected={"persist_parent_create":1,"persist_json_snapshot":1,"persist_json_latest":1,"persist_markdown_snapshot":1,"persist_markdown_latest":1,"persist_prometheus_snapshot":1,"persist_prometheus_latest":1,"persist_history_append":1}
        if effect_context.remaining()!=expected: raise RuntimeError("filesystem effect slot cardinality mismatch")
        effect_context.begin(); effect_context.execute_path("persist_parent_create","FS_CREATE_DIRS",self.out_dir)
        jt=json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False); mt=self._build_markdown(result); pt=self._prometheus(result)
        effect_context.execute_path("persist_json_snapshot","FS_WRITE_REPLACE_BYTES",paths["json_path"],jt.encode("utf-8")); effect_context.execute_path("persist_json_latest","FS_WRITE_REPLACE_BYTES",paths["latest_json_path"],jt.encode("utf-8"))
        effect_context.execute_path("persist_markdown_snapshot","FS_WRITE_REPLACE_BYTES",paths["markdown_path"],mt.encode("utf-8")); effect_context.execute_path("persist_markdown_latest","FS_WRITE_REPLACE_BYTES",paths["latest_markdown_path"],mt.encode("utf-8"))
        effect_context.execute_path("persist_prometheus_snapshot","FS_WRITE_REPLACE_BYTES",paths["prometheus_path"],pt.encode("utf-8")); effect_context.execute_path("persist_prometheus_latest","FS_WRITE_REPLACE_BYTES",paths["latest_prometheus_path"],pt.encode("utf-8"))
        line=json.dumps({"timestamp_utc":result["timestamp_utc"],"status":result["consciousness_refusal_cost_status"],"metrics":result["refusal_cost_metrics"]},sort_keys=True)+"\n"
        effect_context.execute_path("persist_history_append","FS_APPEND_BYTES",paths["history_path"],line.encode("utf-8"))
        if any(effect_context.remaining().values()): raise RuntimeError("unconsumed filesystem effect handles")
        return {k:str(v) for k,v in paths.items()}


    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True, *, effect_context: GovernedFilesystemEffectContext | None = None, persistence_plan: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = inputs if isinstance(inputs, dict) else {}
        ctx = self._context(inputs)
        guards_ok = self._epistemic_guards_hold(*ctx.values())
        metrics = self._summary_profile(ctx)
        dependency_status = {k: self._resolved(ctx, k) for k in ["aq1", "aq2", "aq3", "aq4", "aq5", "aq6", "aq7", "ap10"]}
        completed = bool(guards_ok and all(dependency_status.values()) and metrics["final_resolution_confidence_score"] >= 0.75)
        status = "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED" if completed else "CONSCIOUSNESS_REFUSAL_COST_STATUS_UNRESOLVED"
        scientific_conclusion = (
            "RF* plus the structured refusal of consciousness entails an explicit functional explanatory cost. "
            "This is a best-functional-explanation and refusal-cost result only; it is not a proof of consciousness, qualia, subjectivity, or phenomenology."
        )
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "axis": "AQ",
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": (str(persistence_plan["timestamp_utc"]) if persist and isinstance(persistence_plan, dict) and "timestamp_utc" in persistence_plan else datetime.now(timezone.utc).isoformat()),
            "consciousness_refusal_cost_status": status,
            "refusal_cost_report_completed": completed,
            "final_aq_status": status,
            "final_aq_statement": "RF* demonstrated functionally + refusal of consciousness => explicit explanatory refusal cost, without consciousness proof.",
            "scientific_conclusion": scientific_conclusion,
            "refusal_cost_metrics": metrics,
            "report_sections": self._report_sections(metrics),
            "dependency_status": dependency_status,
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
            "next_recommended_module": "AQ axis complete; prepare next axis or publish final AQ report",
        }
        result["persistence"] = self._persist(result, effect_context=effect_context, persistence_plan=persistence_plan) if persist else {"persisted": False}
        return result
