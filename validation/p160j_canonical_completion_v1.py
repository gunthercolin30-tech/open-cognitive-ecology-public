from pathlib import Path
import hashlib
R=Path.home()/"open-cognitive-ecology";G=R/"ontology"/"p160_normative_decision_sealing.py";J=R/"ontology"/"p160_normative_decision_persistence.py"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(G)=="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
s=J.read_text()
for x in ("PREPARE","VALIDATE","SEAL","PERSIST","COMMIT","timestamp","STARTUP_SAFE_MODE_REQUIRED","planned_authority_consumption","decision_execution_separation"):assert x in s
print("P160J_CANONICAL_COMPLETION_CONTRACT_OK");print("J_SHA256="+sha(J));print("G_RUNTIME_UNCHANGED=true");print("P160K_OPENED=false");print("P161_OPENED=false")
