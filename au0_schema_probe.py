from ontology.comparative_blueprint import ComparativeBlueprint

r = ComparativeBlueprint().step(persist=False)

print("AU0_KEYS:")
for k in sorted(r.keys()):
    print("-", k)
