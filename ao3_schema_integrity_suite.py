from ontology.epistemic_guard import EpistemicGuard

r = EpistemicGuard().step(persist=False)

assert r["epistemic_guard_status"] == "EPISTEMIC_GUARD_ESTABLISHED"
assert r["step"] == "AO3"

joined = "\n".join(r.keys()).lower()

for semantic in ["guard", "epistem", "status"]:
    assert semantic in joined, semantic

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AO3_SCHEMA_INTEGRITY_OK")
