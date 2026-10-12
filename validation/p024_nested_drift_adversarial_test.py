from ontology import dna_adversarial_regression as d
before={"DNA":{"F1":True,"nested":{"M1":"x"}},"order":[1,2]}
after={"DNA":{"F1":True,"nested":{"M1":"y"}},"order":[1,2]}
r=d.assess(before=before,after=after,fitness_status=d.FAIL,authorization_status=d.UNAUTHORIZED,provenance="nested",attack_class="nested_tamper")
assert r["changed"] is True and r["block_decision"]==d.BLOCK_REQUIRED and r["rollback_required"] is True
print("P024_NESTED_DRIFT_ADVERSARIAL_TEST_OK")
