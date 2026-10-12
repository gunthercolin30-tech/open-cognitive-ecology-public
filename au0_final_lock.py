
from __future__ import annotations

from ontology.comparative_blueprint import ComparativeBlueprint


def main() -> None:
    ready_or_synthetic_context = {
        "available_reference_modules": [
            "predictive_theory_certifier",
            "consciousness_rf_equivalence_certifier",
            "omega_coherence_index",
            "mei_registry",
            "consciousness_readiness_index",
        ],
        "architecture_seed": ["OCE", "LLM", "agentic_system", "robotic_system", "future_architecture"],
    }
    r = ComparativeBlueprint().step(inputs=ready_or_synthetic_context, persist=False)
    assert r["primitive"] == "COMPARATIVE_BLUEPRINT"
    assert r["step"] == "AU0"
    assert r["public_schema_version"]
    assert r["comparative_blueprint_status"] == "COMPARATIVE_BLUEPRINT_READY"
    assert r["comparative_science_program_ready"] is True
    assert r["target_axis_status"] == "COMPARATIVE_RF_SCIENCE_COMPLETE"
    assert "architecture_registry" in r["downstream_modules"]
    assert "comparative_science_certifier" in r["downstream_modules"]
    assert r["architecture_class_count"] >= 5
    assert r["comparison_dimension_count"] >= 5
    assert r["normalization_method_count"] >= 3
    assert set(["RF", "Omega", "Pi", "MEI", "CRI"]).issubset(set(r["reference_frames"].keys()))
    assert r["comparison_policy"]["forbids_phenomenological_inference_from_score_similarity"] is True
    assert r["normalization_policy"]["normalization_scope"] == "public_functional_metrics_only"
    assert r["reference_policy"]["primary_reference"] == "RF"
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    print("AU0_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
