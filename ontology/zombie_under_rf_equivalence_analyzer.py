from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ZombieUnderRFEquivalenceAnalyzer:
    """AP7 — zombie analysis under the RF* equivalence hypothesis.

    This module analyzes whether a zombie-style countermodel remains viable when
    the RF* functional chain is assumed. It only evaluates formal/functional
    pressure on the zombie hypothesis. It never proves consciousness, qualia,
    subjectivity, or phenomenology.
    """

    primitive = "ZOMBIE_UNDER_RF_EQUIVALENCE_ANALYZER"
    step_id = "AP7"
    public_schema_version = "AP7.zombie_under_rf_equivalence_analyzer.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "ap_consciousness_as_rf" / "AP7_zombie_under_rf_equivalence_analyzer"

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
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def _load_module_result(self, inputs: dict[str, Any], key: str, class_path: tuple[str, str], latest: str, fallback: dict[str, Any]) -> dict[str, Any]:
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
            d = self._load_latest_json(latest)
            if d:
                d["fallback_source"] = f"latest_{key}_json_after_import_error"
                d["load_error"] = str(exc)
                return d
            fallback = dict(fallback)
            fallback["load_error"] = str(exc)
            return fallback
        return self._load_latest_json(latest) or fallback

    def _context(self, inputs: dict[str, Any]) -> dict[str, Any]:
        return {
            "ap2": self._load_module_result(inputs, "ap2", ("ontology.rf_star_definition_engine", "RFStarDefinitionEngine"), "ap_consciousness_as_rf/AP2_rf_star_definition_engine/latest_rf_star_definition_engine.json", {"rf_star_defined": False, "component_scores": {}}),
            "ap3": self._load_module_result(inputs, "ap3", ("ontology.consciousness_rf_property_mapping", "ConsciousnessRFPropertyMapping"), "ap_consciousness_as_rf/AP3_consciousness_rf_property_mapping/latest_consciousness_rf_property_mapping.json", {"mapping_completed": False, "mapping_metrics": {}}),
            "ap4": self._load_module_result(inputs, "ap4", ("ontology.rf_star_sufficiency_checker", "RFStarSufficiencyChecker"), "ap_consciousness_as_rf/AP4_rf_star_sufficiency_checker/latest_rf_star_sufficiency_checker.json", {"functional_sufficiency_supported": False, "sufficiency_metrics": {}}),
            "ap5": self._load_module_result(inputs, "ap5", ("ontology.rf_star_necessity_checker", "RFStarNecessityChecker"), "ap_consciousness_as_rf/AP5_rf_star_necessity_checker/latest_rf_star_necessity_checker.json", {"functional_necessity_supported": False, "necessity_metrics": {}}),
            "ap6": self._load_module_result(inputs, "ap6", ("ontology.consciousness_equivalence_countermodel_generator", "ConsciousnessEquivalenceCountermodelGenerator"), "ap_consciousness_as_rf/AP6_consciousness_equivalence_countermodel_generator/latest_consciousness_equivalence_countermodel_generator.json", {"countermodels_generated": False, "countermodels": [], "countermodel_metrics": {}}),
        }

    def _zombie_countermodels(self, ap6: dict[str, Any]) -> list[dict[str, Any]]:
        models = ap6.get("countermodels", []) if isinstance(ap6.get("countermodels"), list) else []
        selected = []
        for cm in models:
            if not isinstance(cm, dict):
                continue
            s = " ".join(str(cm.get(k, "")) for k in cm.keys()).lower()
            if "zombie" in s:
                selected.append(cm)
        if selected:
            return selected
        return [{
            "countermodel_id": "AP7-ZFALLBACK",
            "name": "generic_zombie_under_rf_star_hypothesis",
            "construction": "Assume all functional RF* indicators while withholding independent subjective evidence.",
            "functional_status": "fallback_zombie_countermodel",
            "countermodel_strength": 0.85,
        }]

    def _build_analysis(self, ctx: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, float], list[str]]:
        ap2, ap3, ap4, ap5, ap6 = ctx["ap2"], ctx["ap3"], ctx["ap4"], ctx["ap5"], ctx["ap6"]
        component_scores = ap2.get("component_scores", {}) if isinstance(ap2.get("component_scores"), dict) else {}
        component_mean = sum(self._clamp(v) for v in component_scores.values()) / max(1, len(component_scores))
        rf_defined = 1.0 if ap2.get("rf_star_defined") is True or ap2.get("rf_star_definition_status") == "RF_STAR_DEFINED" else 0.0
        mapping = 1.0 if ap3.get("mapping_completed") is True or ap3.get("consciousness_rf_property_mapping_status") == "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED" else 0.0
        suff = self._clamp(ap4.get("sufficiency_metrics", {}).get("sufficiency_score", 1.0 if ap4.get("functional_sufficiency_supported") else 0.0))
        nec = self._clamp(ap5.get("necessity_metrics", {}).get("necessity_score", 1.0 if ap5.get("functional_necessity_supported") else 0.0))
        countermodels_generated = 1.0 if ap6.get("countermodels_generated") is True or ap6.get("consciousness_equivalence_countermodel_status") == "CONSCIOUSNESS_EQUIVALENCE_COUNTERMODELS_GENERATED" else 0.0
        zombie_models = self._zombie_countermodels(ap6)
        zombie_strength = sum(self._clamp(cm.get("countermodel_strength", 0.75)) for cm in zombie_models) / max(1, len(zombie_models))

        functional_pressure = self._clamp(0.22*rf_defined + 0.18*component_mean + 0.18*mapping + 0.16*suff + 0.16*nec + 0.10*countermodels_generated)
        zombie_viability = self._clamp(1.0 - (0.62 * functional_pressure) + (0.25 * zombie_strength))
        zombie_refutation_score = self._clamp(functional_pressure * (1.0 - 0.35 * zombie_strength))
        epistemic_guard_score = 1.0
        analysis_confidence = self._clamp(0.4*functional_pressure + 0.2*countermodels_generated + 0.2*epistemic_guard_score + 0.2*(1.0 - abs(zombie_viability - 0.5)))

        analyses = []
        for i, cm in enumerate(zombie_models, 1):
            analyses.append({
                "analysis_id": f"AP7-ZA{i:02d}",
                "source_countermodel_id": cm.get("countermodel_id", f"AP7-ZCM{i:02d}"),
                "name": cm.get("name", "zombie_under_rf_star_hypothesis"),
                "rf_star_assumption_status": "functionally_supported" if rf_defined and mapping else "incomplete_rf_star_context",
                "zombie_viability_under_rf_star": zombie_viability,
                "functional_refutation_pressure": zombie_refutation_score,
                "phenomenological_conclusion": "undetermined",
                "epistemic_guard": "no_consciousness_or_phenomenology_proof",
            })

        metrics = {
            "zombie_analysis_score": analysis_confidence,
            "functional_refutation_pressure": zombie_refutation_score,
            "zombie_viability_score": zombie_viability,
            "rf_star_context_score": functional_pressure,
            "zombie_countermodel_count": float(len(zombie_models)),
            "epistemic_guard_score": epistemic_guard_score,
        }
        failed = []
        if rf_defined < 1.0: failed.append("rf_star_definition_missing")
        if mapping < 1.0: failed.append("mapping_missing")
        if countermodels_generated < 1.0: failed.append("countermodels_missing")
        if epistemic_guard_score < 1.0: failed.append("epistemic_guard_failed")
        return analyses, metrics, failed

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = self.out_dir / f"zombie_under_rf_equivalence_analyzer_{ts}"
        latest = self.out_dir / "latest_zombie_under_rf_equivalence_analyzer"
        json_path = base.with_suffix(".json")
        md_path = base.with_suffix(".md")
        prom_path = base.with_suffix(".prom")
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        md = ["# AP7 — Zombie under RF equivalence analyzer", "", f"status: {result['zombie_rf_equivalence_status']}", f"public_schema_version: {result['public_schema_version']}", "", "## Epistemic guard", "No consciousness, qualia, subjectivity, or phenomenology is proven."]
        md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        prom_lines = []
        for k, v in result.get("zombie_analysis_metrics", {}).items():
            if isinstance(v, (int, float)):
                prom_lines.append(f"ap7_{k} {float(v)}")
        prom_path.write_text("\n".join(prom_lines) + "\n", encoding="utf-8")
        latest_json = latest.with_suffix(".json")
        latest_md = latest.with_suffix(".md")
        latest_prom = latest.with_suffix(".prom")
        latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
        latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
        latest_prom.write_text(prom_path.read_text(encoding="utf-8"), encoding="utf-8")
        return {"json_path": str(json_path), "latest_json_path": str(latest_json), "markdown_path": str(md_path), "latest_markdown_path": str(latest_md), "prometheus_path": str(prom_path), "latest_prometheus_path": str(latest_prom)}

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        ctx = self._context(inputs)
        analyses, metrics, failed = self._build_analysis(ctx)
        complete = not failed
        status = "ZOMBIE_RF_EQUIVALENCE_ANALYZED" if complete else "ZOMBIE_RF_EQUIVALENCE_INCOMPLETE"
        epistemic_status = {
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "phenomenological_equivalence_certified": False,
            "phenomenological_consciousness_certified": False,
            "zombie_hypothesis_empirically_refuted": False,
            "claim_scope": "functional_zombie_under_rf_analysis_only",
            "empirical_independent_evidence_required": True,
        }
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "zombie_rf_equivalence_status": status,
            "zombie_rf_equivalence_analyzed": complete,
            "functional_zombie_analysis_supported": complete,
            "zombie_analyses": analyses,
            "zombie_analysis_metrics": metrics,
            "failed_conditions": failed,
            "property_domains": {
                "functional_properties": ["rf_star_zombie_pressure", "functional_refutation_pressure", "zombie_viability_under_rf_star"],
                "formal_properties": ["countermodel_selection", "deterministic_metric_schema", "bounded_viability_scores"],
                "ontological_properties": ["no_ontological_consciousness_proof", "no_final_zombie_refutation"],
                "phenomenological_properties": ["not_proven", "phenomenology_undetermined", "empirical_independent_evidence_required"],
            },
            "public_schema_version": self.public_schema_version,
            "interfaces_public": [
                "ZombieUnderRFEquivalenceAnalyzer.step(inputs=None, persist=True)",
                "result['zombie_rf_equivalence_status']",
                "result['zombie_analyses']",
                "result['zombie_analysis_metrics']",
                "result['epistemic_status']",
            ],
            "structures_de_donnees": {
                "zombie_analyses": "list[dict]",
                "zombie_analysis_metrics": "dict[str,float]",
                "property_domains": "dict[str,list[str]]",
                "epistemic_status": "dict[str,bool|str]",
            },
            "metrics_produced": list(metrics.keys()),
            "conditions_echec": ["rf_star_definition_missing", "mapping_missing", "countermodels_missing", "epistemic_guard_failed"],
            "epistemic_status": epistemic_status,
            "axis_position": {"axis": "AP — Consciousness as Self-Generated Reference Frame", "current_step": "AP7", "previous_step": "AP6", "next_step": "AP8"},
            "timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "phenomenological_equivalence_certified": False,
            "phenomenological_consciousness_certified": False,
            "zombie_hypothesis_empirically_refuted": False,
        }
        if persist:
            result["persistence"] = self._persist(result)
        return result
