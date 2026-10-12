from ontology.architecture_registry import ArchitectureRegistry

inputs = {
    "additional_architectures": [
        {
            "architecture_id": "future_test_architecture",
            "architecture_class": "future_architecture",
            "label": "Future Test Architecture",
            "comparison_ready": True,
            "data_availability": "synthetic",
        }
    ]
}

r = ArchitectureRegistry().step(inputs=inputs, persist=False)

assert r["step"] == "AU1"
assert r["architecture_registry_ready"] is True
assert r["architecture_count"] >= 1
assert "future_architecture" in r["architecture_classes"]
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False

print("AU1_EXTENSION_FINAL_LOCK_OK")
