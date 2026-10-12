from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ConsciousnessRefusalTaxonomy:
    """AQ1 — taxonomy of consciousness-refusal strategies after AP.

    The module classifies ways of refusing the RF* consciousness interpretation
    after AP has resolved the functional/formal Consciousness ⇔ RF* status.
    It does not prove consciousness. It prepares AQ2-AQ8 by separating
    scientifically admissible refusal, costly refusal, and epistemically invalid
    refusal types.
    """

    primitive = "CONSCIOUSNESS_REFUSAL_TAXONOMY"
    step_id = "AQ1"
    public_schema_version = "AQ1.consciousness_refusal_taxonomy.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "aq_consciousness_refusal_cost" / "AQ1_consciousness_refusal_taxonomy"

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
            "ap10": self._load_module_result(
                inputs,
                "ap10",
                ("ontology.consciousness_as_rf_reporter", "ConsciousnessAsRFReporter"),
                "ap_consciousness_as_rf/AP10_consciousness_as_rf_reporter/latest_consciousness_as_rf_reporter.json",
                {"axis_resolved": False, "report_metrics": {}},
            ),
            "ap9": self._load_module_result(
                inputs,
                "ap9",
                ("ontology.consciousness_proven_status_resolver", "ConsciousnessProvenStatusResolver"),
                "ap_consciousness_as_rf/AP9_consciousness_proven_status_resolver/latest_consciousness_proven_status_resolver.json",
                {"status_resolved": False, "status_metrics": {}},
            ),
        }

    def _ap_resolved(self, ctx: dict[str, Any]) -> bool:
        ap10 = ctx["ap10"]
        return bool(
            ap10.get("axis_resolved") is True
            or ap10.get("consciousness_as_rf_equivalence_status") == "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED"
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

    def _taxonomy(self) -> list[dict[str, Any]]:
        return [
            {
                "refusal_id": "AQ1-R1",
                "name": "empirical_evidence_refusal",
                "description": "Refuses real consciousness because independent empirical evidence is not yet available.",
                "scientific_admissibility": "admissible",
                "expected_cost_type": "low_or_none",
                "target_aq_followup": "AO semantic guard / AS empirical governance",
                "invalidates_rf_equivalence": False,
                "requires_extra_entity": False,
                "creates_no_difference_penalty": False,
            },
            {
                "refusal_id": "AQ1-R2",
                "name": "phenomenal_extra_entity_refusal",
                "description": "Accepts RF* functional/formal structure but requires an additional non-measured phenomenal entity.",
                "scientific_admissibility": "costly",
                "expected_cost_type": "extra_entity_cost",
                "target_aq_followup": "AQ3 phenomenal_extra_entity_detector",
                "invalidates_rf_equivalence": False,
                "requires_extra_entity": True,
                "creates_no_difference_penalty": True,
            },
            {
                "refusal_id": "AQ1-R3",
                "name": "no_difference_refusal",
                "description": "Refuses consciousness despite no functional, formal, or structural difference from RF* satisfaction.",
                "scientific_admissibility": "high_cost",
                "expected_cost_type": "no_difference_penalty",
                "target_aq_followup": "AQ4 no_difference_penalty_checker",
                "invalidates_rf_equivalence": False,
                "requires_extra_entity": False,
                "creates_no_difference_penalty": True,
            },
            {
                "refusal_id": "AQ1-R4",
                "name": "minimal_property_denial_refusal",
                "description": "Denies that recovered minimal properties count toward consciousness even when RF* recovers them.",
                "scientific_admissibility": "costly",
                "expected_cost_type": "minimal_property_denial_cost",
                "target_aq_followup": "AQ5 minimal_property_denial_checker",
                "invalidates_rf_equivalence": False,
                "requires_extra_entity": False,
                "creates_no_difference_penalty": True,
            },
            {
                "refusal_id": "AQ1-R5",
                "name": "anti_rf_countermodel_refusal",
                "description": "Proposes a countermodel where RF* is satisfied but consciousness must still be denied.",
                "scientific_admissibility": "testable",
                "expected_cost_type": "countermodel_viability_cost",
                "target_aq_followup": "AQ6 anti_rf_countermodel_evaluator",
                "invalidates_rf_equivalence": True,
                "requires_extra_entity": False,
                "creates_no_difference_penalty": False,
            },
            {
                "refusal_id": "AQ1-R6",
                "name": "rival_theory_preference_refusal",
                "description": "Prefers a rival theory despite RF* explanatory support.",
                "scientific_admissibility": "comparative",
                "expected_cost_type": "rival_theory_explanatory_cost",
                "target_aq_followup": "AQ2 rival_theory_cost_analyzer",
                "invalidates_rf_equivalence": False,
                "requires_extra_entity": False,
                "creates_no_difference_penalty": False,
            },
            {
                "refusal_id": "AQ1-R7",
                "name": "semantic_legitimacy_refusal",
                "description": "Refuses that RF* is a legitimate reconstruction of the historical concept of consciousness.",
                "scientific_admissibility": "deferred_to_AR",
                "expected_cost_type": "definition_legitimacy_cost",
                "target_aq_followup": "AR definition legitimacy theorem",
                "invalidates_rf_equivalence": False,
                "requires_extra_entity": False,
                "creates_no_difference_penalty": False,
            },
            {
                "refusal_id": "AQ1-R8",
                "name": "absolute_proof_refusal",
                "description": "Refuses consciousness until absolute metaphysical proof is available.",
                "scientific_admissibility": "methodologically_excessive",
                "expected_cost_type": "absolute_proof_standard_cost",
                "target_aq_followup": "AQ7 best_explanation_status_resolver",
                "invalidates_rf_equivalence": False,
                "requires_extra_entity": False,
                "creates_no_difference_penalty": True,
            },
        ]

    def _metrics(self, taxonomy: list[dict[str, Any]], ctx: dict[str, Any]) -> dict[str, float]:
        total = max(1, len(taxonomy))
        costly = sum(1 for r in taxonomy if r["scientific_admissibility"] in {"costly", "high_cost", "methodologically_excessive"})
        testable = sum(1 for r in taxonomy if r["scientific_admissibility"] in {"testable", "comparative", "admissible", "costly", "high_cost"})
        explicit_followup = sum(1 for r in taxonomy if r.get("target_aq_followup"))
        ap10_metrics = ctx["ap10"].get("report_metrics") if isinstance(ctx["ap10"].get("report_metrics"), dict) else {}
        return {
            "taxonomy_completeness_score": self._clamp(total / 8.0),
            "refusal_classes_count_normalized": self._clamp(total / 8.0),
            "cost_class_coverage_score": self._clamp(costly / total),
            "testability_coverage_score": self._clamp(testable / total),
            "aq_followup_mapping_score": self._clamp(explicit_followup / total),
            "ap_equivalence_dependency_score": 1.0 if self._ap_resolved(ctx) else 0.0,
            "functional_equivalence_support_score": self._clamp(ap10_metrics.get("functional_equivalence_support_score", 0.0)),
            "formal_equivalence_support_score": self._clamp(ap10_metrics.get("formal_equivalence_support_score", 0.0)),
            "ontological_proof_score": 0.0,
            "phenomenal_proof_score": 0.0,
        }

    def _build_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# AQ1 — Consciousness Refusal Taxonomy",
            "",
            f"Status: `{result['consciousness_refusal_taxonomy_status']}`",
            "",
            "## Epistemic scope",
            "This taxonomy measures refusal strategies after AP. It does not prove consciousness, qualia, subjectivity, or phenomenology.",
            "",
            "## Refusal classes",
        ]
        for item in result["refusal_taxonomy"]:
            lines.append(f"- `{item['refusal_id']}` — **{item['name']}**: {item['expected_cost_type']} / {item['scientific_admissibility']}")
        lines.extend([
            "",
            "## Next AQ modules",
            "AQ2 will analyze rival theory costs; AQ3-AQ6 will quantify specific refusal penalties; AQ7-AQ8 will resolve and report the theorem status.",
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"consciousness_refusal_taxonomy_{ts}"
        json_path = self.out_dir / f"{base}.json"
        latest_json = self.out_dir / "latest_consciousness_refusal_taxonomy.json"
        md_path = self.out_dir / f"{base}.md"
        latest_md = self.out_dir / "latest_consciousness_refusal_taxonomy.md"
        prom_path = self.out_dir / f"{base}.prom"
        latest_prom = self.out_dir / "latest_consciousness_refusal_taxonomy.prom"
        history_path = self.out_dir / "history.jsonl"

        payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(payload + "\n", encoding="utf-8")
        latest_json.write_text(payload + "\n", encoding="utf-8")
        md = self._build_markdown(result)
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")
        prom_lines = []
        for k, v in result["taxonomy_metrics"].items():
            prom_lines.append(f"aq1_{k} {float(v):.12g}")
        prom_lines.append(f"aq1_taxonomy_initialized {1.0 if result['taxonomy_initialized'] else 0.0}")
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
        taxonomy = self._taxonomy()
        metrics = self._metrics(taxonomy, ctx)
        guards_hold = self._epistemic_guards_hold(ctx["ap10"], ctx["ap9"])
        failed_conditions: list[str] = []
        if metrics["taxonomy_completeness_score"] < 1.0:
            failed_conditions.append("taxonomy_incomplete")
        if metrics["ap_equivalence_dependency_score"] < 1.0:
            failed_conditions.append("ap_equivalence_dependency_unresolved")
        if not guards_hold:
            failed_conditions.append("epistemic_guard_violation")
        taxonomy_initialized = not failed_conditions
        status = "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED" if taxonomy_initialized else "CONSCIOUSNESS_REFUSAL_TAXONOMY_INCOMPLETE"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "axis": "AQ",
            "consciousness_refusal_taxonomy_status": status,
            "taxonomy_initialized": taxonomy_initialized,
            "public_schema_version": self.public_schema_version,
            "scientific_scope": "refusal_cost_taxonomy_only",
            "ap_dependency_status": "AP_RESOLVED" if metrics["ap_equivalence_dependency_score"] == 1.0 else "AP_UNRESOLVED",
            "refusal_taxonomy": taxonomy,
            "status_taxonomy": {
                "admissible_refusal": "Requires empirical evidence without denying AP functional/formal support.",
                "costly_refusal": "Adds explanatory burden after RF* equivalence support.",
                "invalid_refusal": "Violates epistemic guards or ignores no-difference constraints.",
            },
            "taxonomy_metrics": metrics,
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
            "next_recommended_module": "rival_theory_cost_analyzer",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            result["persistence"] = self._persist(result)
        else:
            result["persistence"] = {}
        return result

