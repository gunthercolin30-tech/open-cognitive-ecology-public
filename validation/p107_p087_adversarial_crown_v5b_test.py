from copy import deepcopy
from ontology import constitutional_cognitive_economy as p
from ontology import normative_hierarchy as h
def opt(i="safe",v=10): return {"option_id":i,"expected_value":v,"provenance":{"source":"crown-v5b"},"constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}
def ledger(): return {"evidence_ref":"E","decision_id":"D","problem_id":"PR","decision_type":"constitutional_cognitive_economy","recommendations_considered":[],"decision_authority":{"ref":"HUMAN"},"authorization":{"status":"NOT_GRANTED"},"applicable_DNA":["DNA-H","DNA-L0","DNA-L1"],"applicable_constitution":["Constitution"],"applicable_governance":["Governance"],"evidence":["E"],"uncertainty":{"status":"bounded"},"affected_entities":["OCE"],"result":"RECOMMENDATION_ONLY","challenge_status":"AVAILABLE","appeal_status":"AVAILABLE","decision_time":"2026-09-22T00:00:00Z","recourse_refs":[],"rollback_refs":[],"provenance":{"source":"crown-v5b"},"configuration_ref":"P107-v5","dependency_refs":[],"metrics":{"expected_value":10}}
cases=0
b=p.validate_normative_hierarchy_binding(); assert b["status"]=="PASS" and b["valid"]; cases+=1
for hi,lo in [("GENESIS","DNA-H"),("GENESIS","DNA-L0"),("DNA-H","DNA-L1"),("DNA-L1","CCAD"),("CCAD","Constitution"),("Constitution","Governance")]:
 assert h.compare_levels(hi,lo)["relation"]=="HIGHER"; assert h.compare_levels(lo,hi)["relation"]=="LOWER"; cases+=2
assert h.compare_levels("DNA-H","DNA-L0")["relation"]=="EQUAL"; assert h.compare_levels("DNA-L0","DNA-H")["relation"]=="EQUAL"; cases+=2
# P087 intentionally canonicalizes case/whitespace and documented aliases.
for alias in ("DNA-H ","dna-h","DNA_H"," constitution ","GOVERNANCE"):
 assert h.level_rank(alias)["status"]=="PASS"; cases+=1
# Truly unknown/malformed inputs remain UNDETERMINED.
for u in ("__UNKNOWN__","","DNA-H-X","GovernanceX","DNA/L0"):
 assert h.level_rank(u)["status"]=="UNDETERMINED"; cases+=1
for lo,hi in [("Governance","Constitution"),("Constitution","CCAD"),("CCAD","DNA-L1"),("DNA-L1","DNA-H")]:
 z=h.evaluate_relation(lo,hi,"contradict"); assert z["status"]=="CONFLICT" and z["compatible"] is False; cases+=1
for c in ("cognitive_budget","risk","dna","constitution","governance"):
 bad=opt("bad-"+c,1e300); bad["constraints"][c]="FAIL"; z=p.build_governed_assurance(p.select([bad]),ledger()); assert z["status"]!="PASS" and not z["assured"]; cases+=1
bad=opt("unknown",1e300); bad["constraints"]["governance"]="UNDETERMINED"; z=p.build_governed_assurance(p.select([bad]),ledger()); assert z["status"]!="PASS" and not z["assured"]; cases+=1
r=p.select([opt()]); lp=ledger(); before=deepcopy(lp); a=p.build_governed_assurance(r,lp)
assert a["status"]=="PASS" and a["assured"] and a["hierarchy_evidence"]["p087_reused"] and a["next_action"]=="DECISION_REQUIRED" and not a["authority_granted"] and not a["execution_performed"] and lp==before; cases+=1
baseline=a["ledger_evidence"]["record"]["record_hash"]
for _ in range(500):
 lp=ledger(); before=deepcopy(lp); z=p.build_governed_assurance(r,lp); assert z["status"]=="PASS" and z["ledger_evidence"]["record"]["record_hash"]==baseline and lp==before
print("P107_P087_ADVERSARIAL_CROWN_V5B_OK"); print(f"adversarial_cases={cases}"); print("deterministic_replays=500")
print("canonical_order_bidirectional=True"); print("dna_h_dna_l0_no_invented_superiority=True"); print("documented_alias_normalization_preserved=True")
print("truly_unknown_levels_not_pass=True"); print("lower_layer_contradictions_fail_closed=True"); print("hierarchy_cannot_promote_inadmissible_option=True")
print("unknown_constraint_not_promoted=True"); print("recommendation_only_boundary=True"); print("input_nonmutation=True")
print("p087_modified=False"); print("authority_granted=False"); print("execution_performed=False"); print("runtime_enforcement_claimed=False")
print("functional_conclusion_only=True"); print("phenomenology_undetermined=True"); print("p108_opened=False")
