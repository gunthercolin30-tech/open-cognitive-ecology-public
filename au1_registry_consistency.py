from ontology.architecture_registry import ArchitectureRegistry

r = ArchitectureRegistry().step(persist=False)

assert r["oce_registered"]
assert r["llm_registered"]
assert r["agentic_system_registered"]
assert r["robotic_system_registered"]

print("AU1_REGISTRY_CONSISTENCY_OK")
