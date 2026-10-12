from ontology import dna_adversarial_regression as d
for bad in ("authorized","TRUE","PASS","UNKNOWN","",None,True,1):
 try:
  d.assess(before={"v":1},after={"v":2},fitness_status=d.PASS,authorization_status=bad,provenance="adv",attack_class="auth_confusion")
  raise AssertionError("accepted_bad_authorization:"+repr(bad))
 except ValueError: pass
print("P024_AUTHORIZATION_CONFUSION_ADVERSARIAL_TEST_OK")
