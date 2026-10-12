from ontology.semantic_revision_log import SemanticRevisionLog

r = SemanticRevisionLog().step(persist=False)

assert r["semantic_revision_log_status"] == "SEMANTIC_REVISION_LOG_ESTABLISHED"
assert r["step"] == "AO4"

joined = "\n".join(r.keys()).lower()
for semantic in ["revision", "log", "semantic"]:
    assert semantic in joined, semantic

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AO4_SCHEMA_INTEGRITY_OK")
