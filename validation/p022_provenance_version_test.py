from ontology import dna_versioning_lineage as d
m=d.lineage_manifest()
assert m["version"]=="P022-v1" and m["schema_version"]=="oce.p022.dna_versioning_lineage.v1" and m["scope"]=="P022_ONLY"
assert m["transversal_referentials"]["doctrines"]==("R2","R4","R11","R18","R21")
assert m["transversal_referentials"]["artifacts"]==("A-CANON","A-TRACE","A-NONLOSS")
assert m["transversal_referentials"]["world_models_dependency"] is None
assert m["boundaries"]["does_not_define_p023_fitness_suite"] and m["boundaries"]["does_not_define_p024_adversarial_campaign"]
print("P022_PROVENANCE_VERSION_TEST_OK")
