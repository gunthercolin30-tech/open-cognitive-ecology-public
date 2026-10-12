from ontology.theorem_dependency_mapper import TheoremDependencyMapper

r = TheoremDependencyMapper().step(persist=False)

assert r["theorem_dependency_mapping_status"] == "THEOREM_DEPENDENCIES_MAPPED"
assert r["step"] == "AN6"

for key in [
    "theorem_dependency_graph",
    "axiom_usage",
    "minimal_proof_dependencies",
    "redundant_proof_paths",
]:
    assert key in r

assert isinstance(r["theorem_dependency_graph"], dict)
assert isinstance(r["axiom_usage"], dict)
assert isinstance(r["minimal_proof_dependencies"], dict)
assert isinstance(r["redundant_proof_paths"], list)

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False

print("AN6_EXTRA_VALIDATION_SUITE_OK")
