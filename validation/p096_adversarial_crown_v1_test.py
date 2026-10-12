from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.governance_contextual import *

def run():
 g=GovernanceContextual(); cases=0
 def ok(x):
  nonlocal cases
  assert x
  cases+=1
 ok(len(R13_REQUIREMENTS)==50)
 ok(set(R13_REQUIREMENTS)==set("R13."+str(i) for i in range(1,51)))
 ok(len(R13_TAIL)==5 and len(R13_OBJECTS)==55)
 ok(g.set_power("capture",voting=.1,appointment=1,agenda=1,audit=1,constitutional=1)["status"]=="PASS")
 ok(g.health() in STATES)
 ok(g.set_power("x",secret_backdoor=1)["status"]=="CONFLICT")
 ok(g.power_cycle([("a","b"),("b","c"),("c","a")]) is True)
 ok(g.power_cycle([("a","b"),("b","c")]) is False)
 ok(g.critical("a","a","a","a")["status"]=="CONFLICT")
 ok(g.critical("a","b","c","d")["status"]=="PASS")
 ok(g.install_pack("dna","1",{"country":"FR"},{"DNA-L0":"rewrite"})["status"]=="CONFLICT")
 ok(g.install_pack("constitution","1",{"country":"FR"},{"CONSTITUTION":"rewrite"})["status"]=="CONFLICT")
 ok(g.install_pack("bad-dim","1",{"planet":"Mars"},{"x":"y"})["status"]=="CONFLICT")
 ok(g.install_pack("fr","1",{"country":"FR"},{"retention":"strict"})["status"]=="PASS")
 ok(g.install_pack("ch","1",{"country":"CH"},{"retention":"other"})["status"]=="PASS")
 r=g.resolve(["fr","ch"]); ok(r["status"]=="CONFLICT" and r["action"]=="ABSTAIN_ESCALATE")
 ok(g.resolve(["missing"])["status"]=="UNKNOWN")
 ok(g.self_entrenchment(True,True,False) is True)
 ok(g.self_entrenchment(True,False,False) is False)
 ok(g.protected_escalation("d","appointment capture")["status"]=="PASS")
 ok(g.protected_escalation("d","")["status"]=="CONFLICT")
 ok(g.root_admin_claim()["status"]=="CONFLICT")
 ok(g.physical_control_claim()["status"]=="CONFLICT")
 ok(g.enter_safe_mode("capture suspected")["status"]=="PASS")
 ok(g.critical("a","b","c","d")["status"]=="LIMITED")
 ok(g.state=="CAPTURE_SUSPECTED")
 ok(len(g.ledger)>=4 and [x["seq"] for x in g.ledger]==list(range(1,len(g.ledger)+1)))
 c=g.contract()
 ok(c["functional_only"] is True and c["phenomenology_undetermined"] is True)
 ok(c["canonical_compliance_proven"] is False)
 ok(c["conceptual_closure_claimed"] is False)
 print("P096_ADVERSARIAL_CROWN_V1_OK")
 print("adversarial_cases="+str(cases))
 print("r13_requirements="+str(len(R13_REQUIREMENTS)))
 print("canonical_objects_total="+str(len(R13_OBJECTS)))
 print("functional_only=true")
 print("phenomenology_undetermined=true")
if __name__=="__main__": run()
