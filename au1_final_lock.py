
from __future__ import annotations

from ontology.architecture_registry import ArchitectureRegistry


def main() -> None:
    ready_or_synthetic_context = {
        "architectures": [
            {"architecture_id": "OCE_RF_STAR", "architecture_type": "OCE", "display_name": "Open Cognitive Ecology", "available_reference_frames": ["RF", "Omega", "Pi", "MEI", "CRI"]},
            {"architecture_id": "LLM_BASELINE", "architecture_type": "LLM", "display_name": "LLM baseline", "available_reference_frames": ["RF", "Pi", "CRI"]},
            {"architecture_id": "AGENT_BASELINE", "architecture_type": "agentic_system", "display_name": "Agent baseline", "available_reference_frames": ["RF", "Pi", "CRI"]},
            {"architecture_id": "ROBOT_BASELINE", "architecture_type": "robotic_system", "display_name": "Robot baseline", "available_reference_frames": ["RF", "Pi", "CRI"]},
            {"architecture_id": "HUMAN_PLACEHOLDER", "architecture_type": "human_dataset_when_available", "display_name": "Human dataset placeholder", "empirical_human_dataset": True, "available_reference_frames": ["RF", "Omega", "Pi", "MEI", "CRI"]},
            {"architecture_id": "FUTURE_SLOT", "architecture_type": "future_architecture", "display_name": "Future architecture slot", "future_extension_slot": True, "available_reference_frames": ["RF", "Omega", "Pi", "MEI", "CRI"]},
        ]
    }
    r = ArchitectureRegistry().step(inputs=ready_or_synthetic_context, persist=False)
    assert r["primitive"] == "ARCHITECTURE_REGISTRY"
    assert r["step"] == "AU1"
    assert r["public_schema_version"]
    assert r["architecture_registry_status"] == "ARCHITECTURE_REGISTRY_READY"
    assert r["architecture_registry_ready"] is True
    assert r["target_axis_status"] == "COMPARATIVE_RF_SCIENCE_COMPLETE"
    assert r["architecture_count"] >= 6
    assert set(["OCE", "LLM", "agentic_system", "robotic_system", "human_dataset_when_available", "future_architecture"]).issubset(set(r["registered_architecture_types"]))
    assert r["human_dataset_placeholder_registered"] is True
    assert r["future_architecture_slots"] >= 1
    assert r["registration_policy"]["human_architecture_requires_empirical_dataset"] is True
    assert r["normalization_contract"]["profile_builder_target"] == "rf_profile_builder"
    assert "rf_profile_builder" in r["downstream_modules"]
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    print("AU1_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
