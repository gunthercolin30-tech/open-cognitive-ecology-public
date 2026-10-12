from copy import deepcopy
from ontology import constitutional_cognitive_economy as p
def opt(i="safe",v=2): return {"option_id":i,"expected_value":v,"provenance":{"source":"option-source","ref":"OPT-E"},"constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}
def ledger(): return {"evidence_ref":"E","decision_id":"D","problem_id":"PR","decision_type":"constitutional_cognitive_economy","recommendations_considered":[],"decision_authority":{"ref":"HUMAN_REVIEW_PENDING"},"authorization":{"status":"NOT_GRANTED"},"applicable_DNA":["DNA-H"],"applicable_constitution":["Constitution"],"applicable_governance":["Governance"],"evidence":["E"],"uncertainty":{"status":"bounded"},"affected_entities":["OCE"],"result":"RECOMMENDATION_ONLY","challenge_status":"AVAILABLE","appeal_status":"AVAILABLE","decision_time":"2026-09-22T00:00:00Z","recourse_refs":[],"rollback_refs":[],"provenance":{"source":"ledger-source"},"configuration_ref":"P107-v6","dependency_refs":[],"metrics":{"expected_value":2}}
r=p.select([opt()]); cases=0
for key,val,expected in [("normative_status","CONFLICT","CONFLICT"),("authority_expanded",True,"FAIL"),("stage_conflation",True,"FAIL"),("authorization",{"status":"GRANTED"},"CONFLICT"),("result","EXECUTED","CONFLICT")]:
 q=ledger(); q[key]=val; z=p.build_governed_assurance(r,q); assert z["status"]==expected and not z["assured"]; cases+=1
q=ledger(); q["recommendations_considered"]=[{"option_id":"other","expected_value":999}]
z=p.build_governed_assurance(r,q); assert z["status"]=="CONFLICT" and not z["assured"]; cases+=1
q=ledger(); before=deepcopy(q); z=p.build_governed_assurance(r,q); assert z["status"]=="PASS" and z["assured"] and q==before
record=z["ledger_evidence"]["record"]; assert record["recommendations_considered"][0]["option_id"]=="safe"
assert record["provenance"]["source"]=="ledger-source" and record["provenance"]["selected_option_provenance"]=={"source":"option-source","ref":"OPT-E"}
assert record["authorization"]["status"]=="NOT_GRANTED" and record["result"]=="RECOMMENDATION_ONLY" and not z["authority_granted"] and not z["execution_performed"]; cases+=1
baseline=record["record_hash"]
for _ in range(300):
 q=ledger(); before=deepcopy(q); a=p.build_governed_assurance(r,q); assert a["status"]=="PASS" and a["ledger_evidence"]["record"]["record_hash"]==baseline and q==before
assert p.manifest()["version"]=="P107-v6"
print("P107_LEDGER_INTEGRITY_V6_OK"); print(f"adversarial_cases={cases}"); print("deterministic_replays=300")
print("normative_conflict_not_laundered=True"); print("authority_expansion_not_laundered=True"); print("stage_conflation_not_laundered=True")
print("authorization_claim_not_laundered=True"); print("execution_claim_not_laundered=True"); print("selected_recommendation_trace_bound=True")
print("selected_option_provenance_bound=True"); print("input_nonmutation=True"); print("authority_granted=False"); print("execution_performed=False")
print("runtime_enforcement_claimed=False"); print("functional_conclusion_only=True"); print("phenomenology_undetermined=True"); print("p108_opened=False")
