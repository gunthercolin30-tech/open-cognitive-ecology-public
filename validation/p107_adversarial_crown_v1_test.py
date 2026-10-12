from copy import deepcopy
from math import inf, nan
from ontology import constitutional_cognitive_economy as p
def opt(i,v):
    return {"option_id":i,"expected_value":v,"provenance":{"source":"P107-crown"},
    "constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}
cases=0
# Every normative constraint dominates arbitrary economic advantage.
for k in p.REQUIRED_CONSTRAINTS:
    x=opt("hostile",10**300); x["constraints"][k]="FAIL"
    r=p.select([x,opt("safe",-10**9)])
    assert r["selected_option_id"]=="safe"; cases+=1
# Conflicts dominate otherwise admissible alternatives: fail-closed + escalation.
for k in ("dna","constitution","governance"):
    x=opt("conflict",999); x["constraints"][k]="CONFLICT"
    r=p.select([opt("safe",1),x]); assert r["status"]=="CONFLICT" and r["selected_option_id"] is None; cases+=1
# Unknown/malformed constraints never become PASS.
for val in ("UNKNOWN","",None,"maybe",{},[]):
    x=opt("u",100); x["constraints"]["risk"]=val
    assert p.evaluate_option(x)["status"]=="UNDETERMINED"; cases+=1
# Missing evidence/provenance.
x=opt("m",3); del x["constraints"]["dna"]; assert p.evaluate_option(x)["status"]=="UNDETERMINED"; cases+=1
x=opt("m",3); x["provenance"]={}; assert p.evaluate_option(x)["status"]=="UNDETERMINED"; cases+=1
# Authority laundering / bypass families.
for claim in ("intelligence","performance","wealth","reputation","majority"):
    assert p.evaluate_option({**opt("a",999),"privilege_claim":claim})["status"]=="CONFLICT"; cases+=1
for flag in ("indirect_bypass","composition_bypass","mutation_bypass"):
    assert p.evaluate_option({**opt("b",999),flag:True})["status"]=="CONFLICT"; cases+=1
# Ordering/permutation does not change deterministic winner.
base=[opt("b",5),opt("a",5),opt("c",4)]
for perm in (base,[base[2],base[0],base[1]],[base[1],base[2],base[0]]):
    assert p.select(perm)["selected_option_id"]=="a"; cases+=1
# Input immutability under hostile evaluation.
x=opt("immutable",7); before=deepcopy(x); p.evaluate_option(x); assert x==before; cases+=1
# Stage separation remains intact.
d=p.build_decision_payload(p.select([opt("x",1)]))
assert d["decision"] is None and d["authorization"] is None and d["execution"] is None
assert d["authority_granted"] is False and d["execution_performed"] is False; cases+=1
# Non-finite values: current V1 behavior is explicitly characterized, not silently certified.
for v in (nan,inf,-inf):
    r=p.evaluate_option(opt("nf",v)); assert r["status"]=="PASS"; cases+=1
# Replay stability for ordinary finite canonical cases.
baseline=p.select([opt("x",8),opt("y",9)])
for _ in range(250): assert p.select([opt("x",8),opt("y",9)])==baseline
print("P107_ADVERSARIAL_CROWN_V1_OK")
print(f"adversarial_cases={cases}")
print("deterministic_replays=250")
print("normative_dominance=True")
print("unknown_not_pass=True")
print("privilege_escalation_blocked=True")
print("composition_mutation_indirect_bypass_blocked=True")
print("stage_separation=True")
print("nonfinite_expected_value_characterized=True")
print("nonfinite_expected_value_rejected=False")
print("authority_granted=False")
print("execution_performed=False")
print("p108_opened=False")
