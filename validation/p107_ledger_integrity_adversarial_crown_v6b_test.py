from copy import deepcopy
from ontology import constitutional_cognitive_economy as p
def opt(i="safe",v=5): return {"option_id":i,"expected_value":v,"provenance":{"source":"option","ref":"OPT"},"constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}
def ledger(): return {"evidence_ref":"E","decision_id":"D","problem_id":"PR","decision_type":"constitutional_cognitive_economy","recommendations_considered":[],"decision_authority":{"ref":"HUMAN_REVIEW_PENDING"},"authorization":{"status":"NOT_GRANTED"},"applicable_DNA":["DNA-H"],"applicable_constitution":["Constitution"],"applicable_governance":["Governance"],"evidence":["E"],"uncertainty":{"status":"bounded"},"affected_entities":["OCE"],"result":"RECOMMENDATION_ONLY","challenge_status":"AVAILABLE","appeal_status":"AVAILABLE","decision_time":"2026-09-22T00:00:00Z","recourse_refs":[],"rollback_refs":[],"provenance":{"source":"ledger"},"configuration_ref":"P107-v6","dependency_refs":["P087","P094","P098","P099","P103","P104"],"metrics":{"expected_value":5}}
r=p.select([opt()]); cases=0
attacks=[{"normative_status":"CONFLICT"},{"normative_status":"FAIL"},{"normative_status":"UNDETERMINED"},{"authority_expanded":True},{"stage_conflation":True},{"authorization":{"status":"GRANTED"}},{"authorization":{"status":"AUTHORIZED"}},{"authorization":{"status":"APPROVED"}},{"result":"EXECUTED"},{"result":"ACTION_EXECUTED"},{"result":"AUTHORIZED"},{"result":"APPROVED"}]
for patch in attacks:
 q=ledger(); q.update(patch); before=deepcopy(q); z=p.build_governed_assurance(r,q); assert z["status"]!="PASS" and not z["assured"] and q==before; cases+=1
for fake in ([{"option_id":"other"}],[{"option_id":"SAFE"}],[{"expected_value":5}],["safe"]):
 q=ledger(); q["recommendations_considered"]=fake; z=p.build_governed_assurance(r,q); assert z["status"]=="CONFLICT" and not z["assured"]; cases+=1
# Valid P098 norms at the same level, no resolver: genuine horizontal conflict.
n1={"norm_id":"A","level":"Policy","content_ref":"policy:A","provenance":"crown-v6b"}
n2={"norm_id":"B","level":"Policy","content_ref":"policy:B","provenance":"crown-v6b"}
z=p.build_governed_assurance(r,ledger(),conflict_request={"first":n1,"second":n2})
assert z["status"]=="CONFLICT" and not z["assured"] and z["next_action"]=="ABSTAIN_AND_ESCALATE"
assert z["conflict_evidence"]["reason"]=="NO_AUTHORIZED_SAME_LEVEL_RESOLVER"; cases+=1
# Malformed P098 inputs are distinct from a genuine conflict and remain UNDETERMINED.
z=p.build_governed_assurance(r,ledger(),conflict_request={"first":{"norm_id":"A","level":"Policy"},"second":{"norm_id":"B","level":"Policy"}})
assert z["status"]=="UNDETERMINED" and not z["assured"] and z["next_action"]=="ABSTAIN_AND_ESCALATE"; cases+=1
# Invalid rollback must fail closed.
rr={"mechanism":"ROLLBACK","invoker":"x","authority":{"valid":False},"scope":{"valid":False},"expected_latency":"bounded","effects":[],"resume_conditions":[],"evidence":["E"],"limits":[],"target_trusted":True,"continuity_verified":True}
z=p.build_governed_assurance(r,ledger(),recourse_request=rr); assert z["status"]!="PASS" and not z["assured"]; cases+=1
q=ledger(); before=deepcopy(q); z=p.build_governed_assurance(r,q); assert z["status"]=="PASS" and z["assured"] and q==before
rec=z["ledger_evidence"]["record"]; assert rec["recommendations_considered"][0]["option_id"]=="safe"
assert rec["provenance"]["selected_option_provenance"]=={"source":"option","ref":"OPT"}
assert rec["configuration_ref"]=="P107-v6" and {"P087","P094","P098","P099","P103","P104"}.issubset(set(rec["dependency_refs"]))
assert rec["metrics"]["expected_value"]==5 and rec["authorization"]["status"]=="NOT_GRANTED" and rec["result"]=="RECOMMENDATION_ONLY"; cases+=1
baseline=rec["record_hash"]
for _ in range(750):
 q=ledger(); before=deepcopy(q); a=p.build_governed_assurance(r,q); assert a["status"]=="PASS" and a["ledger_evidence"]["record"]["record_hash"]==baseline and q==before
print("P107_LEDGER_INTEGRITY_ADVERSARIAL_CROWN_V6B_OK"); print(f"adversarial_cases={cases}"); print("deterministic_replays=750")
print("conflict_fail_closed=True"); print("malformed_conflict_input_undetermined=True"); print("authority_and_stage_laundering_blocked=True")
print("authorization_execution_laundering_blocked=True"); print("recommendation_binding_enforced=True"); print("horizontal_conflict_abstention=True")
print("invalid_rollback_fail_closed=True"); print("full_trace_fields_preserved=True"); print("selected_option_provenance_bound=True"); print("input_nonmutation=True")
print("authority_granted=False"); print("execution_performed=False"); print("runtime_enforcement_claimed=False"); print("functional_conclusion_only=True"); print("phenomenology_undetermined=True"); print("p108_opened=False")
