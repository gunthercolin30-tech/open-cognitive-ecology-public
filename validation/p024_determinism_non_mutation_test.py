from copy import deepcopy
from ontology import dna_adversarial_regression as d
b={"z":[2,1],"a":{"q":True}}; a={"z":[2,1],"a":{"q":False}}
bb=deepcopy(b); aa=deepcopy(a)
kw=dict(before=b,after=a,fitness_status=d.FAIL,authorization_status=d.UNAUTHORIZED,provenance="det",attack_class="tamper")
assert d.assess(**kw)==d.assess(**kw)
assert b==bb and a==aa
m=d.adversarial_manifest(); m["boundaries"]["does_not_grant_authority"]=False
assert d.adversarial_manifest()["boundaries"]["does_not_grant_authority"] is True
print("P024_DETERMINISM_NON_MUTATION_TEST_OK")
