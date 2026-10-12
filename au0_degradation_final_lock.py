from ontology.comparative_blueprint import ComparativeBlueprint

bad = {
    "architecture_classes": [],
    "comparison_dimensions": [],
    "normalization_methods": [],
    "reference_frames": [],
}

r = ComparativeBlueprint().step(inputs=bad, persist=False)

assert r["step"] == "AU0"
assert r["comparative_science_program_ready"] is False
assert r["comparative_blueprint_status"] != "COMPARATIVE_BLUEPRINT_READY"
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AU0_DEGRADATION_FINAL_LOCK_OK")
