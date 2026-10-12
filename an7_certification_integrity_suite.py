from ontology.axiomatic_completeness_certifier import AxiomaticCompletenessCertifier

r = AxiomaticCompletenessCertifier().step(persist=False)

assert r["axiomatic_completeness_status"] == "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED"
assert r["step"] == "AN7"

assert r["minimal"] is True
assert r["independent"] is True
assert r["non_redundant"] is True
assert r["axiomatically_complete"] is True
assert r["ready_to_close_axis_AN"] is True

assert 0.0 <= r["completeness_score"] <= 1.0

for k, v in r["criterion_scores"].items():
    assert 0.0 <= v <= 1.0, (k, v)

for k, v in r["criterion_passes"].items():
    assert isinstance(v, bool), (k, v)

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AN7_CERTIFICATION_INTEGRITY_OK")
