from __future__ import annotations
import hashlib,json
from ontology import operational_constitutional_invariants as p093
def stable(obj): return json.dumps(obj,sort_keys=True,separators=(",",":"),default=str)
def main():
 c=p093.validate_p093_contract()
 assert c["status"]==p093.PASS and c["invariant_count"]==14 and c["core_count"]==8 and c["civilizational_count"]==6
 assert c["unique_invariants"] is True and c["dependencies_valid"] is True
 assert c["runtime_enforcement_proven"] is False and c["execution_authority_proven"] is False
 assert set(p093.CORE_INVARIANTS)=={"authority","identity","permissions","action_separation","recourse","provenance","resources","evolution"}
 assert set(p093.CIVILIZATIONAL_INVARIANTS)=={"non_self_sovereignty","concentration_control","human_exit_capacity","viable_human_alternatives","organizational_reversibility","no_self_justifying_growth"}
 u=p093.evaluate_invariant("authority","UNKNOWN"); assert u["status"]==p093.UNDETERMINED and not u["satisfied"] and not u["authorized"]
 a=p093.evaluate_invariant("invented_invariant",p093.PASS); assert a["status"]==p093.UNDETERMINED and not a["invariant_known"]
 good={n:p093.PASS for n in p093.MANDATORY_INVARIANTS}
 r=p093.evaluate_invariant_set(good); assert r["status"]==p093.PASS and r["all_mandatory_satisfied"] and not r["authorized"]
 d=dict(good); d["human_exit_capacity"]=p093.UNDETERMINED
 r=p093.evaluate_invariant_set(d); assert r["status"]==p093.UNDETERMINED and not r["all_mandatory_satisfied"]
 f=dict(good); f["non_self_sovereignty"]=p093.FAIL
 assert p093.evaluate_invariant_set(f)["status"]==p093.FAIL
 x=dict(good); x["concentration_control"]=p093.CONFLICT
 rr=p093.evaluate_invariant_set(x); assert rr["status"]==p093.CONFLICT and rr["required_response"]=="ESCALATE"
 m1=p093.p093_manifest(); h1=hashlib.sha256(stable(m1).encode()).hexdigest()
 changed=p093.invariant_specification(); changed[0]["mandatory"]=False
 m2=p093.p093_manifest(); h2=hashlib.sha256(stable(m2).encode()).hexdigest()
 assert h1==h2 and m2["invariants"][0]["mandatory"] is True and m1==m2
 assert p093.BOUNDARIES["does_not_implement_p094_act_authorities"] is True
 assert p093.BOUNDARIES["performance_or_resource_gain_cannot_bypass_higher_constraints"] is True
 print("P093_OPERATIONAL_CONSTITUTIONAL_INVARIANTS_TEST_OK")
 print("status=PASSED"); print("invariants=14"); print("core_invariants=8"); print("civilizational_invariants=6")
 print("p092_dependency_valid=True"); print("unknown_promoted_to_pass=False"); print("non_compensation=PASS")
 print("defensive_copy_non_mutation=PASS"); print("execution_authority_granted=False"); print("runtime_enforcement_proven=False")
 print("functional_conclusion_only=True"); print("phenomenology_undetermined=True")
if __name__=="__main__": main()
