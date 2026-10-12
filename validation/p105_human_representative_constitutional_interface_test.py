import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.human_representative_constitutional_interface import *
from ontology.human_reserved_authority_registry import HumanAuthority,ReservedEntry,ActionManifest,P095Canonical
NOW=200
def setup():
 r=P095Canonical()
 assert r.register_authority(HumanAuthority("AUTH-1","human-1",True,"representative","reserved-governance",("SIGNIFICANT_SANCTION",),("ctx",),100,300,"C1","G1"))["status"]=="PASS"
 assert r.register_reserved(ReservedEntry("RES-1","SIGNIFICANT_SANCTION",("critical",),("representative",),1,1,False,300))["status"]=="PASS"
 return HumanRepresentativeConstitutionalInterface(r)
def act(n="n1"): return ActionManifest("A1","SIGNIFICANT_SANCTION","obj","ctx","Constitution",False,True,"risk",("objection",),("ev1","ev2"),n,NOW)
def main():
 x=setup().examine(manifest=act(),authority_ids=("AUTH-1",),independent_domains=("d1",),now=NOW,rationale="bounded",explicit_confirmation=True,evidence=("ev1","ev2"))
 assert x["status"]=="PASS" and x["action"]=="APPROVE" and not x["execution_permitted"]
 c=setup().examine(manifest=act("n2"),authority_ids=("AUTH-1",),independent_domains=("d1",),now=NOW,rationale="x",explicit_confirmation=True,normative_status="CONFLICT")
 assert c["status"]=="CONFLICT" and c["action"]=="ABSTAIN_AND_ESCALATE"
 b=setup().examine(manifest=act("n3"),authority_ids=("UNKNOWN",),independent_domains=("d1",),now=NOW,rationale="x",explicit_confirmation=True)
 assert b["status"]!="PASS"
 a=setup().human_absence(requires_human=True); assert a["status"]=="UNDETERMINED" and not a["execution_permitted"]
 m=manifest(); assert not m["boundaries"]["human_representative_is_unlimited_root"] and not m["boundaries"]["renderer_holds_authority_logic"] and m["boundaries"]["does_not_implement_p106_amendment_protocol"]
 rec=setup().request_recourse({"mechanism":"CHALLENGE","invoker":"human-1","authority":"AUTH-1","scope":"A1","expected_latency":"bounded","effects":"review","resume_conditions":"reviewed","evidence":["ev1"],"limits":"no execution","authority_valid":True,"scope_valid":True})
 assert rec["status"]=="PASS" and not rec["execution_permitted"]
 payload={"decision_id":"D1","problem_id":"P1","decision_type":"RESERVED_HUMAN","recommendations_considered":["R1"],"decision_authority":"AUTH-1","authorization":"bounded","applicable_DNA":["F9","F10","F11"],"applicable_constitution":["C1"],"applicable_governance":["G1"],"evidence":["ev1"],"uncertainty":"bounded","affected_entities":["obj"],"result":"APPROVE","challenge_status":"AVAILABLE","appeal_status":"AVAILABLE","decision_time":"2026-09-21T00:00:00Z","normative_status":"PASS","provenance":{"milestone":"P105"}}
 led=setup().build_decision_ledger_record(payload); assert led["status"]=="PASS" and led["p104"]["persisted"] is False
 outs=[]
 for i in range(50):
  z=setup().examine(manifest=act("d"+str(i)),authority_ids=("AUTH-1",),independent_domains=("d1",),now=NOW,rationale="bounded",explicit_confirmation=True,evidence=("ev1","ev2")); outs.append((z["status"],z["action"],z["reason"]))
 assert len(set(outs))==1
 print("P105_HUMAN_REPRESENTATIVE_CONSTITUTIONAL_INTERFACE_TEST_OK"); print("deterministic_replays=50"); print("functional_conclusion_only=True"); print("phenomenology_undetermined=True")
if __name__=="__main__": main()
