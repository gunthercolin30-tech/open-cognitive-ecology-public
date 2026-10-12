from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RivalTheoryCostAnalyzer:
    """AQ2 — comparative explanatory-cost analyzer for rival theories.

    Given AP's resolved RF* equivalence support and AQ1's refusal taxonomy,
    this module estimates the explicit explanatory burden incurred by rival
    theories when they refuse to identify consciousness with RF*.

    The output is comparative and functional only. It does not prove
    consciousness, qualia, subjectivity, or phenomenology.
    """

    primitive = "RIVAL_THEORY_COST_ANALYZER"
    step_id = "AQ2"
    public_schema_version = "AQ2.rival_theory_cost_analyzer.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "aq_consciousness_refusal_cost" / "AQ2_rival_theory_cost_analyzer"

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
            "ap10": self._load_module_result(
                inputs,
                "ap10",
                ("ontology.consciousness_as_rf_reporter", "ConsciousnessAsRFReporter"),
                "ap_consciousness_as_rf/AP10_consciousness_as_rf_reporter/latest_consciousness_as_rf_reporter.json",
                {"axis_resolved": False, "report_metrics": {}},
            ),
        }

    def _ap_resolved(self, ctx: dict[str, Any]) -> bool:
        ap10 = ctx["ap10"]
        return bool(
            ap10.get("axis_resolved") is True
            or ap10.get("consciousness_as_rf_equivalence_status") == "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED"
        )

    def _aq1_resolved(self, ctx: dict[str, Any]) -> bool:
        aq1 = ctx["aq1"]
        return bool(
            aq1.get("taxonomy_initialized") is True
            or aq1.get("consciousness_refusal_taxonomy_status") == "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED"
        )

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

    def _rival_theories(self) -> list[dict[str, Any]]:
        return [
            {
                "theory_id": "AQ2-T1",
                "name": "IIT",
                "scope": "integrated_information_causal_structure",
                "rf_recovery": 0.72,
                "minimal_property_recovery": 0.78,
                "measurement_clarity": 0.62,
                "falsifiability": 0.58,
                "extra_entity_requirement": 0.36,
                "semantic_continuity": 0.77,
                "rf_refusal_mode": "requires_extra_bridge_from_causal_structure_to_appearance",
            },
            {
                "theory_id": "AQ2-T2",
                "name": "GWT",
                "scope": "global_access_and_broadcast",
                "rf_recovery": 0.64,
                "minimal_property_recovery": 0.66,
                "measurement_clarity": 0.82,
                "falsifiability": 0.74,
                "extra_entity_requirement": 0.42,
                "semantic_continuity": 0.81,
                "rf_refusal_mode": "access_without_intrinsic_reference_frame_completion",
            },
            {
                "theory_id": "AQ2-T3",
                "name": "HOT",
                "scope": "higher_order_reflexive_representation",
                "rf_recovery": 0.59,
                "minimal_property_recovery": 0.61,
                "measurement_clarity": 0.65,
                "falsifiability": 0.66,
                "extra_entity_requirement": 0.50,
                "semantic_continuity": 0.72,
                "rf_refusal_mode": "reflexivity_without_complete_proper_frame",
            },
            {
                "theory_id": "AQ2-T4",
                "name": "Predictive Processing",
                "scope": "predictive_dynamics_and_error_minimization",
                "rf_recovery": 0.67,
                "minimal_property_recovery": 0.63,
                "measurement_clarity": 0.76,
                "falsifiability": 0.79,
                "extra_entity_requirement": 0.40,
                "semantic_continuity": 0.70,
                "rf_refusal_mode": "prediction_without_intrinsic_identity_condition",
            },
            {
                "theory_id": "AQ2-T5",
                "name": "Classical Functionalism",
                "scope": "input_output_and_role_realization",
                "rf_recovery": 0.48,
                "minimal_property_recovery": 0.52,
                "measurement_clarity": 0.79,
                "falsifiability": 0.68,
                "extra_entity_requirement": 0.58,
                "semantic_continuity": 0.64,
                "rf_refusal_mode": "behavioral_role_without_minimal_appearing_recovery",
            },
            {
                "theory_id": "AQ2-T6",
                "name": "Dualism",
                "scope": "non_measured_phenomenal_substance_or_property",
                "rf_recovery": 0.24,
                "minimal_property_recovery": 0.38,
                "measurement_clarity": 0.12,
                "falsifiability": 0.08,
                "extra_entity_requirement": 0.96,
                "semantic_continuity": 0.55,
                "rf_refusal_mode": "adds_unmeasured_phenomenal_extra_entity",
            },
            {
                "theory_id": "AQ2-T7",
                "name": "Eliminativism",
                "scope": "denial_of_consciousness_conceptual_validity",
                "rf_recovery": 0.18,
                "minimal_property_recovery": 0.20,
                "measurement_clarity": 0.44,
                "falsifiability": 0.32,
                "extra_entity_requirement": 0.18,
                "semantic_continuity": 0.21,
                "rf_refusal_mode": "denies_minimal_properties_despite_reconstruction",
            },
        ]

    def _analyze_theory(self, t: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        ap10_metrics = ctx["ap10"].get("report_metrics") if isinstance(ctx["ap10"].get("report_metrics"), dict) else {}
        ap_equivalence_support = self._clamp(
            ap10_metrics.get("functional_equivalence_support_score", ap10_metrics.get("equivalence_support_score", 1.0)),
            1.0,
        )
        rf_gap = 1.0 - self._clamp(t["rf_recovery"])
        property_gap = 1.0 - self._clamp(t["minimal_property_recovery"])
        measurement_gap = 1.0 - self._clamp(t["measurement_clarity"])
        falsification_gap = 1.0 - self._clamp(t["falsifiability"])
        extra_entity_cost = self._clamp(t["extra_entity_requirement"])
        semantic_gap = 1.0 - self._clamp(t["semantic_continuity"])
        explanatory_gap_cost = self._clamp(self._mean([rf_gap, property_gap, semantic_gap]))
        scientific_control_cost = self._clamp(self._mean([measurement_gap, falsification_gap]))
        refusal_cost_score = self._clamp(
            0.30 * explanatory_gap_cost
            + 0.25 * extra_entity_cost
            + 0.20 * scientific_control_cost
            + 0.15 * rf_gap
            + 0.10 * ap_equivalence_support
        )
        comparative_viability_score = self._clamp(1.0 - refusal_cost_score)
        cost_level = (
            "low" if refusal_cost_score < 0.35 else
            "moderate" if refusal_cost_score < 0.55 else
            "high" if refusal_cost_score < 0.75 else
            "very_high"
        )
        return {
            **t,
            "rf_gap_cost": rf_gap,
            "minimal_property_gap_cost": property_gap,
            "measurement_gap_cost": measurement_gap,
            "falsification_gap_cost": falsification_gap,
            "semantic_gap_cost": semantic_gap,
            "explanatory_gap_cost": explanatory_gap_cost,
            "scientific_control_cost": scientific_control_cost,
            "refusal_cost_score": refusal_cost_score,
            "comparative_viability_score": comparative_viability_score,
            "cost_level": cost_level,
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
        }

    def _metrics(self, analyses: list[dict[str, Any]], ctx: dict[str, Any]) -> dict[str, float]:
        costs = [self._clamp(x["refusal_cost_score"]) for x in analyses]
        viable = [self._clamp(x["comparative_viability_score"]) for x in analyses]
        high_cost_count = sum(1 for x in analyses if x["cost_level"] in {"high", "very_high"})
        return {
            "rival_theory_count_normalized": self._clamp(len(analyses) / 7.0),
            "ap_equivalence_dependency_score": 1.0 if self._ap_resolved(ctx) else 0.0,
            "aq1_taxonomy_dependency_score": 1.0 if self._aq1_resolved(ctx) else 0.0,
            "mean_refusal_cost_score": self._clamp(self._mean(costs)),
            "max_refusal_cost_score": self._clamp(max(costs) if costs else 0.0),
            "min_refusal_cost_score": self._clamp(min(costs) if costs else 0.0),
            "mean_comparative_viability_score": self._clamp(self._mean(viable)),
            "high_cost_theory_ratio": self._clamp(high_cost_count / max(1, len(analyses))),
            "cost_explicitness_score": 1.0 if all("refusal_cost_score" in x for x in analyses) else 0.0,
            "ontological_proof_score": 0.0,
            "phenomenal_proof_score": 0.0,
        }

    def _build_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# AQ2 — Rival Theory Cost Analyzer",
            "",
            f"Status: `{result['rival_theory_cost_status']}`",
            "",
            "## Epistemic scope",
            "This report estimates comparative explanatory refusal costs only. It does not prove consciousness, qualia, subjectivity, or phenomenology.",
            "",
            "## Rival theories",
        ]
        for item in result["rival_theory_costs"]:
            lines.append(
                f"- `{item['theory_id']}` — **{item['name']}**: "
                f"cost={item['refusal_cost_score']:.3f}, level={item['cost_level']}, "
                f"viability={item['comparative_viability_score']:.3f}"
            )
        lines.extend([
            "",
            "## Next AQ module",
            "AQ3 will isolate the extra-entity burden of phenomenal additions after RF* support.",
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"rival_theory_cost_analyzer_{ts}"
        json_path = self.out_dir / f"{base}.json"
        latest_json = self.out_dir / "latest_rival_theory_cost_analyzer.json"
        md_path = self.out_dir / f"{base}.md"
        latest_md = self.out_dir / "latest_rival_theory_cost_analyzer.md"
        prom_path = self.out_dir / f"{base}.prom"
        latest_prom = self.out_dir / "latest_rival_theory_cost_analyzer.prom"
        history_path = self.out_dir / "history.jsonl"

        payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(payload + "\n", encoding="utf-8")
        latest_json.write_text(payload + "\n", encoding="utf-8")
        md = self._build_markdown(result)
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")
        prom_lines = []
        for k, v in result["cost_metrics"].items():
            prom_lines.append(f"aq2_{k} {float(v):.12g}")
        prom_lines.append(f"aq2_rival_theory_cost_analyzed {1.0 if result['cost_analysis_completed'] else 0.0}")
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
        analyses = [self._analyze_theory(t, ctx) for t in self._rival_theories()]
        metrics = self._metrics(analyses, ctx)
        guards_hold = self._epistemic_guards_hold(ctx["aq1"], ctx["ap10"])
        failed_conditions: list[str] = []
        if metrics["ap_equivalence_dependency_score"] < 1.0:
            failed_conditions.append("ap_equivalence_dependency_unresolved")
        if metrics["aq1_taxonomy_dependency_score"] < 1.0:
            failed_conditions.append("aq1_taxonomy_dependency_unresolved")
        if metrics["rival_theory_count_normalized"] < 1.0:
            failed_conditions.append("rival_theory_coverage_incomplete")
        if not guards_hold:
            failed_conditions.append("epistemic_guard_violation")
        completed = not failed_conditions
        status = "RIVAL_THEORY_COST_ANALYZED" if completed else "RIVAL_THEORY_COST_ANALYSIS_INCOMPLETE"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "axis": "AQ",
            "rival_theory_cost_status": status,
            "cost_analysis_completed": completed,
            "public_schema_version": self.public_schema_version,
            "scientific_scope": "comparative_explanatory_cost_only",
            "ap_dependency_status": "AP_RESOLVED" if metrics["ap_equivalence_dependency_score"] == 1.0 else "AP_UNRESOLVED",
            "aq1_dependency_status": "AQ1_RESOLVED" if metrics["aq1_taxonomy_dependency_score"] == 1.0 else "AQ1_UNRESOLVED",
            "rival_theory_costs": analyses,
            "cost_dimensions": [
                "rf_gap_cost",
                "minimal_property_gap_cost",
                "extra_entity_requirement",
                "measurement_gap_cost",
                "falsification_gap_cost",
                "semantic_gap_cost",
                "explanatory_gap_cost",
                "scientific_control_cost",
            ],
            "cost_metrics": metrics,
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
            "next_recommended_module": "phenomenal_extra_entity_detector",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            result["persistence"] = self._persist(result)
        else:
            result["persistence"] = {}
        return result

