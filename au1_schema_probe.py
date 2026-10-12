from ontology.architecture_registry import ArchitectureRegistry

r = ArchitectureRegistry().step(persist=False)

print("AU1_KEYS:")
for k in sorted(r.keys()):
    print("-", k)
