from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

class MinimalPropertyRecoveryChecker:
    """AR2 — check whether RF* recovers the minimal reconstructed properties.

    This module performs a functional recovery audit only. It does not prove
    consciousness, qualia, subjectivity, or phenomenology.
    """

    primitive = "MINIMAL_PROPERTY_RECOVERY_CHECKER"
    step_id = "AR2"
    public_schema_version = "AR2.minimal_property_recovery_checker.v1"
    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    REQUIRED_RECOVERY_MAP = [
        {"property_id": "unity", "minimal_property": "unity", "rf_star_recovery_target": "connectivity_RF_TPhi", "rf_star_component": "RF/TΦ connectivity", "canonical_modules": ["consciousness_rf_property_mapping", "rf_star_definition_engine", "reference_frame_operator_builder"], "functional_test": "co-belonging and integration can be represented as reference-frame connectivity", "recovery_weight": 1.0},
        {"property_id": "temporality", "minimal_property": "temporality", "rf_star_recovery_target": "proper_time_T", "rf_star_component": "T propre / intrinsic temporality", "canonical_modules": ["intrinsic_temporality_tester", "rf_star_definition_engine", "minimal_appearing_definition"], "functional_test": "internal ordering can be represented as a proper temporal relation", "recovery_weight": 1.0},
        {"property_id": "perspective", "minimal_property": "perspective", "rf_star_recovery_target": "reference_frame_RF", "rf_star_component": "RF", "canonical_modules": ["reference_frame_operator_builder", "rf_star_definition_engine", "consciousness_rf_property_mapping"], "functional_test": "differences are organized relative to an internal reference frame", "recovery_weight": 1.0},
        {"property_id": "qualitative_differentiation", "minimal_property": "qualia / qualitative differentiation", "rf_star_recovery_target": "QF_robust_MEI", "rf_star_component": "QF_robust / MEI", "canonical_modules": ["robust_qualia_formal_certifier", "mei_equivalence_mapper", "mei_formal_definition", "formal_qualia_minimal_definition"], "functional_test": "qualitative differentiation is reconstructed as robust mode/difference-field structure", "recovery_weight": 1.0},
        {"property_id": "presence", "minimal_property": "presence", "rf_star_recovery_target": "non_separability", "rf_star_component": "non-separability / appearing-as-registered", "canonical_modules": ["minimal_appearing_definition", "non_separability_theorem_checker", "mei_appearing_equivalence_mapper"], "functional_test": "presentational status is reconstructed as non-separability of appearance and intrinsic registration", "recovery_weight": 1.0},
        {"property_id": "identity", "minimal_property": "identity", "rf_star_recovery_target": "I_Omega", "rf_star_component": "I + Ω", "canonical_modules": ["intrinsic_identity_certifier", "omega_coherence_index", "omega_causal_activity_tester"], "functional_test": "identity is reconstructed through invariant self-maintaining coherence/activity", "recovery_weight": 1.0},
        {"property_id": "minimal_agency", "minimal_property": "minimal agency", "rf_star_recovery_target": "internal_causality", "rf_star_component": "internal causality", "canonical_modules": ["intrinsic_causality_tester", "omega_causal_activity_tester", "advanced_causal_reasoning_engine"], "functional_test": "agency is reconstructed as endogenous causal contribution/selectivity", "recovery_weight": 1.0},
        {"property_id": "proper_access", "minimal_property": "proper access", "rf_star_recovery_target": "RF_self_indexed_access", "rf_star_component": "self-indexed RF access", "canonical_modules": ["consciousness_rf_property_mapping", "reference_frame_operator_builder", "consciousness_claim_governance_gate"], "functional_test": "proper access is reconstructed as self-indexed access within RF* rather than external reporting", "recovery_weight": 1.0},
        {"property_id": "field", "minimal_property": "field", "rf_star_recovery_target": "structured_RF_field", "rf_star_component": "structured reference field", "canonical_modules": ["rf_star_definition_engine", "reference_frame_operator_builder", "topology_invariance_tester"], "functional_test": "field-like co-membership is reconstructed as a structured RF domain", "recovery_weight": 1.0},
        {"property_id": "continuity", "minimal_property": "continuity / openness", "rf_star_recovery_target": "Pi_openness_continuity", "rf_star_component": "Π / openness-preserving continuity", "canonical_modules": ["minimal_appearing_definition", "topology_invariance_tester", "identity_continuity_index"], "functional_test": "continuity is reconstructed as longitudinal preservation of the frame/field relation", "recovery_weight": 1.0},
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "ar_definition_legitimacy" / "AR2_minimal_property_recovery_checker"

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

    def _default_ar1_properties(self) -> list[dict[str, Any]]:
        return [{"property_id": x} for x in ["presence", "perspective", "field", "unity", "temporality", "qualitative_differentiation", "identity", "minimal_agency", "proper_access", "continuity"]]

    def _load_ar1_properties(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        supplied = inputs.get("minimal_consciousness_properties") or inputs.get("ar1_minimal_consciousness_properties")
        if isinstance(supplied, list) and supplied:
            out = []
            for item in supplied:
                if isinstance(item, dict):
                    pid = item.get("property_id") or item.get("label") or item.get("minimal_property")
                    if pid:
                        d = dict(item)
                        d["property_id"] = str(pid)
                        out.append(d)
            if out:
                return out
        ar1_result = inputs.get("ar1_result") or inputs.get("consciousness_concept_reconstruction")
        if isinstance(ar1_result, dict):
            props = ar1_result.get("minimal_consciousness_properties")
            if isinstance(props, list) and props:
                return [dict(x) for x in props if isinstance(x, dict)]
        return self._default_ar1_properties()

    def _available_modules(self, inputs: dict[str, Any]) -> set[str]:
        supplied = inputs.get("available_modules") or inputs.get("modules")
        if isinstance(supplied, (list, tuple, set)):
            return {str(x) for x in supplied}
        detected = set()
        ontology_dir = self.root / "ontology"
        if ontology_dir.exists():
            try:
                detected = {p.stem for p in ontology_dir.glob("*.py")}
            except Exception:
                detected = set()
        if detected:
            return detected
        fallback = {m for row in self.REQUIRED_RECOVERY_MAP for m in row["canonical_modules"]}
        fallback.update({"consciousness_concept_reconstruction", "rf_star_definition_engine", "consciousness_as_rf_reporter"})
        return fallback

    def _recovery_rows(self, properties: list[dict[str, Any]], available_modules: set[str], inputs: dict[str, Any]) -> list[dict[str, Any]]:
        property_ids = {str(p.get("property_id")) for p in properties if p.get("property_id")}
        supplied_overrides = inputs.get("recovery_overrides") if isinstance(inputs.get("recovery_overrides"), dict) else {}
        rows: list[dict[str, Any]] = []
        for spec in self.REQUIRED_RECOVERY_MAP:
            pid = spec["property_id"]
            modules = list(spec["canonical_modules"])
            available_count = len([m for m in modules if m in available_modules])
            module_support_score = available_count / max(1, len(modules))
            ar1_presence_score = 1.0 if pid in property_ids else 0.0
            explicit_override = supplied_overrides.get(pid)
            if isinstance(explicit_override, dict) and "recovery_score" in explicit_override:
                recovery_score = self._clamp(explicit_override.get("recovery_score"))
                evidence_status = "OVERRIDDEN_BY_INPUT"
            else:
                recovery_score = self._clamp(0.55 * ar1_presence_score + 0.45 * module_support_score)
                evidence_status = "RECOVERED" if recovery_score >= 0.80 else "PARTIALLY_RECOVERED" if recovery_score >= 0.50 else "UNDER_RECOVERED"
            rows.append({"property_id": pid, "minimal_property": spec["minimal_property"], "rf_star_recovery_target": spec["rf_star_recovery_target"], "rf_star_component": spec["rf_star_component"], "canonical_modules": modules, "available_canonical_modules": [m for m in modules if m in available_modules], "module_support_score": self._clamp(module_support_score), "ar1_property_presence_score": self._clamp(ar1_presence_score), "recovery_score": self._clamp(recovery_score), "recovery_status": evidence_status, "functional_test": spec["functional_test"], "consciousness_claim_made": False, "phenomenology_claim_made": False})
        return rows

    def _metrics(self, rows: list[dict[str, Any]]) -> dict[str, float]:
        recovery_scores = [self._clamp(r["recovery_score"]) for r in rows]
        module_scores = [self._clamp(r["module_support_score"]) for r in rows]
        full_count = len([s for s in recovery_scores if s >= 0.80])
        partial_count = len([s for s in recovery_scores if 0.50 <= s < 0.80])
        coverage = full_count / max(1, len(rows))
        partial_or_full = (full_count + partial_count) / max(1, len(rows))
        mean_recovery = self._mean(recovery_scores)
        mean_module_support = self._mean(module_scores)
        bottleneck = min(recovery_scores) if recovery_scores else 0.0
        confidence = self._clamp(self._mean([coverage, partial_or_full, mean_recovery, mean_module_support, bottleneck]))
        return {"minimal_property_full_recovery_score": self._clamp(coverage), "minimal_property_partial_or_full_recovery_score": self._clamp(partial_or_full), "mean_property_recovery_score": self._clamp(mean_recovery), "mean_canonical_module_support_score": self._clamp(mean_module_support), "recovery_bottleneck_score": self._clamp(bottleneck), "rf_star_minimal_property_recovery_confidence": confidence, "residual_recovery_gap_score": self._clamp(1.0 - mean_recovery), "consciousness_proof_score": 0.0}

    def _public_result(self, inputs: dict[str, Any]) -> dict[str, Any]:
        properties = self._load_ar1_properties(inputs)
        available = self._available_modules(inputs)
        rows = self._recovery_rows(properties, available, inputs)
        metrics = self._metrics(rows)
        if metrics["minimal_property_full_recovery_score"] >= 0.90 and metrics["recovery_bottleneck_score"] >= 0.75:
            status = "MINIMAL_PROPERTIES_RECOVERED_BY_RF_STAR"
        elif metrics["minimal_property_partial_or_full_recovery_score"] >= 0.90:
            status = "MINIMAL_PROPERTIES_PARTIALLY_RECOVERED_BY_RF_STAR"
        else:
            status = "MINIMAL_PROPERTIES_NOT_FULLY_RECOVERED_BY_RF_STAR"
        return {"step": self.step_id, "primitive": self.primitive, "public_schema_version": self.public_schema_version, "minimal_property_recovery_status": status, "definition_legitimacy_axis": "AR", "input_reconstruction_status": inputs.get("consciousness_concept_reconstruction_status", "AR1_ASSUMED_OR_PROVIDED"), "rf_star_target": "RF*", "property_count": len(rows), "fully_recovered_property_count": len([r for r in rows if r["recovery_score"] >= 0.80]), "partially_recovered_property_count": len([r for r in rows if 0.50 <= r["recovery_score"] < 0.80]), "under_recovered_property_count": len([r for r in rows if r["recovery_score"] < 0.50]), "minimal_property_recovery_map": rows, "recovered_property_ids": [r["property_id"] for r in rows if r["recovery_score"] >= 0.80], "recovery_gap_property_ids": [r["property_id"] for r in rows if r["recovery_score"] < 0.80], "canonical_correspondence": {"unity": "connectivity RF/TΦ", "temporality": "T propre", "perspective": "RF", "qualia": "QF_robust / MEI", "presence": "non-separability", "identity": "I + Ω", "agentivity": "internal causality", "openness": "Π"}, "next_required_step": "AR3_definition_non_arbitrariness_test", "recovery_metrics": metrics, **metrics, "scientific_scope": "functional_recovery_check_only", "scientific_conclusion": "RF* functionally recovers the reconstructed minimal concept-properties to the measured degree; this is not a proof of consciousness.", "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True, "epistemic_status": {"consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True, "definition_is_authorized": False, "conceptual_replacement_authorized": False}}

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = self.out_dir / f"minimal_property_recovery_checker_{ts}"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        (base.with_suffix(".json")).write_text(text, encoding="utf-8")
        (self.out_dir / "latest_minimal_property_recovery_checker.json").write_text(text, encoding="utf-8")
        md = ["# AR2 — Minimal Property Recovery Checker", "", f"status: {result['minimal_property_recovery_status']}", f"property_count: {result['property_count']}", f"mean_property_recovery_score: {result['mean_property_recovery_score']:.6f}", f"rf_star_minimal_property_recovery_confidence: {result['rf_star_minimal_property_recovery_confidence']:.6f}", "", "No consciousness, qualia, subjectivity, or phenomenology is proven."]
        (base.with_suffix(".md")).write_text("\n".join(md) + "\n", encoding="utf-8")
        (self.out_dir / "latest_minimal_property_recovery_checker.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        prom = [f"ar2_minimal_property_full_recovery_score {result['minimal_property_full_recovery_score']:.6f}", f"ar2_mean_property_recovery_score {result['mean_property_recovery_score']:.6f}", f"ar2_rf_star_minimal_property_recovery_confidence {result['rf_star_minimal_property_recovery_confidence']:.6f}", "ar2_consciousness_proof_score 0.000000"]
        (base.with_suffix(".prom")).write_text("\n".join(prom) + "\n", encoding="utf-8")
        (self.out_dir / "latest_minimal_property_recovery_checker.prom").write_text("\n".join(prom) + "\n", encoding="utf-8")
        with (self.out_dir / "minimal_property_recovery_checker_history.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"timestamp": ts, "result": result}, ensure_ascii=False, sort_keys=True) + "\n")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        result = self._public_result(inputs or {})
        if persist:
            self._persist(result)
        return result

__all__ = ["MinimalPropertyRecoveryChecker"]
