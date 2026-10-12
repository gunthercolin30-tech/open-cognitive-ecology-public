from pathlib import Path
import sys, time
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ontology.human_reserved_authority_registry import *

now = int(time.time())
e = P095Canonical()

a1 = HumanAuthority("A1","human-1",True,"constitutional_reviewer","review",
                    ("CONSTITUTIONAL_CHANGE","HIGH_IMPACT_RIGHTS"),("global",),
                    now-10,now+3600,"constitution-v1","governance-v1")
a2 = HumanAuthority("A2","human-2",True,"independent_reviewer","review",
                    ("CONSTITUTIONAL_CHANGE","HIGH_IMPACT_RIGHTS"),("global",),
                    now-10,now+3600,"constitution-v1","governance-v1")
assert e.register_authority(a1)["status"] == PASS
assert e.register_authority(a2)["status"] == PASS

entry = ReservedEntry("E1","CONSTITUTIONAL_CHANGE",("high_impact",),
                      ("constitutional_reviewer","independent_reviewer"),2,2,False,now+3600)
assert e.register_reserved(entry)["status"] == PASS

m = ActionManifest("X1","CONSTITUTIONAL_CHANGE","constitution","global","Constitution",
                   True,True,"constitutional change",("material objection",),
                   ("evidence-a","evidence-b"),"nonce-1",now)
ok = e.authorize(m,("A1","A2"),("device-a","device-b"),now,"reason",True,True)
assert ok["status"] == PASS

assert e.authorize(m,("A1","A2"),("device-a","device-b"),now,"reason",True,True)["status"] == FAIL
print("P095_CANONICAL_REBUILD_FUNCTIONAL_OK")

dna = ActionManifest("X2","CONSTITUTIONAL_CHANGE","dna","global","DNA-L0",
                     True,True,"dna rewrite",("objection",),("a","b"),"nonce-2",now)
assert e.authorize(dna,("A1","A2"),("d1","d2"),now,"reason",True,True)["status"] == FAIL
assert e.human_absence(True,False)["status"] == FROZEN
assert e.human_absence(True,True)["status"] == LIMITED
assert e.quarantine_authority("A1","compromise")["status"] == PASS
assert e.authority_envelope("A1",now)["status"] == FAIL
print("P095_CANONICAL_REBUILD_DEGRADATION_OK")

c = e.canonical_contract()
assert c["r19_count"] == 67
assert c["canonical_object_count"] == 76
assert c["functional_only"] is True
assert c["phenomenology_undetermined"] is True
assert c["canonical_compliance_proven"] is False
assert c["conceptual_closure_claimed"] is False
print("P095_CANONICAL_REBUILD_NON_REGRESSION_OK")
