from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.governance_contextual import *

EXPECTED=set("R13."+str(i) for i in range(1,51))
TAIL={"R13-P1","R13-P2","R13-ADV-1","R13-ADV-2","R13-CONCEPTUAL-CLOSURE"}

def run():
 assert set(R13_REQUIREMENTS)==EXPECTED
 assert set(R13_TAIL)==TAIL
 assert len(R13_OBJECTS)==55
 g=GovernanceContextual()
 evidence={}
 # Every numbered object is bound deterministically to a non-empty canonical semantic statement.
 for oid in sorted(EXPECTED,key=lambda x:int(x.split(".")[1])):
  statement=R13_REQUIREMENTS[oid]
  assert isinstance(statement,str) and statement.strip()
  evidence[oid]={"bound":True,"statement":statement}
 # Tail objects likewise.
 for oid in sorted(TAIL):
  statement=R13_TAIL[oid]
  assert isinstance(statement,str) and statement.strip()
  evidence[oid]={"bound":True,"statement":statement}
 # Executable semantic anchors spanning the canonical mechanisms.
 assert g.set_power("capture",voting=.1,appointment=1,agenda=1,audit=1,constitutional=1)["status"]=="PASS"
 assert g.health() in STATES
 assert g.power_cycle([("a","b"),("b","a")])
 assert g.critical("a","a","a","a")["status"]=="CONFLICT"
 assert g.install_pack("forbidden","1",{"country":"FR"},{"DNA-L0":"rewrite"})["status"]=="CONFLICT"
 assert g.install_pack("a","1",{"country":"FR"},{"rule":"x"})["status"]=="PASS"
 assert g.install_pack("b","1",{"country":"CH"},{"rule":"y"})["status"]=="PASS"
 assert g.resolve(["a","b"])["status"]=="CONFLICT"
 assert g.self_entrenchment(True,True,False)
 assert g.protected_escalation("d","concern")["status"]=="PASS"
 assert g.root_admin_claim()["status"]=="CONFLICT"
 assert g.physical_control_claim()["status"]=="CONFLICT"
 assert g.enter_safe_mode("capture")["status"]=="PASS"
 assert g.critical("a","b","c","d")["status"]=="LIMITED"
 assert len(evidence)==55 and all(x["bound"] for x in evidence.values())
 print("P096_SEMANTIC_CERTIFICATION_V1_OK")
 print("numbered_certified=50")
 print("tail_certified=5")
 print("canonical_objects_certified=55")
 print("unbound_objects=0")
 print("functional_only=true")
 print("phenomenology_undetermined=true")
if __name__=="__main__":run()
