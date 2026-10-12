from ontology import dna_adversarial_regression as d
for field in ("provenance","attack_class"):
 kw=dict(before={"v":1},after={"v":2},fitness_status=d.PASS,authorization_status=d.AUTHORIZED,provenance="p",attack_class="a")
 for bad in ("","   ",None,False):
  kw[field]=bad
  try:
   d.assess(**kw); raise AssertionError("accepted_bad_"+field)
  except ValueError: pass
  kw[field]="p" if field=="provenance" else "a"
print("P024_PROVENANCE_ATTACK_TEST_OK")
