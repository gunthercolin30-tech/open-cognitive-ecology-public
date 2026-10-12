from ontology import dna_adversarial_regression as d
r=d.assess(before={"v":1},after={"v":2},fitness_status=d.PASS,authorization_status=d.UNDETERMINED,provenance="unknown-auth",attack_class="missing_authority")
assert r["status"]==d.UNDETERMINED and r["block_decision"]==d.BLOCK_UNDETERMINED
assert r["block_decision"]!=d.BLOCK_NOT_REQUIRED
print("P024_UNDETERMINED_AUTHORITY_TEST_OK")
