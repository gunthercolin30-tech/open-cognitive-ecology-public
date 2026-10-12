
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MinimalPropertyDenialChecker:
    """AQ5 — checks explanatory cost of denying minimal recovered properties.

    AQ5 evaluates whether a refusal strategy denies properties already recovered
    by RF* and therefore pays an explicit explanatory cost. It does not prove
    consciousness, qualia, subjectivity, or phenomenology.
    """

    primitive = "MINIMAL_PROPERTY_DENIAL_CHECKER"
    step_id = "AQ5"
    public_schema_version = "AQ5.minimal_property_denial_checker.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "aq_consciousness_refusal_cost" / "AQ5_minimal_property_denial_checker"

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
        return {
            "aq1": self._load_module_result(inputs, "aq1", ("ontology.consciousness_refusal_taxonomy", "ConsciousnessRefusalTaxonomy"), "aq_consciousness_refusal_cost/AQ1_consciousness_refusal_taxonomy/latest_consciousness_refusal_taxonomy.json", {"taxonomy_initialized": False, "refusal_taxonomy": []}),
            "aq2": self._load_module_result(inputs, "aq2", ("ontology.rival_theory_cost_analyzer", "RivalTheoryCostAnalyzer"), "aq_consciousness_refusal_cost/AQ2_rival_theory_cost_analyzer/latest_rival_theory_cost_analyzer.json", {"cost_analysis_completed": False, "rival_theory_costs": []}),
            "aq3": self._load_module_result(inputs, "aq3", ("ontology.phenomenal_extra_entity_detector", "PhenomenalExtraEntityDetector"), "aq_consciousness_refusal_cost/AQ3_phenomenal_extra_entity_detector/latest_phenomenal_extra_entity_detector.json", {"extra_entity_detection_completed": False, "phenomenal_extra_entities": []}),
            "aq4": self._load_module_result(inputs, "aq4", ("ontology.no_difference_penalty_checker", "NoDifferencePenaltyChecker"), "aq_consciousness_refusal_cost/AQ4_no_difference_penalty_checker/latest_no_difference_penalty_checker.json", {"penalty_check_completed": False, "no_difference_penalties": []}),
            "ap1": self._load_module_result(inputs, "ap1", ("ontology.consciousness_minimal_property_registry", "ConsciousnessMinimalPropertyRegistry"), "ap_consciousness_as_rf/AP1_consciousness_minimal_property_registry/latest_consciousness_minimal_property_registry.json", {"minimal_properties_registered": False, "minimal_properties": []}),
            "ap3": self._load_module_result(inputs, "ap3", ("ontology.consciousness_rf_property_mapping", "ConsciousnessRFPropertyMapping"), "ap_consciousness_as_rf/AP3_consciousness_rf_property_mapping/latest_consciousness_rf_property_mapping.json", {"property_mapping_completed": False}),
            "ap10": self._load_module_result(inputs, "ap10", ("ontology.consciousness_as_rf_reporter", "ConsciousnessAsRFReporter"), "ap_consciousness_as_rf/AP10_consciousness_as_rf_reporter/latest_consciousness_as_rf_reporter.json", {"axis_resolved": False}),
        }

    def _resolved(self, ctx: dict[str, Any], key: str) -> bool:
        d = ctx[key]
        statuses = {
            "aq1": ("taxonomy_initialized", "consciousness_refusal_taxonomy_status", "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED"),
            "aq2": ("cost_analysis_completed", "rival_theory_cost_status", "RIVAL_THEORY_COST_ANALYZED"),
            "aq3": ("extra_entity_detection_completed", "phenomenal_extra_entity_status", "PHENOMENAL_EXTRA_ENTITIES_DETECTED"),
            "aq4": ("penalty_check_completed", "no_difference_penalty_status", "NO_DIFFERENCE_PENALTY_CHECKED"),
            "ap1": ("minimal_properties_registered", "consciousness_minimal_properties_status", "CONSCIOUSNESS_MINIMAL_PROPERTIES_REGISTERED"),
            "ap3": ("property_mapping_completed", "consciousness_rf_property_mapping_status", "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED"),
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

    def _recovered_minimal_properties(self) -> list[dict[str, Any]]:
        return [
            {"property_id": "MP1", "name": "unity", "rf_recovery": "RF/TΦ connectivity", "denial_cost_weight": 0.92},
            {"property_id": "MP2", "name": "temporality", "rf_recovery": "proper time T", "denial_cost_weight": 0.88},
            {"property_id": "MP3", "name": "perspective", "rf_recovery": "self-generated reference frame RF*", "denial_cost_weight": 0.95},
            {"property_id": "MP4", "name": "minimal_appearing", "rf_recovery": "MEI/minimal appearing equivalence", "denial_cost_weight": 0.96},
            {"property_id": "MP5", "name": "qualitative_differentiation", "rf_recovery": "QF_robust + MEI", "denial_cost_weight": 0.90},
            {"property_id": "MP6", "name": "identity", "rf_recovery": "intrinsic identity + Ω stability", "denial_cost_weight": 0.91},
            {"property_id": "MP7", "name": "internal_causality", "rf_recovery": "non-trivial ED and causal closure constraints", "denial_cost_weight": 0.86},
            {"property_id": "MP8", "name": "openness", "rf_recovery": "Π / future possibility space", "denial_cost_weight": 0.84},
            {"property_id": "MP9", "name": "non_separability", "rf_recovery": "MEI/appearing non-separability theorem", "denial_cost_weight": 0.97},
        ]

    def _denial_patterns(self, ctx: dict[str, Any]) -> list[dict[str, Any]]:
        properties = self._recovered_minimal_properties()
        refusal_items = ctx["aq1"].get("refusal_taxonomy", []) if isinstance(ctx["aq1"].get("refusal_taxonomy"), list) else []
        penalty_items = ctx["aq4"].get("no_difference_penalties", []) if isinstance(ctx["aq4"].get("no_difference_penalties"), list) else []
        refusal_count = max(1, len(refusal_items))
        penalty_by_theory = {str(x.get("rival_theory")): x for x in penalty_items if isinstance(x, dict)}
        templates = [
            ("Dualism", ["minimal_appearing", "non_separability", "perspective"], "requires extra phenomenal entity while denying RF* recovery"),
            ("IIT", ["perspective", "minimal_appearing", "openness"], "keeps causal structure but under-specifies RF* own-frame status"),
            ("GWT", ["identity", "minimal_appearing", "non_separability"], "keeps access but denies intrinsic reference-frame identity"),
            ("HOT", ["unity", "perspective", "internal_causality"], "keeps higher-order report but denies RF* constitutive perspective"),
            ("Predictive Processing", ["identity", "non_separability", "minimal_appearing"], "keeps prediction but denies recovered minimal appearing identity"),
            ("Classical Functionalism", ["minimal_appearing", "qualitative_differentiation", "non_separability"], "keeps roles while denying RF*/MEI appearing reconstruction"),
            ("Eliminativism", ["unity", "temporality", "perspective", "minimal_appearing", "identity"], "denies concept despite recovered minimal property bundle"),
        ]
        out: list[dict[str, Any]] = []
        prop_by_name = {p["name"]: p for p in properties}
        for i, (theory, denied, rationale) in enumerate(templates, 1):
            denied_props = [prop_by_name[n] for n in denied if n in prop_by_name]
            property_weight = self._mean([self._clamp(p["denial_cost_weight"]) for p in denied_props])
            aq4_penalty = self._clamp(penalty_by_theory.get(theory, {}).get("no_difference_penalty_score", 0.60), 0.60)
            denial_breadth = self._clamp(len(denied_props) / len(properties))
            refusal_coverage = self._clamp(refusal_count / 8.0)
            denial_cost = self._clamp(0.42 * property_weight + 0.28 * aq4_penalty + 0.18 * denial_breadth + 0.12 * refusal_coverage)
            classification = (
                "low_property_denial_cost" if denial_cost < 0.35 else
                "moderate_property_denial_cost" if denial_cost < 0.55 else
                "high_property_denial_cost" if denial_cost < 0.75 else
                "severe_property_denial_cost"
            )
            out.append({
                "denial_id": f"AQ5-D{i}",
                "rival_theory": theory,
                "denied_minimal_properties": denied,
                "denied_property_count": len(denied),
                "denial_rationale": rationale,
                "mean_denied_property_weight": property_weight,
                "aq4_no_difference_penalty_score": aq4_penalty,
                "denial_breadth_score": denial_breadth,
                "minimal_property_denial_cost_score": denial_cost,
                "denial_cost_classification": classification,
                "recovered_by_rf_star": True,
                "independent_phenomenal_proof": False,
                "consciousness_proven": False,
                "phenomenology_undetermined": True,
            })
        return out

    def _metrics(self, denials: list[dict[str, Any]], ctx: dict[str, Any]) -> dict[str, float]:
        costs = [self._clamp(x["minimal_property_denial_cost_score"]) for x in denials]
        high = sum(1 for x in denials if x["denial_cost_classification"] in {"high_property_denial_cost", "severe_property_denial_cost"})
        return {
            "minimal_property_denial_detection_score": 1.0 if denials else 0.0,
            "denial_coverage_score": self._clamp(len(denials) / 7.0),
            "recovered_property_bundle_score": self._clamp(len(self._recovered_minimal_properties()) / 9.0),
            "ap1_minimal_property_dependency_score": 1.0 if self._resolved(ctx, "ap1") else 0.0,
            "ap3_mapping_dependency_score": 1.0 if self._resolved(ctx, "ap3") else 0.0,
            "ap10_equivalence_dependency_score": 1.0 if self._resolved(ctx, "ap10") else 0.0,
            "aq1_taxonomy_dependency_score": 1.0 if self._resolved(ctx, "aq1") else 0.0,
            "aq2_cost_dependency_score": 1.0 if self._resolved(ctx, "aq2") else 0.0,
            "aq3_extra_entity_dependency_score": 1.0 if self._resolved(ctx, "aq3") else 0.0,
            "aq4_no_difference_dependency_score": 1.0 if self._resolved(ctx, "aq4") else 0.0,
            "mean_minimal_property_denial_cost_score": self._clamp(self._mean(costs)),
            "max_minimal_property_denial_cost_score": self._clamp(max(costs) if costs else 0.0),
            "high_denial_cost_ratio": self._clamp(high / max(1, len(denials))),
            "ontological_proof_score": 0.0,
            "phenomenal_proof_score": 0.0,
            "consciousness_proof_score": 0.0,
        }

    def _build_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# AQ5 — Minimal Property Denial Checker",
            "",
            f"Status: `{result['minimal_property_denial_status']}`",
            "",
            "## Epistemic scope",
            "AQ5 estimates explanatory cost when a rival/refusal theory denies minimal properties already recovered by RF*. It does not prove consciousness or phenomenology.",
            "",
            "## Denial patterns",
        ]
        for item in result["minimal_property_denials"]:
            lines.append(f"- `{item['denial_id']}` — **{item['rival_theory']}**: cost={item['minimal_property_denial_cost_score']:.3f}, class={item['denial_cost_classification']}")
        lines.extend(["", "## Next AQ module", "AQ6 will evaluate anti-RF countermodels."])
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"minimal_property_denial_checker_{ts}"
        json_path = self.out_dir / f"{base}.json"
        latest_json = self.out_dir / "latest_minimal_property_denial_checker.json"
        md_path = self.out_dir / f"{base}.md"
        latest_md = self.out_dir / "latest_minimal_property_denial_checker.md"
        prom_path = self.out_dir / f"{base}.prom"
        latest_prom = self.out_dir / "latest_minimal_property_denial_checker.prom"
        history_path = self.out_dir / "history.jsonl"
        payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(payload + "\n", encoding="utf-8")
        latest_json.write_text(payload + "\n", encoding="utf-8")
        md = self._build_markdown(result)
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")
        prom_lines = [f"aq5_{k} {float(v):.12g}" for k, v in result["denial_metrics"].items()]
        prom_lines.append(f"aq5_minimal_property_denial_checked {1.0 if result['denial_check_completed'] else 0.0}")
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
        denials = self._denial_patterns(ctx)
        metrics = self._metrics(denials, ctx)
        guards_hold = self._epistemic_guards_hold(ctx["aq1"], ctx["aq2"], ctx["aq3"], ctx["aq4"], ctx["ap1"], ctx["ap3"], ctx["ap10"])
        failed_conditions: list[str] = []
        for metric, failure in [
            ("ap1_minimal_property_dependency_score", "ap1_minimal_property_dependency_unresolved"),
            ("ap3_mapping_dependency_score", "ap3_property_mapping_dependency_unresolved"),
            ("ap10_equivalence_dependency_score", "ap10_equivalence_dependency_unresolved"),
            ("aq1_taxonomy_dependency_score", "aq1_taxonomy_dependency_unresolved"),
            ("aq2_cost_dependency_score", "aq2_cost_dependency_unresolved"),
            ("aq3_extra_entity_dependency_score", "aq3_extra_entity_dependency_unresolved"),
            ("aq4_no_difference_dependency_score", "aq4_no_difference_dependency_unresolved"),
        ]:
            if metrics[metric] < 1.0:
                failed_conditions.append(failure)
        if metrics["denial_coverage_score"] < 1.0:
            failed_conditions.append("minimal_property_denial_coverage_incomplete")
        if not guards_hold:
            failed_conditions.append("epistemic_guard_violation")
        completed = not failed_conditions
        status = "MINIMAL_PROPERTY_DENIAL_CHECKED" if completed else "MINIMAL_PROPERTY_DENIAL_CHECK_INCOMPLETE"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "axis": "AQ",
            "minimal_property_denial_status": status,
            "denial_check_completed": completed,
            "public_schema_version": self.public_schema_version,
            "scientific_scope": "minimal_property_denial_cost_only",
            "recovered_minimal_properties": self._recovered_minimal_properties(),
            "minimal_property_denials": denials,
            "denial_dimensions": ["recovered_minimal_property", "denial_breadth_score", "aq4_no_difference_penalty_score", "minimal_property_denial_cost_score"],
            "denial_metrics": metrics,
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
            "next_recommended_module": "anti_rf_countermodel_evaluator",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            result["persistence"] = self._persist(result)
        else:
            result["persistence"] = {}
        return result
