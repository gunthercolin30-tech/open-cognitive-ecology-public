from ontology.semantic_status_schema import SemanticStatusSchema

r = SemanticStatusSchema().step(persist=False)

print("AO1_KEYS:")
for k in sorted(r.keys()):
    print("-", k)
