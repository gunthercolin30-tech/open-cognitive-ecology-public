from ontology.semantic_status_schema import SemanticStatusSchema

s = SemanticStatusSchema()

for _ in range(100):
    r = s.step(inputs={}, persist=False)
    assert r["semantic_status_schema_status"] == "SEMANTIC_STATUS_SCHEMA_ESTABLISHED"
    assert r["functional_conclusion_only"] is True

print("AO1_DEGRADATION_100_OK")
