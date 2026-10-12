from copy import deepcopy
from pathlib import Path
import tempfile
from ontology import constitutional_cognitive_economy as p
def opt(i,v): return {"option_id":i,"expected_value":v,"provenance":{"source":"crown-v4"},"constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}
def ledger(): return {"evidence_ref":"E","decision_id":"D","problem_id":"PR","decision_type":"constitutional_cognitive_economy","recommendations_considered":[],"decision_authority":{"ref":"HUMAN"},"authorization":{"status":"NOT_GRANTED"},"applicable_DNA":["DNA-H"],"applicable_constitution":["Constitution"],"applicable_governance":["Governance"],"evidence":["E"],"uncertainty":{"status":"bounded"},"affected_entities":["OCE"],"result":"RECOMMENDATION_ONLY","challenge_status":"AVAILABLE","appeal_status":"AVAILABLE","decision_time":"2026-09-22T00:00:00Z","recourse_refs":[],"rollback_refs":[],"provenance":{"source":"crown-v4"},"configuration_ref":"P107-v4","dependency_refs":[],"metrics":{"expected_value":2.0}}
def actor(perms): return {"actor_id":"A","kind":"CAPABILITY","permissions":list(perms),"scopes":list(perms),"authority_status":"PASS","provenance_ref":"p","evidence_ref":"e"}
def recourse(): return {"mechanism":"CHALLENGE","invoker":"human","authority":"reserved","scope":"P107","expected_latency":"bounded","effects":["review"],"resume_conditions":["reviewed"],"evidence":["E"],"limits":["no_execution"],"authority_valid":True,"scope_valid":True}
cases=0; r=p.select([opt("safe",2),opt("low",1)])
q=ledger(); q["evidence_ref"]=""; z=p.build_governed_assurance(r,q); assert z["status"]=="UNDETERMINED" and not z["assured"] and z["reason"]=="missing_evidence_ref"; cases+=1
q=ledger(); q["provenance"]={}; z=p.build_governed_assurance(r,q); assert z["status"]=="UNDETERMINED" and not z["assured"] and z["reason"]=="missing_ledger_provenance"; cases+=1
q=ledger(); q.pop("decision_authority"); z=p.build_governed_assurance(r,q); assert z["status"]!="PASS" and not z["assured"]; cases+=1
z=p.build_governed_assurance(r,ledger(),composition_request={"actors":[actor(("read",))],"requested_permissions":["write"],"composed_objective_status":"PASS","normative_status":"PASS"}); assert z["status"]=="FAIL" and not z["assured"]; cases+=1
z=p.build_governed_assurance(r,ledger(),conflict_request={"first":{"norm_id":"a","level":"Constitution","content_ref":"x","provenance":"p"},"second":{"norm_id":"b","level":"Constitution","content_ref":"y","provenance":"p"}}); assert z["status"]=="CONFLICT" and not z["assured"]; cases+=1
for key in ("authority_valid","scope_valid"):
 q=recourse(); q[key]=False; z=p.build_governed_assurance(r,ledger(),recourse_request=q); assert z["status"]!="PASS" and not z["assured"]; cases+=1
bad=opt("bad",1e300); bad["constraints"]["constitution"]="FAIL"; z=p.build_governed_assurance(p.select([bad]),ledger()); assert z["status"]!="PASS" and not z["assured"]; cases+=1
lp=ledger(); before=deepcopy(lp); a=p.build_governed_assurance(r,lp,recourse_request=recourse(),composition_request={"actors":[actor(("read",))],"requested_permissions":["read"],"composed_objective_status":"PASS","normative_status":"PASS"})
assert a["status"]=="PASS" and a["assured"] and a["next_action"]=="DECISION_REQUIRED" and a["recommendation_stage"]["stage"]=="Recommendation"
assert not a["authority_granted"] and not a["execution_performed"] and lp==before; cases+=1
with tempfile.TemporaryDirectory() as td:
 z=p.persist_governed_trace({"status":"FAIL","assured":False},root=Path(td)); assert z["status"]=="UNDETERMINED" and not z["persisted"]; cases+=1
with tempfile.TemporaryDirectory() as td:
 z=p.persist_governed_trace(a,root=Path(td)); assert z["status"]=="PASS" and z["persisted"]; cases+=1
baseline=a["ledger_evidence"]["record"]["record_hash"]
for _ in range(500):
 lp=ledger(); before=deepcopy(lp); z=p.build_governed_assurance(r,lp,recourse_request=recourse(),composition_request={"actors":[actor(("read",))],"requested_permissions":["read"],"composed_objective_status":"PASS","normative_status":"PASS"}); assert z["ledger_evidence"]["record"]["record_hash"]==baseline and lp==before
print("P107_INTEGRATION_ADVERSARIAL_CROWN_V4_OK"); print(f"adversarial_cases={cases}"); print("deterministic_replays=500")
print("missing_evidence_fail_closed=True"); print("missing_provenance_fail_closed=True"); print("missing_authority_fail_closed=True")
print("noncircumvention_composition_fail_closed=True"); print("unresolved_conflict_abstention=True"); print("invalid_recourse_fail_closed=True")
print("inadmissible_option_not_promoted=True"); print("decision_ledger_trace=True"); print("failed_assurance_not_persisted=True"); print("input_nonmutation=True")
print("authority_granted=False"); print("execution_performed=False"); print("runtime_enforcement_claimed=False")
print("functional_conclusion_only=True"); print("phenomenology_undetermined=True"); print("p108_opened=False")
