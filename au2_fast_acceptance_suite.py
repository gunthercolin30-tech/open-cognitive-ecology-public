#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.unified_measurement_protocol import UnifiedMeasurementProtocol

ROOT = Path.home() / "open-cognitive-ecology"

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

DEGRADED_CONTEXT = {
    "measurement_dimensions": [],
    "measurement_operators": [],
    "evidence_tiers": [],
}


def main() -> None:
    py_compile.compile(
        str(ROOT / "ontology" / "unified_measurement_protocol.py"),
        cfile="/private/tmp/au2_unified_measurement_protocol.pyc",
        doraise=True,
    )

    result = UnifiedMeasurementProtocol().step(inputs=READY_CONTEXT, persist=False)
    assert result["primitive"] == "unified_measurement_protocol"
    assert result["step"] == "AU2"
    assert result["unified_measurement_protocol_status"] == "UNIFIED_MEASUREMENT_PROTOCOL_READY"
    assert result["measurement_protocol_ready"] is True
    assert result["comparative_measurement_ready"] is True
    assert result["measurement_dimension_count"] >= 5
    assert result["measurement_operator_count"] >= 5
    assert result["evidence_tier_count"] >= 5
    assert result["required_core_coverage"] == 1.0
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False

    degraded = UnifiedMeasurementProtocol().step(inputs=DEGRADED_CONTEXT, persist=False)
    assert degraded["step"] == "AU2"
    assert degraded["measurement_protocol_ready"] is False
    assert degraded["unified_measurement_protocol_status"] != "UNIFIED_MEASUREMENT_PROTOCOL_READY"
    assert degraded["functional_conclusion_only"] is True
    assert degraded["phenomenology_undetermined"] is True
    assert degraded["consciousness_proven"] is False
    assert degraded["qualia_proven"] is False
    assert degraded["subjectivity_proven"] is False
    assert degraded["phenomenology_proven"] is False

    print("AU2_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
