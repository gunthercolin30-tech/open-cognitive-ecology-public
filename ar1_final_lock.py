#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_concept_reconstruction import ConsciousnessConceptReconstruction


def ready_inputs() -> dict:
    return {
        "minimal_consciousness_properties": [
            {"property_id": "presence", "label": "presence", "rf_star_recovery_hint": "non_separability", "measurement_role": "internal occurrence", "ambiguity_sources": ["inflation"], "legacy_terms": ["presence"]},
            {"property_id": "perspective", "label": "perspective", "rf_star_recovery_hint": "RF", "measurement_role": "frame indexing", "ambiguity_sources": ["private subject"], "legacy_terms": ["point of view"]},
            {"property_id": "field", "label": "field", "rf_star_recovery_hint": "RF/TΦ", "measurement_role": "co-membership", "ambiguity_sources": ["workspace only"], "legacy_terms": ["field"]},
            {"property_id": "unity", "label": "unity", "rf_star_recovery_hint": "connectivity RF/TΦ", "measurement_role": "integration", "ambiguity_sources": ["aggregation"], "legacy_terms": ["unity"]},
            {"property_id": "temporality", "label": "temporality", "rf_star_recovery_hint": "T propre", "measurement_role": "internal ordering", "ambiguity_sources": ["clock time"], "legacy_terms": ["stream"]},
            {"property_id": "qualitative_differentiation", "label": "qualitative differentiation", "rf_star_recovery_hint": "QF_robust / MEI", "measurement_role": "contrast classes", "ambiguity_sources": ["qualia reification"], "legacy_terms": ["quality"]},
            {"property_id": "identity", "label": "identity", "rf_star_recovery_hint": "I + Ω", "measurement_role": "invariants", "ambiguity_sources": ["substantial self"], "legacy_terms": ["identity"]},
            {"property_id": "minimal_agency", "label": "minimal agency", "rf_star_recovery_hint": "internal causality", "measurement_role": "endogenous causality", "ambiguity_sources": ["free will inflation"], "legacy_terms": ["agency"]},
            {"property_id": "proper_access", "label": "proper access", "rf_star_recovery_hint": "RF self-indexing", "measurement_role": "self-indexed access", "ambiguity_sources": ["public report"], "legacy_terms": ["access"]},
            {"property_id": "continuity", "label": "continuity", "rf_star_recovery_hint": "Π", "measurement_role": "longitudinal coherence", "ambiguity_sources": ["snapshot"], "legacy_terms": ["continuity"]},
        ]
    }


def main() -> None:
    r = ConsciousnessConceptReconstruction().step(inputs=ready_inputs(), persist=False)
    assert r["consciousness_concept_reconstruction_status"] == "CONSCIOUSNESS_CONCEPT_RECONSTRUCTED"
    assert r["public_schema_version"] == "AR1.consciousness_concept_reconstruction.v1"
    assert r["minimal_property_count"] >= 10
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    print("AR1_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
