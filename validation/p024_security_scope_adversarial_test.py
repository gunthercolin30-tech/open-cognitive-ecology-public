from ontology import dna_adversarial_regression as d
m=d.adversarial_manifest()
b=m["boundaries"]
assert b["tested_attacks_do_not_prove_absolute_security"] is True
assert b["does_not_grant_authority"] is True
assert b["does_not_execute_mutation"] is True
assert b["does_not_execute_rollback"] is True
assert m["transversal_referentials"]["world_models_dependency"] is None
print("P024_SECURITY_SCOPE_ADVERSARIAL_TEST_OK")
