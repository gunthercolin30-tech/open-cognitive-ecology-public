from ontology import dna_adversarial_regression as d
r=d.assess(before={"F1":True},after={"F1":False},fitness_status=d.FAIL,authorization_status=d.UNAUTHORIZED,provenance="unauth",attack_class="invariant_removal")
assert r["status"]==d.FAIL and r["block_decision"]==d.BLOCK_REQUIRED
assert r["regression_detected"] is True and r["rollback_required"] is True
print("P024_UNAUTHORIZED_DRIFT_TEST_OK")
