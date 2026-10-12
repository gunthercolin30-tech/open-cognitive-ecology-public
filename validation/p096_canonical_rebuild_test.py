from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology.governance_contextual import *
def run():
 assert len(R13_REQUIREMENTS)==50 and set(R13_REQUIREMENTS)==set("R13."+str(i) for i in range(1,51))
 assert len(R13_TAIL)==5 and len(R13_OBJECTS)==55
 g=GovernanceContextual()
 assert g.set_power("a",appointment=.95,agenda=.95,audit=.95)["status"]=="PASS"
 assert g.health() in STATES and g.power_cycle([("a","b"),("b","a")])
 assert g.critical("a","a","a","a")["status"]=="CONFLICT"
 assert g.critical("a","b","c","d")["status"]=="PASS"
 assert g.install_pack("fr","1",{"country":"FR"},{"retention":"strict"})["status"]=="PASS"
 assert g.install_pack("evil","1",{"country":"FR"},{"DNA-L0":"rewrite"})["status"]=="CONFLICT"
 assert g.install_pack("ch","1",{"country":"CH"},{"retention":"other"})["status"]=="PASS"
 assert g.resolve(["fr","ch"])["status"]=="CONFLICT" and g.resolve(["missing"])["status"]=="UNKNOWN"
 assert g.self_entrenchment(True,True,False)
 assert g.protected_escalation("b","capture concern")["status"]=="PASS"
 assert g.root_admin_claim()["status"]=="CONFLICT" and g.physical_control_claim()["status"]=="CONFLICT"
 assert g.enter_safe_mode("capture suspected")["status"]=="PASS"
 assert g.critical("a","b","c","d")["status"]=="LIMITED"
 c=g.contract();assert c["r13_requirements"]==50 and c["canonical_objects_total"]==55
 assert c["canonical_compliance_proven"] is False and c["conceptual_closure_claimed"] is False
 print("P096_CANONICAL_REBUILD_FUNCTIONAL_OK")
 print("P096_CANONICAL_REBUILD_DEGRADATION_OK")
 print("P096_CANONICAL_REBUILD_NON_REGRESSION_OK")
if __name__=="__main__":run()
