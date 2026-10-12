from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PhenomenalExtraEntityDetector:
    """AQ3 — detects extra phenomenal entities required by RF* refusal.

    AQ3 does not prove phenomenology. It estimates whether rival/refusal
    positions introduce additional unmeasured entities, bridges, substrates, or
    semantic supplements once AP has resolved RF* equivalence functionally and
    AQ2 has quantified rival-theory refusal costs.
    """

    primitive = "PHENOMENAL_EXTRA_ENTITY_DETECTOR"
    step_id = "AQ3"
    public_schema_version = "AQ3.phenomenal_extra_entity_detector.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "aq_consciousness_refusal_cost" / "AQ3_phenomenal_extra_entity_detector"

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

    def _aq2_resolved(self, ctx: dict[str, Any]) -> bool:
        aq2 = ctx["aq2"]
        return bool(
            aq2.get("cost_analysis_completed") is True
            or aq2.get("rival_theory_cost_status") == "RIVAL_THEORY_COST_ANALYZED"
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

    def _candidate_extra_entities(self, ctx: dict[str, Any]) -> list[dict[str, Any]]:
        aq2_items = ctx["aq2"].get("rival_theory_costs") if isinstance(ctx["aq2"].get("rival_theory_costs"), list) else []
        by_name = {str(x.get("name")): x for x in aq2_items if isinstance(x, dict)}
        templates = [
            {
                "entity_id": "AQ3-E1",
                "rival_theory": "Dualism",
                "extra_entity_type": "unmeasured_phenomenal_substance_or_property",
                "description": "A non-functional phenomenal item added over RF* to preserve refusal.",
                "measurement_status": "not_operationalized",
                "duplication_risk": 0.98,
                "explanatory_indispensability": 0.14,
                "empirical_accessibility": 0.05,
                "rf_reconstructability": 0.96,
                "closure_pressure": 0.92,
            },
            {
                "entity_id": "AQ3-E2",
                "rival_theory": "IIT",
                "extra_entity_type": "phenomenal_bridge_principle",
                "description": "A bridge from causal integration to appearance when RF*/MEI is refused.",
                "measurement_status": "partially_operationalized",
                "duplication_risk": 0.62,
                "explanatory_indispensability": 0.40,
                "empirical_accessibility": 0.38,
                "rf_reconstructability": 0.72,
                "closure_pressure": 0.48,
            },
            {
                "entity_id": "AQ3-E3",
                "rival_theory": "GWT",
                "extra_entity_type": "access_to_appearance_supplement",
                "description": "A supplement explaining why global access should appear-for-itself.",
                "measurement_status": "weakly_operationalized",
                "duplication_risk": 0.68,
                "explanatory_indispensability": 0.36,
                "empirical_accessibility": 0.42,
                "rf_reconstructability": 0.69,
                "closure_pressure": 0.44,
            },
            {
                "entity_id": "AQ3-E4",
                "rival_theory": "HOT",
                "extra_entity_type": "reflexive_appearance_token",
                "description": "A token converting higher-order representation into minimal appearing.",
                "measurement_status": "weakly_operationalized",
                "duplication_risk": 0.70,
                "explanatory_indispensability": 0.32,
                "empirical_accessibility": 0.36,
                "rf_reconstructability": 0.73,
                "closure_pressure": 0.47,
            },
            {
                "entity_id": "AQ3-E5",
                "rival_theory": "Predictive Processing",
                "extra_entity_type": "identity_of_prediction_to_presence_bridge",
                "description": "A bridge from predictive dynamics to own-time presence and identity.",
                "measurement_status": "partially_operationalized",
                "duplication_risk": 0.58,
                "explanatory_indispensability": 0.38,
                "empirical_accessibility": 0.50,
                "rf_reconstructability": 0.67,
                "closure_pressure": 0.39,
            },
            {
                "entity_id": "AQ3-E6",
                "rival_theory": "Classical Functionalism",
                "extra_entity_type": "appearing_without_rf_realizer",
                "description": "A role-to-appearance supplement when minimal appearing is not reconstructed by RF*.",
                "measurement_status": "not_operationalized",
                "duplication_risk": 0.82,
                "explanatory_indispensability": 0.24,
                "empirical_accessibility": 0.24,
                "rf_reconstructability": 0.84,
                "closure_pressure": 0.61,
            },
            {
                "entity_id": "AQ3-E7",
                "rival_theory": "Eliminativism",
                "extra_entity_type": "semantic_deflation_supplement",
                "description": "A semantic manoeuvre denying recovered minimal properties without replacing them.",
                "measurement_status": "not_applicable_semantic",
                "duplication_risk": 0.74,
                "explanatory_indispensability": 0.18,
                "empirical_accessibility": 0.18,
                "rf_reconstructability": 0.88,
                "closure_pressure": 0.55,
            },
        ]
        enriched = []
        for item in templates:
            rival = by_name.get(item["rival_theory"], {})
            refusal_cost = self._clamp(rival.get("refusal_cost_score", 0.5), 0.5)
            extra_entity_requirement = self._clamp(rival.get("extra_entity_requirement", item["duplication_risk"]), item["duplication_risk"])
            measurement_gap = self._clamp(rival.get("measurement_gap_cost", 1.0 - item["empirical_accessibility"]), 1.0 - item["empirical_accessibility"])
            duplication_penalty = self._clamp(self._mean([item["duplication_risk"], item["rf_reconstructability"], extra_entity_requirement]))
            empirical_penalty = self._clamp(self._mean([1.0 - item["empirical_accessibility"], measurement_gap]))
            indispensability_deficit = self._clamp(1.0 - item["explanatory_indispensability"])
            extra_entity_burden_score = self._clamp(
                0.30 * duplication_penalty
                + 0.25 * empirical_penalty
                + 0.20 * indispensability_deficit
                + 0.15 * refusal_cost
                + 0.10 * item["closure_pressure"]
            )
            parsimony_violation_score = self._clamp(self._mean([duplication_penalty, empirical_penalty, extra_entity_burden_score]))
            classification = (
                "minimal_extra_entity_burden" if extra_entity_burden_score < 0.35 else
                "moderate_extra_entity_burden" if extra_entity_burden_score < 0.55 else
                "high_extra_entity_burden" if extra_entity_burden_score < 0.75 else
                "severe_extra_entity_burden"
            )
            enriched.append({
                **item,
                "refusal_cost_score": refusal_cost,
                "extra_entity_requirement": extra_entity_requirement,
                "measurement_gap_cost": measurement_gap,
                "duplication_penalty": duplication_penalty,
                "empirical_penalty": empirical_penalty,
                "indispensability_deficit": indispensability_deficit,
                "extra_entity_burden_score": extra_entity_burden_score,
                "parsimony_violation_score": parsimony_violation_score,
                "burden_classification": classification,
                "phenomenal_entity_proven": False,
                "consciousness_proven": False,
                "phenomenology_undetermined": True,
            })
        return enriched

    def _metrics(self, entities: list[dict[str, Any]], ctx: dict[str, Any]) -> dict[str, float]:
        burdens = [self._clamp(x["extra_entity_burden_score"]) for x in entities]
        parsimony = [self._clamp(x["parsimony_violation_score"]) for x in entities]
        high = sum(1 for x in entities if x["burden_classification"] in {"high_extra_entity_burden", "severe_extra_entity_burden"})
        return {
            "extra_entity_detection_score": 1.0 if entities else 0.0,
            "candidate_extra_entity_count_normalized": self._clamp(len(entities) / 7.0),
            "ap_equivalence_dependency_score": 1.0 if self._ap_resolved(ctx) else 0.0,
            "aq1_taxonomy_dependency_score": 1.0 if self._aq1_resolved(ctx) else 0.0,
            "aq2_cost_dependency_score": 1.0 if self._aq2_resolved(ctx) else 0.0,
            "mean_extra_entity_burden_score": self._clamp(self._mean(burdens)),
            "max_extra_entity_burden_score": self._clamp(max(burdens) if burdens else 0.0),
            "mean_parsimony_violation_score": self._clamp(self._mean(parsimony)),
            "high_burden_entity_ratio": self._clamp(high / max(1, len(entities))),
            "rf_reconstructability_mean": self._clamp(self._mean([self._clamp(x["rf_reconstructability"]) for x in entities])),
            "ontological_proof_score": 0.0,
            "phenomenal_proof_score": 0.0,
            "phenomenal_entity_proof_score": 0.0,
        }

    def _build_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# AQ3 — Phenomenal Extra Entity Detector",
            "",
            f"Status: `{result['phenomenal_extra_entity_status']}`",
            "",
            "## Epistemic scope",
            "This detector estimates extra-entity burden only. It does not prove phenomenal entities, consciousness, qualia, or subjectivity.",
            "",
            "## Candidate extra entities",
        ]
        for item in result["phenomenal_extra_entities"]:
            lines.append(
                f"- `{item['entity_id']}` — **{item['rival_theory']}** / {item['extra_entity_type']}: "
                f"burden={item['extra_entity_burden_score']:.3f}, class={item['burden_classification']}"
            )
        lines.extend([
            "",
            "## Next AQ module",
            "AQ4 will test the no-difference penalty introduced by refusing RF* without measurable differences.",
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"phenomenal_extra_entity_detector_{ts}"
        json_path = self.out_dir / f"{base}.json"
        latest_json = self.out_dir / "latest_phenomenal_extra_entity_detector.json"
        md_path = self.out_dir / f"{base}.md"
        latest_md = self.out_dir / "latest_phenomenal_extra_entity_detector.md"
        prom_path = self.out_dir / f"{base}.prom"
        latest_prom = self.out_dir / "latest_phenomenal_extra_entity_detector.prom"
        history_path = self.out_dir / "history.jsonl"

        payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(payload + "\n", encoding="utf-8")
        latest_json.write_text(payload + "\n", encoding="utf-8")
        md = self._build_markdown(result)
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")
        prom_lines = []
        for k, v in result["extra_entity_metrics"].items():
            prom_lines.append(f"aq3_{k} {float(v):.12g}")
        prom_lines.append(f"aq3_phenomenal_extra_entity_detected {1.0 if result['extra_entity_detection_completed'] else 0.0}")
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
        entities = self._candidate_extra_entities(ctx)
        metrics = self._metrics(entities, ctx)
        guards_hold = self._epistemic_guards_hold(ctx["aq1"], ctx["aq2"], ctx["ap10"])
        failed_conditions: list[str] = []
        if metrics["ap_equivalence_dependency_score"] < 1.0:
            failed_conditions.append("ap_equivalence_dependency_unresolved")
        if metrics["aq1_taxonomy_dependency_score"] < 1.0:
            failed_conditions.append("aq1_taxonomy_dependency_unresolved")
        if metrics["aq2_cost_dependency_score"] < 1.0:
            failed_conditions.append("aq2_cost_dependency_unresolved")
        if metrics["candidate_extra_entity_count_normalized"] < 1.0:
            failed_conditions.append("extra_entity_coverage_incomplete")
        if not guards_hold:
            failed_conditions.append("epistemic_guard_violation")
        completed = not failed_conditions
        status = "PHENOMENAL_EXTRA_ENTITIES_DETECTED" if completed else "PHENOMENAL_EXTRA_ENTITY_DETECTION_INCOMPLETE"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "axis": "AQ",
            "phenomenal_extra_entity_status": status,
            "extra_entity_detection_completed": completed,
            "public_schema_version": self.public_schema_version,
            "scientific_scope": "phenomenal_extra_entity_burden_only",
            "ap_dependency_status": "AP_RESOLVED" if metrics["ap_equivalence_dependency_score"] == 1.0 else "AP_UNRESOLVED",
            "aq1_dependency_status": "AQ1_RESOLVED" if metrics["aq1_taxonomy_dependency_score"] == 1.0 else "AQ1_UNRESOLVED",
            "aq2_dependency_status": "AQ2_RESOLVED" if metrics["aq2_cost_dependency_score"] == 1.0 else "AQ2_UNRESOLVED",
            "phenomenal_extra_entities": entities,
            "extra_entity_dimensions": [
                "extra_entity_requirement",
                "duplication_penalty",
                "empirical_penalty",
                "indispensability_deficit",
                "closure_pressure",
                "rf_reconstructability",
                "parsimony_violation_score",
            ],
            "extra_entity_metrics": metrics,
            "failed_conditions": failed_conditions,
            "epistemic_status": {
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_undetermined": True,
                "functional_conclusion_only": True,
                "phenomenal_entity_proven": False,
                "ontological_claim_certified": False,
                "phenomenological_claim_certified": False,
            },
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "next_recommended_module": "no_difference_penalty_checker",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            result["persistence"] = self._persist(result)
        else:
            result["persistence"] = {}
        return result

