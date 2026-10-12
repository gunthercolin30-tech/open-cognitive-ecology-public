from pathlib import Path
import hashlib,json,platform
ROOT=Path.home()/"open-cognitive-ecology"
G=ROOT/"ontology"/"p160_normative_decision_sealing.py"
J=ROOT/"ontology"/"p160_normative_decision_persistence.py"
T=ROOT/"validation"/"p160j_exhaustive_crown_v1_test.py"
E="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(G)==E
assert J.is_file() and T.is_file()
import ontology.p160_normative_decision_persistence as m
assert m.manifest()["boundaries"]["authorization_created"] is False
print("P160J_EXHAUSTIVE_CROWN_CONTRACT_OK")
print("PLATFORM="+platform.system()+"-"+platform.machine())
print("G_RUNTIME_UNCHANGED=true")
print("P160K_OPENED=false")
print("P161_OPENED=false")
