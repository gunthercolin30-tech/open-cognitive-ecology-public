from ontology.axiomatic_completeness_certifier import AxiomaticCompletenessCertifier

r = AxiomaticCompletenessCertifier().step(persist=False)

assert r["axiomatic_completeness_status"] == "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED"
assert r["step"] == "AN7"

for key in [
    "minimal",
    "independent",
    "non_redundant",
    "axiomatically_complete",
    "axiomatic_completeness_score",
]:
    assert key in r

assert isinstance(r["minimal"], bool)
assert isinstance(r["independent"], bool)
assert isinstance(r["non_redundant"], bool)
assert isinstance(r["axiomatically_complete"], bool)
assert 0.0 <= r["axiomatic_completeness_score"] <= 1.0

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False

print("AN7_EXTRA_VALIDATION_SUITE_OK")
