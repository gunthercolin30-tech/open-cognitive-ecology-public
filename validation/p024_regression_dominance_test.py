from ontology import dna_adversarial_regression as d
# Even an authorization claim cannot turn demonstrated structural regression into acceptance.
r=d.assess(before={"x":True},after={"x":False},fitness_status=d.FAIL,authorization_status=d.AUTHORIZED,provenance="reg",attack_class="regression")
assert r["status"]==d.FAIL and r["block_decision"]==d.BLOCK_REQUIRED and r["rollback_required"] is True
print("P024_REGRESSION_DOMINANCE_TEST_OK")
