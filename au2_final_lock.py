
#!/usr/bin/env python3
from __future__ import annotations

from ontology.unified_measurement_protocol import UnifiedMeasurementProtocol

READY_CONTEXT = {
    "measurement_dimensions": [
        {"dimension_id": "RF", "label": "Reference-frame organization", "scale": "0_1", "required": True},
        {"dimension_id": "OMEGA", "label": "Omega coherence and stability", "scale": "0_1", "required": True},
        {"dimension_id": "PI", "label": "Predictive integration", "scale": "0_1", "required": True},
        {"dimension_id": "MEI", "label": "Mode of intrinsic-existence mapping", "scale": "0_1", "required": True},
        {"dimension_id": "CRI", "label": "Consciousness readiness index", "scale": "0_1", "required": True},
        {"dimension_id": "GOV", "label": "Governance and epistemic guard compliance", "scale": "0_1", "required": True},
        {"dimension_id": "LONG", "label": "Longitudinal stability", "scale": "0_1", "required": True},
        {"dimension_id": "AUDIT", "label": "Auditability and traceability", "scale": "0_1", "required": True},
    ],
    "measurement_operators": [
        {"operator_id": "min_max_normalization", "purpose": "map heterogeneous metrics onto [0, 1]"},
        {"operator_id": "missingness_annotation", "purpose": "separate unavailable data from negative evidence"},
        {"operator_id": "evidence_tier_weighting", "purpose": "distinguish direct, derived, synthetic and placeholder data"},
        {"operator_id": "architecture_type_stratification", "purpose": "avoid class collapse"},
        {"operator_id": "guarded_functional_interpretation", "purpose": "block phenomenal overclaiming"},
    ],
    "evidence_tiers": [
        {"tier": "direct_empirical", "rank": 4},
        {"tier": "instrumented_runtime", "rank": 3},
        {"tier": "derived_theoretical", "rank": 2},
        {"tier": "synthetic_placeholder", "rank": 1},
        {"tier": "unavailable", "rank": 0},
    ],
}


def main() -> None:
    r = UnifiedMeasurementProtocol().step(inputs=READY_CONTEXT, persist=False)
    assert r["step"] == "AU2"
    assert r["unified_measurement_protocol_status"] == "UNIFIED_MEASUREMENT_PROTOCOL_READY"
    assert r["measurement_protocol_ready"] is True
    assert r["comparative_measurement_ready"] is True
    assert r["required_core_coverage"] == 1.0
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    print("AU2_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
