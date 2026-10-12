from ontology.semantic_revision_log import SemanticRevisionLog

r = SemanticRevisionLog().step(persist=False)

print("AO4_KEYS:")
for k in sorted(r.keys()):
    print("-", k)
