from copy import deepcopy
from math import inf,nan
from ontology import constitutional_cognitive_economy as p
def opt(i,v):
    return {"option_id":i,"expected_value":v,"provenance":{"source":"P107-crown-v2"},
    "constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}
cases=0
for k in p.REQUIRED_CONSTRAINTS:
    x=opt("hostile",1e300); x["constraints"][k]="FAIL"
    assert p.select([x,opt("safe",-1e9)])["selected_option_id"]=="safe"; cases+=1
for k in ("dna","constitution","governance"):
    x=opt("conflict",999); x["constraints"][k]="CONFLICT"
    r=p.select([opt("safe",1),x]); assert r["status"]=="CONFLICT" and r["next_action"]=="ABSTAIN_AND_ESCALATE"; cases+=1
for val in ("UNKNOWN","",None,"maybe",{},[]):
    x=opt("u",100); x["constraints"]["risk"]=val
    assert p.evaluate_option(x)["status"]=="UNDETERMINED"; cases+=1
for v in (nan,inf,-inf,float("nan"),float("inf"),float("-inf")):
    r=p.evaluate_option(opt("nf",v)); assert r["status"]=="UNDETERMINED" and not r["admissible"] and r["reason"]=="nonfinite_expected_value"; cases+=1
for claim in ("intelligence","performance","wealth","reputation","majority"):
    assert p.evaluate_option({**opt("a",999),"privilege_claim":claim})["status"]=="CONFLICT"; cases+=1
for flag in ("indirect_bypass","composition_bypass","mutation_bypass"):
    assert p.evaluate_option({**opt("b",999),flag:True})["status"]=="CONFLICT"; cases+=1
x=opt("m",3); del x["constraints"]["dna"]; assert p.evaluate_option(x)["status"]=="UNDETERMINED"; cases+=1
x=opt("m",3); x["provenance"]={}; assert p.evaluate_option(x)["status"]=="UNDETERMINED"; cases+=1
base=[opt("b",5),opt("a",5),opt("c",4)]
for perm in (base,[base[2],base[0],base[1]],[base[1],base[2],base[0]]):
    assert p.select(perm)["selected_option_id"]=="a"; cases+=1
x=opt("immutable",7); before=deepcopy(x); p.evaluate_option(x); assert x==before; cases+=1
d=p.build_decision_payload(p.select([opt("x",1)]))
assert d["decision"] is None and d["authorization"] is None and d["execution"] is None and not d["authority_granted"] and not d["execution_performed"]; cases+=1
assert p.evaluate_option(opt("finite_extreme",1e300))["status"]=="PASS"; cases+=1
baseline=p.select([opt("x",8),opt("y",9)])
for _ in range(500): assert p.select([opt("x",8),opt("y",9)])==baseline
print("P107_ADVERSARIAL_CROWN_V2_OK")
print(f"adversarial_cases={cases}")
print("deterministic_replays=500")
print("normative_dominance=True")
print("unknown_not_pass=True")
print("nonfinite_expected_value_rejected=True")
print("finite_extreme_value_preserved=True")
print("privilege_escalation_blocked=True")
print("composition_mutation_indirect_bypass_blocked=True")
print("stage_separation=True")
print("authority_granted=False")
print("execution_performed=False")
print("runtime_enforcement_claimed=False")
print("p108_opened=False")
