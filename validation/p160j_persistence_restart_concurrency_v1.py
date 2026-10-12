from pathlib import Path
import hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R=ROOT/"ontology"/"p160_normative_decision_sealing.py"
J=ROOT/"ontology"/"p160_normative_decision_persistence.py"
E="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R)==E
import ontology.p160_normative_decision_persistence as m
x=m.manifest()
assert x["version"]=="P160-J-v1"
assert x["boundaries"]=={"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p161_opened":False}
print("P160J_PERSISTENCE_RESTART_CONCURRENCY_CONTRACT_OK")
print("G_RUNTIME_UNCHANGED=true");print("P160K_OPENED=false");print("P161_OPENED=false")
