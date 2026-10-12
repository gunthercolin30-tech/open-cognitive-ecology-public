from pathlib import Path
from copy import deepcopy
import hashlib, json
from ontology import occ_package_validation_readiness_audit as q
from ontology import occ_canonical_principal_kernel_population as population
ROOT=Path(__file__).resolve().parents[1]

def main():
    a=q.audit(ROOT); b=q.audit(ROOT)
    assert a==b
    assert a["decision"] in (q.READY,q.BLOCKED)
    assert a["package_validation_performed"] is False and a["package_state_changed"] is False
    assert not a["authority_activated"] and not a["execution_performed"]
    assert not a["occ1a_closed"] and not a["occ1b_opened"] and not a["p160_opened"]
    print("P159_OCC1A_PACKAGE_READINESS_AUDIT_DETERMINISM_OK")
    print("P159_OCC1A_PACKAGE_READINESS_AUDIT_STAGE_BOUNDARY_OK")
    # Degradation crown at verifier level: each critical mutation must fail physical plan verification.
    plan=population.plan(ROOT)
    def rows_for(p):
        return {k:json.loads(v.decode("utf-8")) for k,v in p.items()}
    cases=[]
    d=rows_for(plan); k=next(iter(d)); d[k]["norms"]=d[k]["norms"][:-1]; cases.append(d)
    d=rows_for(plan); k=next(x for x in d if "dna_l0" in x); d[k]["norms"][0]["semantic_status"]="GOVERNED_ADOPTED_SEMANTIC_BINDING"; cases.append(d)
    d=rows_for(plan); k=next(x for x in d if "genesis" in x); d[k]["norms"][0]["text"]="INVENTED"; cases.append(d)
    d=rows_for(plan); k=next(iter(d)); d[k]["norms"][0]["runtime_authority_granted"]=True; cases.append(d)
    for d in cases:
        enc={k:population._json_bytes(v) for k,v in d.items()}
        assert population.verify_plan(enc) is False
    print("P159_OCC1A_PACKAGE_READINESS_DEGRADATION_CROWN_OK")
    print("decision="+a["decision"])
    print("check_count="+str(a["check_count"]))
    print("passed_count="+str(a["passed_count"]))
    print("blockers="+json.dumps(a["blockers"],ensure_ascii=False))
    print("package_validation_performed=false")
    print("package_state_changed=false")
    print("authority_activated=false")
    print("execution_performed=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")
if __name__=="__main__": main()
