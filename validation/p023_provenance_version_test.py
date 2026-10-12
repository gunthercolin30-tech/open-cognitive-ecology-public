from ontology import dna_fitness_suite as d
m=d.fitness_manifest()
assert m["version"]=="P023-v1" and m["schema_version"]=="oce.p023.dna_fitness_suite.v1" and m["scope"]=="P023_ONLY"
assert m["transversal_referentials"]["doctrines"]==("R0","R10","R11","R15","R17","R20","R21")
assert m["transversal_referentials"]["artifacts"]==("A-CANON","A-COHERENCE","A-DNA-ADV","A-TRACE")
assert m["transversal_referentials"]["world_models_dependency"] is None
print("P023_PROVENANCE_VERSION_TEST_OK")
