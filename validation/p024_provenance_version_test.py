from ontology import dna_adversarial_regression as d
m=d.adversarial_manifest()
assert m["version"]=="P024-v1" and m["schema_version"]=="oce.p024.dna_adversarial_regression.v1"
assert m["transversal_referentials"]["doctrines"]==("R0","R5","R21")
assert m["transversal_referentials"]["artifacts"]==("A-CANON","A-COHERENCE","A-DNA-ADV","A-NONLOSS")
assert m["transversal_referentials"]["world_models_dependency"] is None
print("P024_PROVENANCE_VERSION_TEST_OK")
