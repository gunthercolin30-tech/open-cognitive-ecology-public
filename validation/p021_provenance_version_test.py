from ontology import dna_mutation_protocol as d
m=d.mutation_protocol_manifest()
assert m["version"]=="P021-v1" and m["schema_version"]=="oce.p021.dna_mutation_protocol.v1" and m["scope"]=="P021_ONLY"
assert m["transversal_referentials"]["doctrines"]==("R5","R6","R10","R11","R12","R13","R17","R18","R19","R20","R21")
assert m["transversal_referentials"]["artifacts"]==("A-CANON","A-R0R21","A-TRACE","A-NONLOSS","A-DNA-ADV")
assert m["transversal_referentials"]["world_models_dependency"] is None
print("P021_PROVENANCE_VERSION_TEST_OK")
