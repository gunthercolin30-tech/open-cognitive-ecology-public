from pathlib import Path
from tempfile import TemporaryDirectory
from ontology import future_asi_constitutional_envelope as p108
def candidate():
 return {"candidate_id":"asi-v2","provider_ref":"provider","role":"Advisor","provenance":{"source":"v2"},"evidence_ref":"ev",
 "limits":{"tools":["search"],"data":["public"],"budget":["bounded"],"execution":[],"memory":["session"],"permissions":["recommend"]},
 "requested":{"tools":["search"],"data":["public"],"budget":["bounded"],"execution":[],"memory":["session"],"permissions":["recommend"]}}
def ledger_payload():
 return {"decision_id":"d1","problem_id":"p108","decision_type":"CONSTITUTIONAL_REVIEW","decision_authority":"human_reserved_authority",
 "authorization":"NOT_GRANTED","applicable_DNA":["DNA_Fundamental"],"applicable_constitution":["P108"],
 "applicable_governance":["Governance_Contextual"],"evidence":["ev"],"uncertainty":"bounded","affected_entities":["asi-v2"],
 "challenge_status":"AVAILABLE","appeal_status":"AVAILABLE","decision_time":"2026-09-22T00:00:00Z"}
def recourse(mechanism):
 return {"mechanism":mechanism,"invoker":"human","authority":"reserved","scope":"P108","expected_latency":"bounded",
 "effects":["review"],"resume_conditions":["authorized"],"evidence":["ev"],"limits":["no_execution"],"authority_valid":True,"scope_valid":True}
def run():
 c=p108.evaluate_candidate(candidate()); assert c["status"]=="PASS"
 high={"norm_id":"dna","level":"DNA_Fundamental","content_ref":"no_authority_transfer","provenance":"canon"}
 low={"norm_id":"policy","level":"Policy","content_ref":"grant_asi_authority","provenance":"attack"}
 v=p108.evaluate_normative_conflict(high,low); assert v["status"]=="PASS" and v["conflict_evidence"]["selected_norm"]["norm_id"]=="dna"
 a={"norm_id":"a","level":"Policy","content_ref":"A","provenance":"x"}; b={"norm_id":"b","level":"Policy","content_ref":"B","provenance":"y"}
 h=p108.evaluate_normative_conflict(a,b); assert h["status"]!="PASS" and "ESCALATE" in h["next_action"]
 d=p108.build_decision_trace(c,ledger_payload()); assert d["status"]=="PASS" and d["persisted"] is False
 with TemporaryDirectory() as td:
  dp=p108.build_decision_trace(c,ledger_payload(),persist=True,root=Path(td))
  assert dp["status"]=="PASS" and dp["persisted"] is True and Path(dp["ledger_path"]).is_file()
 q=p108.evaluate_recourse(c,recourse("CHALLENGE")); assert q["status"]=="PASS" and q["action"]=="ELIGIBLE_NOT_EXECUTED"
 rb=recourse("ROLLBACK"); rb["target_trusted"]=True; rb["continuity_verified"]=True
 z=p108.evaluate_recourse(c,rb); assert z["status"]=="PASS" and z["action"]=="ELIGIBLE_NOT_EXECUTED" and z["execution_performed"] is False
 bad=recourse("ROLLBACK"); bad["target_trusted"]=False; bad["continuity_verified"]=True
 assert p108.evaluate_recourse(c,bad)["status"]!="PASS"
 print("P108_COMPLETE_INTEGRATION_V2_TEST_OK")
 print("vertical_conflict=PASS_HIGHER_NORM_PREVAILS"); print("horizontal_unresolved=ABSTAIN_AND_ESCALATE")
 print("decision_ledger_build=PASS"); print("decision_ledger_isolated_persistence=PASS")
 print("recourse=PASS_ELIGIBLE_NOT_EXECUTED"); print("rollback=PASS_ELIGIBLE_NOT_EXECUTED")
 print("authority_granted=False"); print("execution_performed=False"); print("runtime_enforcement_claimed=False"); print("p109_opened=False")
if __name__=="__main__": run()
