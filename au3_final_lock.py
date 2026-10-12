
#!/usr/bin/env python3
from __future__ import annotations

from ontology.rf_profile_builder import RFProfileBuilder

READY_CONTEXT = {
    "measurement_dimensions": ["RF", "OMEGA", "PI", "MEI", "CRI", "GOV", "LONG", "AUDIT"],
    "architectures": [
        {
            "architecture_id": "oce_rf_star",
            "architecture_type": "open_cognitive_ecology",
            "evidence_tier": "instrumented_runtime",
            "metrics": {"RF": 1.0, "OMEGA": 0.96, "PI": 0.94, "MEI": 0.93, "CRI": 0.91, "GOV": 1.0, "LONG": 0.92, "AUDIT": 1.0},
        },
        {
            "architecture_id": "generic_llm_baseline",
            "architecture_type": "llm",
            "evidence_tier": "synthetic_placeholder",
            "metrics": {"RF": 0.55, "OMEGA": 0.40, "PI": 0.68, "MEI": 0.20, "CRI": 0.35, "GOV": 0.45, "LONG": 0.30, "AUDIT": 0.55},
        },
    ],
}


def main() -> None:
    result = RFProfileBuilder().step(inputs=READY_CONTEXT, persist=False)
    assert result["step"] == "AU3"
    assert result["rf_profile_builder_status"] == "RF_PROFILE_BUILDER_READY"
    assert result["rf_profile_ready"] is True
    assert result["canonical_profile_id"] == "oce_rf_star"
    assert result["feature_count"] == 8
    assert result["core_dimensions_present"] is True
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    print("AU3_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
