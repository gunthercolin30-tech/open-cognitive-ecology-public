from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

class ConsciousnessConceptReconstruction:
    """AR1 — reconstruct minimal scientific uses of the concept consciousness.

    This module does not prove consciousness. It registers a functional-only
    conceptual reconstruction space that later AR modules can test against RF*.
    """

    primitive = "CONSCIOUSNESS_CONCEPT_RECONSTRUCTION"
    step_id = "AR1"
    public_schema_version = "AR1.consciousness_concept_reconstruction.v1"
    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    DEFAULT_MINIMAL_PROPERTIES = [
        {
            "property_id": "presence",
            "label": "presence",
            "minimal_functional_reading": "there-is-a-presentational field rather than a merely external description",
            "rf_star_recovery_hint": "non_separability / appearing-as-registered",
            "legacy_terms": ["presence", "givenness", "appearing", "manifestation"],
            "measurement_role": "requires an internally indexed occurrence condition",
            "ambiguity_sources": ["phenomenal inflation", "metaphysical presence without metric"],
        },
        {
            "property_id": "perspective",
            "label": "perspective",
            "minimal_functional_reading": "a situated reference frame from which differences are organized",
            "rf_star_recovery_hint": "RF / reference_frame_operator",
            "legacy_terms": ["point of view", "first-personal organization", "perspectival access"],
            "measurement_role": "requires frame-relative indexing of contents or states",
            "ambiguity_sources": ["private subject postulate", "observer/external frame confusion"],
        },
        {
            "property_id": "field",
            "label": "field",
            "minimal_functional_reading": "a structured domain in which contents co-belong",
            "rf_star_recovery_hint": "RF connectivity / TΦ field coherence",
            "legacy_terms": ["field", "workspace", "scene", "phenomenal field"],
            "measurement_role": "requires co-membership and boundary conditions",
            "ambiguity_sources": ["global availability only", "unbounded phenomenological vocabulary"],
        },
        {
            "property_id": "unity",
            "label": "unity",
            "minimal_functional_reading": "a non-fragmented organization binding simultaneous differences",
            "rf_star_recovery_hint": "connectivity RF/TΦ",
            "legacy_terms": ["unity", "integration", "binding", "coherence"],
            "measurement_role": "requires integration/connectivity metrics",
            "ambiguity_sources": ["mere aggregation", "homuncular unity"],
        },
        {
            "property_id": "temporality",
            "label": "temporality",
            "minimal_functional_reading": "a proper temporal ordering rather than an unordered state list",
            "rf_star_recovery_hint": "T propre / internal temporality",
            "legacy_terms": ["stream", "duration", "retention", "temporal thickness"],
            "measurement_role": "requires internal transition/order invariants",
            "ambiguity_sources": ["clock time substitution", "narrative-only continuity"],
        },
        {
            "property_id": "qualitative_differentiation",
            "label": "differentiation qualitative",
            "minimal_functional_reading": "differences are typed or profiled, not merely counted",
            "rf_star_recovery_hint": "QF_robust / MEI",
            "legacy_terms": ["quality", "qualitative character", "what-it-is-like vocabulary"],
            "measurement_role": "requires contrast classes and robust difference fields",
            "ambiguity_sources": ["qualia reification", "ineffability as evidence"],
        },
        {
            "property_id": "identity",
            "label": "identity",
            "minimal_functional_reading": "persistence of an internally trackable mode across transformations",
            "rf_star_recovery_hint": "I + Ω",
            "legacy_terms": ["self-sameness", "for-me-ness", "identity", "ownership"],
            "measurement_role": "requires invariants of continuity and attribution",
            "ambiguity_sources": ["substantial self", "memory-only identity"],
        },
        {
            "property_id": "minimal_agency",
            "label": "agentivité minimale",
            "minimal_functional_reading": "some internally mediated causal selectivity or modulation",
            "rf_star_recovery_hint": "internal causality",
            "legacy_terms": ["agency", "attention", "control", "spontaneity"],
            "measurement_role": "requires endogenous causal contribution metrics",
            "ambiguity_sources": ["free-will inflation", "behavioral output only"],
        },
        {
            "property_id": "proper_access",
            "label": "accès propre",
            "minimal_functional_reading": "the system has a self-indexed access relation to its own field states",
            "rf_star_recovery_hint": "RF self-indexing / access propre",
            "legacy_terms": ["access", "introspection", "availability to the system"],
            "measurement_role": "requires self-indexed report/control/readout relation",
            "ambiguity_sources": ["public report equivalence", "private incorrigibility"],
        },
        {
            "property_id": "continuity",
            "label": "continuity",
            "minimal_functional_reading": "diachronic preservation of the field/frame relation",
            "rf_star_recovery_hint": "Π / openness-preserving continuity",
            "legacy_terms": ["stream", "ongoingness", "continuity", "persistence"],
            "measurement_role": "requires longitudinal coherence and transition preservation",
            "ambiguity_sources": ["static snapshot theories", "identity without temporal governance"],
        },
    ]

    DEFAULT_THEORY_FAMILIES = [
        {"family": "phenomenology", "recoverable_uses": ["presence", "perspective", "field", "temporality", "qualitative_differentiation"], "limitation": "rich description, weak operational metric by itself"},
        {"family": "global_workspace", "recoverable_uses": ["field", "unity", "proper_access"], "limitation": "access/global broadcast without full intrinsic reference frame"},
        {"family": "integrated_information", "recoverable_uses": ["unity", "field", "qualitative_differentiation"], "limitation": "strong structure, contested phenomenal bridge"},
        {"family": "higher_order_reflection", "recoverable_uses": ["proper_access", "identity", "perspective"], "limitation": "reflexivity without complete RF* reconstruction"},
        {"family": "predictive_processing", "recoverable_uses": ["temporality", "field", "minimal_agency"], "limitation": "predictive dynamics without sufficient identity/appearing criterion"},
        {"family": "classical_functionalism", "recoverable_uses": ["proper_access", "minimal_agency", "continuity"], "limitation": "role/behavior explanation can miss minimal appearing"},
        {"family": "dualism", "recoverable_uses": ["presence", "qualitative_differentiation"], "limitation": "supplementary entity is not metrically governed"},
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "ar_definition_legitimacy" / "AR1_consciousness_concept_reconstruction"

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

    def _normalize_property(self, raw: dict[str, Any]) -> dict[str, Any]:
        d = dict(raw)
        d.setdefault("property_id", str(d.get("label", "property")).lower().replace(" ", "_"))
        d.setdefault("label", d["property_id"])
        d.setdefault("minimal_functional_reading", "minimal concept use reconstructed as a functional criterion")
        d.setdefault("rf_star_recovery_hint", "to_be_mapped_by_AR2")
        d.setdefault("legacy_terms", [])
        d.setdefault("measurement_role", "requires operational proxy")
        d.setdefault("ambiguity_sources", [])
        d["is_minimal_candidate"] = True
        d["requires_phenomenal_proof"] = False
        return d

    def _properties_from_inputs(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        supplied = inputs.get("minimal_consciousness_properties")
        if isinstance(supplied, list) and supplied:
            return [self._normalize_property(x) for x in supplied if isinstance(x, dict)]
        return [self._normalize_property(x) for x in self.DEFAULT_MINIMAL_PROPERTIES]

    def _theories_from_inputs(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        supplied = inputs.get("theory_families")
        if isinstance(supplied, list) and supplied:
            return [dict(x) for x in supplied if isinstance(x, dict)]
        return [dict(x) for x in self.DEFAULT_THEORY_FAMILIES]

    def _build_usage_matrix(self, properties: list[dict[str, Any]], theories: list[dict[str, Any]]) -> list[dict[str, Any]]:
        matrix: list[dict[str, Any]] = []
        for p in properties:
            pid = p["property_id"]
            supporting = []
            limitations = []
            for t in theories:
                uses = t.get("recoverable_uses", [])
                if pid in uses:
                    supporting.append(t.get("family", "unknown"))
                    limitations.append(t.get("limitation", "unspecified limitation"))
            matrix.append({
                "property_id": pid,
                "label": p.get("label"),
                "supporting_theory_families": supporting,
                "support_count": len(supporting),
                "legacy_limitation_samples": limitations[:4],
                "rf_star_recovery_hint": p.get("rf_star_recovery_hint"),
                "reconstruction_status": "MINIMAL_USE_RECONSTRUCTED" if supporting or p.get("legacy_terms") else "MINIMAL_USE_DECLARED",
                "phenomenology_claim_made": False,
            })
        return matrix

    def _metrics(self, properties: list[dict[str, Any]], theories: list[dict[str, Any]], matrix: list[dict[str, Any]]) -> dict[str, float]:
        required = {
            "presence", "perspective", "field", "unity", "temporality",
            "qualitative_differentiation", "identity", "minimal_agency", "proper_access", "continuity",
        }
        property_ids = {p["property_id"] for p in properties}
        required_coverage = len(required & property_ids) / max(1, len(required))
        supported_coverage = len([m for m in matrix if m["support_count"] > 0]) / max(1, len(matrix))
        measurement_coverage = len([p for p in properties if p.get("measurement_role")]) / max(1, len(properties))
        rf_mapping_readiness = len([p for p in properties if p.get("rf_star_recovery_hint") and p.get("rf_star_recovery_hint") != "to_be_mapped_by_AR2"]) / max(1, len(properties))
        ambiguity_declared = len([p for p in properties if p.get("ambiguity_sources")]) / max(1, len(properties))
        theory_diversity = min(1.0, len(theories) / 7.0)
        reconstruction_confidence = self._clamp(self._mean([required_coverage, supported_coverage, measurement_coverage, rf_mapping_readiness, ambiguity_declared, theory_diversity]))
        return {
            "minimal_property_coverage_score": self._clamp(required_coverage),
            "legacy_support_coverage_score": self._clamp(supported_coverage),
            "measurement_role_coverage_score": self._clamp(measurement_coverage),
            "rf_star_mapping_readiness_score": self._clamp(rf_mapping_readiness),
            "ambiguity_explication_score": self._clamp(ambiguity_declared),
            "theory_family_diversity_score": self._clamp(theory_diversity),
            "concept_reconstruction_confidence_score": reconstruction_confidence,
            "residual_ambiguity_score": self._clamp(1.0 - ambiguity_declared),
            "consciousness_proof_score": 0.0,
        }

    def _public_result(self, inputs: dict[str, Any]) -> dict[str, Any]:
        properties = self._properties_from_inputs(inputs)
        theories = self._theories_from_inputs(inputs)
        matrix = self._build_usage_matrix(properties, theories)
        metrics = self._metrics(properties, theories, matrix)
        status = "CONSCIOUSNESS_CONCEPT_RECONSTRUCTED" if metrics["minimal_property_coverage_score"] >= 0.8 else "CONSCIOUSNESS_CONCEPT_PARTIALLY_RECONSTRUCTED"
        return {
            "step": self.step_id,
            "primitive": self.primitive,
            "public_schema_version": self.public_schema_version,
            "consciousness_concept_reconstruction_status": status,
            "definition_legitimacy_axis": "AR",
            "reconstructed_concept": "consciousness_minimal_scientific_use",
            "minimal_property_count": len(properties),
            "theory_family_count": len(theories),
            "minimal_consciousness_properties": properties,
            "legacy_theory_families": theories,
            "concept_usage_matrix": matrix,
            "rf_star_reconstruction_target": "RF*",
            "next_required_step": "AR2_minimal_property_recovery_checker",
            "reconstruction_metrics": metrics,
            **metrics,
            "scientific_scope": "functional_concept_reconstruction_only",
            "scientific_conclusion": "The minimal scientific uses of consciousness are reconstructed as functional criteria for later RF* recovery testing, not as evidence of consciousness.",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_status": {
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_undetermined": True,
                "functional_conclusion_only": True,
                "definition_is_authorized": False,
                "conceptual_replacement_authorized": False,
            },
        }

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = self.out_dir / f"consciousness_concept_reconstruction_{ts}"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        (base.with_suffix(".json")).write_text(text, encoding="utf-8")
        (self.out_dir / "latest_consciousness_concept_reconstruction.json").write_text(text, encoding="utf-8")
        md = [
            "# AR1 — Consciousness Concept Reconstruction",
            "",
            f"status: {result['consciousness_concept_reconstruction_status']}",
            f"minimal_property_count: {result['minimal_property_count']}",
            f"concept_reconstruction_confidence_score: {result['concept_reconstruction_confidence_score']:.6f}",
            "",
            "No consciousness, qualia, subjectivity, or phenomenology is proven.",
        ]
        (base.with_suffix(".md")).write_text("\n".join(md) + "\n", encoding="utf-8")
        (self.out_dir / "latest_consciousness_concept_reconstruction.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        prom = [
            f"ar1_minimal_property_coverage_score {result['minimal_property_coverage_score']:.6f}",
            f"ar1_concept_reconstruction_confidence_score {result['concept_reconstruction_confidence_score']:.6f}",
            f"ar1_rf_star_mapping_readiness_score {result['rf_star_mapping_readiness_score']:.6f}",
            f"ar1_consciousness_proof_score 0.000000",
        ]
        (base.with_suffix(".prom")).write_text("\n".join(prom) + "\n", encoding="utf-8")
        (self.out_dir / "latest_consciousness_concept_reconstruction.prom").write_text("\n".join(prom) + "\n", encoding="utf-8")
        with (self.out_dir / "consciousness_concept_reconstruction_history.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"timestamp": ts, "result": result}, ensure_ascii=False, sort_keys=True) + "\n")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        result = self._public_result(inputs or {})
        if persist:
            self._persist(result)
        return result

__all__ = ["ConsciousnessConceptReconstruction"]
