from ontology import dna_inheritance as d

m = d.inheritance_manifest()
assert m["version"] == "P020-v1"
assert m["schema_version"] == "oce.p020.dna_inheritance.v1"
assert m["scope"] == "P020_ONLY"
assert m["transversal_referentials"]["doctrines"] == (
    "R1", "R2", "R3", "R8", "R9", "R15", "R18", "R19",
)
assert m["transversal_referentials"]["artifacts"] == (
    "A-CANON", "A-R0R21", "A-TRACE", "A-NONLOSS",
)
print("P020_PROVENANCE_VERSION_TEST_OK")
