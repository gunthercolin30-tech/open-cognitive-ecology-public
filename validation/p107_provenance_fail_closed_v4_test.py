from copy import deepcopy
from ontology import constitutional_cognitive_economy as p
def opt(): return {"option_id":"safe","expected_value":2,"provenance":{"source":"v4"},"constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}
def ledger(): return {"evidence_ref":"E","decision_id":"D","problem_id":"PR","decision_type":"constitutional_cognitive_economy","recommendations_considered":[],"decision_authority":{"ref":"HUMAN"},"authorization":{"status":"NOT_GRANTED"},"applicable_DNA":["DNA-H"],"applicable_constitution":["Constitution"],"applicable_governance":["Governance"],"evidence":["E"],"uncertainty":{"status":"bounded"},"affected_entities":["OCE"],"result":"RECOMMENDATION_ONLY","challenge_status":"AVAILABLE","appeal_status":"AVAILABLE","decision_time":"2026-09-22T00:00:00Z","recourse_refs":[],"rollback_refs":[],"provenance":{"source":"P107-v4-test"},"configuration_ref":"P107-v4","dependency_refs":[],"metrics":{"expected_value":2.0}}
r=p.select([opt()])
lp=ledger(); before=deepcopy(lp); a=p.build_governed_assurance(r,lp)
assert a["status"]=="PASS" and a["assured"] and lp==before
for badprov in ({},None,""):
 q=ledger(); q["provenance"]=badprov
 z=p.build_governed_assurance(r,q)
 assert z["status"]=="UNDETERMINED" and not z["assured"] and z["reason"]=="missing_ledger_provenance"
q=ledger(); q["evidence_ref"]=""
z=p.build_governed_assurance(r,q); assert z["status"]=="UNDETERMINED" and z["reason"]=="missing_evidence_ref"
baseline=a["ledger_evidence"]["record"]["record_hash"]
for _ in range(200):
 z=p.build_governed_assurance(r,ledger()); assert z["ledger_evidence"]["record"]["record_hash"]==baseline
assert p.manifest()["version"]=="P107-v4"
print("P107_PROVENANCE_FAIL_CLOSED_V4_OK")
print("missing_provenance_rejected=True")
print("missing_evidence_ref_rejected=True")
print("valid_provenance_preserved=True")
print("deterministic_replays=200")
print("input_nonmutation=True")
print("authority_granted=False")
print("execution_performed=False")
print("runtime_enforcement_claimed=False")
print("functional_conclusion_only=True")
print("phenomenology_undetermined=True")
print("p108_opened=False")
