from pathlib import Path
from copy import deepcopy
import json,tempfile
from ontology import constitutional_cognitive_economy as p
def opt(i,v):
 return {"option_id":i,"expected_value":v,"provenance":{"source":"P107-v3-test"},"constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}
def ledger():
 return {"evidence_ref":"E-P107","decision_id":"D-P107","problem_id":"PR-P107","decision_type":"constitutional_cognitive_economy","recommendations_considered":[],"decision_authority":{"ref":"HUMAN-REVIEW"},"authorization":{"status":"NOT_GRANTED"},"applicable_DNA":["DNA-H","DNA-L0","DNA-L1"],"applicable_constitution":["CCAD","Constitution"],"applicable_governance":["Governance"],"evidence":["P107-V3"],"uncertainty":{"status":"bounded"},"affected_entities":["OCE"],"result":"RECOMMENDATION_ONLY","challenge_status":"AVAILABLE","appeal_status":"AVAILABLE","decision_time":"2026-09-21T00:00:00Z","recourse_refs":[],"rollback_refs":[],"provenance":{"source":"P107-integration-test"},"configuration_ref":"P107-v3","dependency_refs":[],"metrics":{"expected_value":2.0}}
def actor(i,perms=("read",)):
 return {"actor_id":i,"kind":"CAPABILITY","permissions":list(perms),"scopes":list(perms),"authority_status":"PASS","provenance_ref":"prov","evidence_ref":"ev"}
def recourse():
 return {"mechanism":"CHALLENGE","invoker":"human","authority":"reserved","scope":"P107","expected_latency":"bounded","effects":["review"],"resume_conditions":["reviewed"],"evidence":["E"],"limits":["no_execution"],"authority_valid":True,"scope_valid":True}
r=p.select([opt("safe",2),opt("lower",1)]); lp=ledger(); baseline=deepcopy(lp)
a=p.build_governed_assurance(r,lp,recourse_request=recourse(),composition_request={"actors":[actor("A")],"requested_permissions":["read"],"composed_objective_status":"PASS","normative_status":"PASS"})
assert a["status"]=="PASS" and a["assured"] and a["recommendation_stage"]["stage"]=="Recommendation"
assert a["ledger_evidence"]["status"]=="PASS" and a["recourse_evidence"]["status"]=="PASS" and a["composition_evidence"]["status"]=="PASS"
assert not a["authority_granted"] and not a["execution_performed"] and lp==baseline
bad=ledger(); bad.pop("decision_authority"); assert p.build_governed_assurance(r,bad)["status"]=="UNDETERMINED"
denied=p.build_governed_assurance(r,ledger(),composition_request={"actors":[actor("A",("read",))],"requested_permissions":["write"],"composed_objective_status":"PASS","normative_status":"PASS"})
assert denied["status"]=="FAIL" and not denied["assured"]
conf=p.build_governed_assurance(r,ledger(),conflict_request={"first":{"norm_id":"n1","level":"Constitution","content_ref":"c1","provenance":"p"},"second":{"norm_id":"n2","level":"Constitution","content_ref":"c2","provenance":"p"}})
assert conf["status"]=="CONFLICT" and not conf["assured"]
rr=recourse(); rr["authority_valid"]=False; assert p.build_governed_assurance(r,ledger(),recourse_request=rr)["status"]=="UNDETERMINED"
with tempfile.TemporaryDirectory() as td:
 persisted=p.persist_governed_trace(a,root=Path(td)); assert persisted["status"]=="PASS" and persisted["persisted"]
 path=Path(persisted["ledger_path"]); envelope=json.loads(path.read_text(encoding="utf-8").strip()); assert envelope["record"]["decision_id"]=="D-P107"
 assert json.loads(path.read_text(encoding="utf-8").splitlines()[0])["record"]["record_hash"]==envelope["record"]["record_hash"]
baseline_hash=a["ledger_evidence"]["record"]["record_hash"]
for _ in range(200):
 z=p.build_governed_assurance(r,ledger(),recourse_request=recourse(),composition_request={"actors":[actor("A")],"requested_permissions":["read"],"composed_objective_status":"PASS","normative_status":"PASS"})
 assert z["ledger_evidence"]["record"]["record_hash"]==baseline_hash
assert p.manifest()["version"]=="P107-v3"
print("P107_INTEGRATION_ASSURANCE_V3_OK")
print("p094_stage_integration=True")
print("p098_conflict_fail_closed=True")
print("p099_noncircumvention_integration=True")
print("p103_recourse_integration=True")
print("p104_decision_ledger_trace=True")
print("p104_persistence_restart_format=True")
print("deterministic_replays=200")
print("input_nonmutation=True")
print("authority_granted=False")
print("execution_performed=False")
print("runtime_enforcement_claimed=False")
print("functional_conclusion_only=True")
print("phenomenology_undetermined=True")
print("p108_opened=False")
