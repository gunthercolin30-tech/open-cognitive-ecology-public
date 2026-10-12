from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

class BestExplanationStatusResolver:
    """AQ7 — resolves RF* as provisional best functional explanation only."""

    primitive = "BEST_EXPLANATION_STATUS_RESOLVER"
    step_id = "AQ7"
    public_schema_version = "AQ7.best_explanation_status_resolver.v1"
    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "aq_consciousness_refusal_cost" / "AQ7_best_explanation_status_resolver"

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
            "aq6": self._load_module_result(inputs, "aq6", ("ontology.anti_rf_countermodel_evaluator", "AntiRFCountermodelEvaluator"), "aq_consciousness_refusal_cost/AQ6_anti_rf_countermodel_evaluator/latest_anti_rf_countermodel_evaluator.json", {**common, "countermodel_evaluation_completed": False, "anti_rf_countermodels": [], "countermodel_metrics": {}}),
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
        for container_key in ["countermodel_metrics", "best_explanation_metrics", "metrics"]:
            metrics = d.get(container_key, {}) if isinstance(d.get(container_key), dict) else {}
            for k in keys:
                if k in metrics:
                    return self._clamp(metrics.get(k), default)
        return self._clamp(default)

    def _evidence_profile(self, ctx: dict[str, Any]) -> dict[str, Any]:
        dep = [1.0 if self._resolved(ctx, k) else 0.0 for k in ["aq1", "aq2", "aq3", "aq4", "aq5", "aq6", "ap10"]]
        anti_rf_cost = self._metric(ctx["aq6"], "mean_anti_rf_refusal_cost_score", "mean_explanatory_cost_score", default=0.72)
        countermodel_viability = self._metric(ctx["aq6"], "mean_countermodel_viability_score", default=0.24)
        low_viability_ratio = self._metric(ctx["aq6"], "low_viability_countermodel_ratio", default=0.80)
        support_deficit = self._metric(ctx["aq6"], "mean_support_deficit_score", default=0.78)
        rival_cost = self._mean([self._clamp(x.get("refusal_cost_score", x.get("rival_theory_cost_score", 0.70)), 0.70) for x in ctx["aq2"].get("rival_theory_costs", []) if isinstance(x, dict)] or [0.70])
        extra_cost = self._mean([self._clamp(x.get("extra_entity_burden_score", x.get("phenomenal_extra_entity_cost_score", 0.70)), 0.70) for x in ctx["aq3"].get("phenomenal_extra_entities", []) if isinstance(x, dict)] or [0.70])
        no_diff_cost = self._mean([self._clamp(x.get("no_difference_penalty_score", x.get("penalty_score", 0.70)), 0.70) for x in ctx["aq4"].get("no_difference_penalties", []) if isinstance(x, dict)] or [0.70])
        denial_cost = self._mean([self._clamp(x.get("minimal_property_denial_cost_score", x.get("denial_cost_score", 0.75)), 0.75) for x in ctx["aq5"].get("minimal_property_denials", []) if isinstance(x, dict)] or [0.75])
        ap10_support = 1.0 if self._resolved(ctx, "ap10") else 0.0
        dependency_resolution_score = self._clamp(self._mean(dep))
        refusal_cost_convergence_score = self._clamp(self._mean([anti_rf_cost, rival_cost, extra_cost, no_diff_cost, denial_cost, support_deficit]))
        countermodel_weakness_score = self._clamp(self._mean([1.0 - countermodel_viability, low_viability_ratio, support_deficit]))
        rf_explanatory_support_score = self._clamp(self._mean([ap10_support, dependency_resolution_score, refusal_cost_convergence_score, countermodel_weakness_score]))
        rival_explanatory_support_score = self._clamp(self._mean([countermodel_viability, 1.0 - refusal_cost_convergence_score, 1.0 - support_deficit]))
        margin = self._clamp((rf_explanatory_support_score - rival_explanatory_support_score + 1.0) / 2.0)
        confidence = self._clamp(self._mean([rf_explanatory_support_score, margin, dependency_resolution_score, 1.0 - countermodel_viability]))
        status = "RF_STAR_CURRENTLY_BEST_FUNCTIONAL_EXPLANATION" if confidence >= 0.70 and rf_explanatory_support_score > rival_explanatory_support_score else "BEST_EXPLANATION_UNRESOLVED"
        return {
            "dependency_resolution_score": dependency_resolution_score,
            "rf_star_dependency_support_score": ap10_support,
            "rival_theory_refusal_cost_score": rival_cost,
            "phenomenal_extra_entity_cost_score": extra_cost,
            "no_difference_penalty_score": no_diff_cost,
            "minimal_property_denial_cost_score": denial_cost,
            "anti_rf_countermodel_refusal_cost_score": anti_rf_cost,
            "mean_countermodel_viability_score": countermodel_viability,
            "countermodel_weakness_score": countermodel_weakness_score,
            "refusal_cost_convergence_score": refusal_cost_convergence_score,
            "rf_explanatory_support_score": rf_explanatory_support_score,
            "rival_explanatory_support_score": rival_explanatory_support_score,
            "best_explanation_margin_score": margin,
            "best_explanation_confidence_score": confidence,
            "ontological_proof_score": 0.0,
            "phenomenal_proof_score": 0.0,
            "consciousness_proof_score": 0.0,
            "best_explanation_resolution_status": status,
        }

    def _resolution_arguments(self, profile: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {"argument_id": "AQ7-ARG1", "claim": "RF* integrates the AP equivalence result while preserving epistemic humility", "support_score": profile["rf_star_dependency_support_score"], "scope": "functional_only"},
            {"argument_id": "AQ7-ARG2", "claim": "rival theories incur accumulated refusal cost across AQ2-AQ6", "support_score": profile["refusal_cost_convergence_score"], "scope": "explanatory_cost"},
            {"argument_id": "AQ7-ARG3", "claim": "anti-RF countermodels remain weak explanatory alternatives", "support_score": profile["countermodel_weakness_score"], "scope": "countermodel_viability"},
            {"argument_id": "AQ7-ARG4", "claim": "best-explanation status is provisional and not a proof of consciousness", "support_score": 1.0, "scope": "epistemic_governance"},
        ]

    def _build_markdown(self, result: dict[str, Any]) -> str:
        lines = ["# AQ7 — Best Explanation Status Resolver", "", f"Status: `{result['best_explanation_status']}`", f"Functional resolution: `{result['functional_best_explanation_resolution']}`", "", "## Epistemic scope", "AQ7 resolves provisional best-explanation status only. It does not prove consciousness, qualia, subjectivity, or phenomenology.", "", "## Metrics"]
        for k, v in result["best_explanation_metrics"].items():
            if isinstance(v, (int, float)):
                lines.append(f"- `{k}`: {v:.3f}")
        lines.extend(["", "## Next AQ module", "AQ8 should produce the final Consciousness Refusal Cost report."])
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: dict[str, Any]) -> str:
        lines = ["# TYPE oce_aq7_metric gauge"]
        for k, v in result["best_explanation_metrics"].items():
            if isinstance(v, (int, float)):
                lines.append(f'oce_aq7_metric{{metric="{k}"}} {float(v):.6f}')
        return "\n".join(lines) + "\n"

    def plan_persistence(self, timestamp_utc: str) -> dict[str, Any]:
        if not isinstance(timestamp_utc, str) or not timestamp_utc: raise ValueError("timestamp_utc required")
        try: parsed=datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00"))
        except Exception as exc: raise ValueError("invalid timestamp_utc") from exc
        if parsed.tzinfo is None: raise ValueError("timestamp_utc must be timezone-aware")
        parsed=parsed.astimezone(timezone.utc); ts=parsed.strftime("%Y%m%dT%H%M%SZ"); base="best_explanation_status_resolver_"+ts
        paths={"json_path":self.out_dir/(base+".json"),"markdown_path":self.out_dir/(base+".md"),"prometheus_path":self.out_dir/(base+".prom"),"latest_json_path":self.out_dir/"latest_best_explanation_status_resolver.json","latest_markdown_path":self.out_dir/"latest_best_explanation_status_resolver.md","latest_prometheus_path":self.out_dir/"latest_best_explanation_status_resolver.prom","history_path":self.out_dir/"best_explanation_status_resolver_history.jsonl"}
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
        line=json.dumps({"timestamp_utc":result["timestamp_utc"],"status":result["best_explanation_status"],"metrics":result["best_explanation_metrics"]},sort_keys=True)+"\n"
        effect_context.execute_path("persist_history_append","FS_APPEND_BYTES",paths["history_path"],line.encode("utf-8"))
        if any(effect_context.remaining().values()): raise RuntimeError("unconsumed filesystem effect handles")
        return {k:str(v) for k,v in paths.items()}


    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True, *, effect_context: GovernedFilesystemEffectContext | None = None, persistence_plan: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = inputs if isinstance(inputs, dict) else {}
        ctx = self._context(inputs)
        guards_ok = self._epistemic_guards_hold(*ctx.values())
        profile = self._evidence_profile(ctx)
        best_status = str(profile["best_explanation_resolution_status"])
        completed = guards_ok and profile["dependency_resolution_score"] >= 0.85 and best_status == "RF_STAR_CURRENTLY_BEST_FUNCTIONAL_EXPLANATION"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "axis": "AQ",
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": (str(persistence_plan["timestamp_utc"]) if persist and isinstance(persistence_plan, dict) and "timestamp_utc" in persistence_plan else datetime.now(timezone.utc).isoformat()),
            "best_explanation_status": "BEST_EXPLANATION_STATUS_RESOLVED" if completed else "BEST_EXPLANATION_STATUS_UNRESOLVED",
            "functional_best_explanation_resolution": best_status,
            "best_explanation_completed": completed,
            "best_explanation_metrics": profile,
            "resolution_arguments": self._resolution_arguments(profile),
            "dependency_status": {k: self._resolved(ctx, k) for k in ["aq1", "aq2", "aq3", "aq4", "aq5", "aq6", "ap10"]},
            "epistemic_guards_hold": guards_ok,
            "epistemic_status": {"consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True},
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "next_recommended_module": "refusal_cost_reporter",
        }
        result["persistence"] = self._persist(result, effect_context=effect_context, persistence_plan=persistence_plan) if persist else {"persisted": False}
        return result
