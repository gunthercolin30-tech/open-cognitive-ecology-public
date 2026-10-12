from ontology.architecture_registry import ArchitectureRegistry

r = ArchitectureRegistry().step(persist=False)

assert r["architecture_count"] >= 4
assert r["architecture_type_count"] >= 4
assert len(r["registered_architecture_ids"]) == r["architecture_count"]
assert len(r["registered_architecture_types"]) == r["architecture_type_count"]

print("AU1_NUMERIC_FINAL_LOCK_OK")
