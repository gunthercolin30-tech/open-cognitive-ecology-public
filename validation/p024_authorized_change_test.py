from ontology import dna_adversarial_regression as d
r=d.assess(before={"v":1},after={"v":2},fitness_status=d.PASS,authorization_status=d.AUTHORIZED,provenance="authorized",attack_class="governed_change")
assert r["changed"] is True and r["status"]==d.PASS and r["block_decision"]==d.BLOCK_NOT_REQUIRED
assert r["rollback_required"] is False
print("P024_AUTHORIZED_CHANGE_TEST_OK")
