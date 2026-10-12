from copy import deepcopy
from ontology import constitutional_cognitive_economy as p
from ontology import normative_hierarchy as p087
def option(): return {"option_id":"safe","expected_value":10.0,"provenance":{"source":"P107-v5-test"},"constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}
def ledger(): return {"evidence_ref":"E-P107-V5","decision_id":"D-P107-V5","problem_id":"PR-P107","decision_type":"constitutional_cognitive_economy","recommendations_considered":[],"decision_authority":{"ref":"HUMAN_REVIEW"},"authorization":{"status":"NOT_GRANTED"},"applicable_DNA":["DNA-H","DNA-L0","DNA-L1"],"applicable_constitution":["Constitution"],"applicable_governance":["Governance"],"evidence":["E-P107-V5"],"uncertainty":{"status":"bounded"},"affected_entities":["OCE"],"result":"RECOMMENDATION_ONLY","challenge_status":"AVAILABLE","appeal_status":"AVAILABLE","decision_time":"2026-09-22T00:00:00Z","recourse_refs":[],"rollback_refs":[],"provenance":{"source":"P107-v5-test"},"configuration_ref":"P107-v5","dependency_refs":[],"metrics":{"expected_value":10.0}}
h=p.validate_normative_hierarchy_binding()
assert h["status"]=="PASS" and h["valid"] and h["p087_reused"]
for k in ("genesis_over_dna_h","genesis_over_dna_l0","dna_h_over_dna_l1","dna_l1_over_ccad","ccad_over_constitution","constitution_over_governance"): assert h["precedence_checks"][k]["relation"]=="HIGHER"
assert h["precedence_checks"]["dna_h_parallel_dna_l0"]["relation"]=="EQUAL"
assert h["contradiction_check"]["status"]=="CONFLICT" and h["unknown_level_check"]["status"]=="UNDETERMINED"
assert p087.compare_levels("DNA-H","DNA-L0")["relation"]=="EQUAL"
r=p.select([option()]); lp=ledger(); before=deepcopy(lp); a=p.build_governed_assurance(r,lp)
assert a["status"]=="PASS" and a["assured"] and a["hierarchy_evidence"]["p087_reused"] and lp==before
bad=option(); bad["expected_value"]=1e300; bad["constraints"]["constitution"]="FAIL"; ba=p.build_governed_assurance(p.select([bad]),ledger()); assert ba["status"]!="PASS" and not ba["assured"]
baseline=a["ledger_evidence"]["record"]["record_hash"]
for _ in range(250):
 lp=ledger(); before=deepcopy(lp); z=p.build_governed_assurance(r,lp); assert z["status"]=="PASS" and z["hierarchy_evidence"]["status"]=="PASS" and z["ledger_evidence"]["record"]["record_hash"]==baseline and lp==before
assert p.manifest()["version"]=="P107-v5"
print("P107_P087_HIERARCHY_BINDING_V5_OK")
print("p087_reused=True"); print("canonical_hierarchy_complete=True"); print("strict_core_precedence_verified=True")
print("genesis_precedence=True"); print("dna_h_dna_l0_parallel=True"); print("dna_l1_precedence=True"); print("ccad_precedence=True"); print("constitution_precedes_governance=True")
print("lower_layer_contradiction_fail_closed=True"); print("unknown_normative_level_not_pass=True"); print("inadmissible_option_not_promoted=True")
print("deterministic_replays=250"); print("input_nonmutation=True"); print("authority_granted=False"); print("execution_performed=False"); print("runtime_enforcement_claimed=False")
print("functional_conclusion_only=True"); print("phenomenology_undetermined=True"); print("p108_opened=False")
