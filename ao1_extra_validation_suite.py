from ontology.semantic_status_schema import SemanticStatusSchema

r = SemanticStatusSchema().step(persist=False)

assert r["semantic_status_schema_status"] == "SEMANTIC_STATUS_SCHEMA_ESTABLISHED"
assert r["step"] == "AO1"

assert "authorized_statuses" in r
assert "required_inputs" in r
assert "status_order" in r

for status in [
    "CONSCIOUSNESS_NOT_EVALUATED",
    "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
    "PHENOMENALITY_CANDIDATE_SUPPORTED",
    "QUALIA_IDENTITY_CONDITIONALLY_SUPPORTED",
    "CONSCIOUSNESS_AS_RF_EQUIVALENCE_SUPPORTED",
    "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
    "CONSCIOUSNESS_PROVEN_BEST_THEORY",
    "CONSCIOUSNESS_PROVEN",
    "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
]:
    assert status in r["authorized_statuses"]

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False

print("AO1_EXTRA_VALIDATION_SUITE_OK")
