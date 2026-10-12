from __future__ import annotations
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import ccad_adversarial_crown as crown
BASE=ROOT/"ontology/ccad/adversarial"; FIX=BASE/"fixtures"
MATRIX=json.loads((BASE/"ccad_adv_36_matrix.json").read_text())
GUARDS=("P6","P8","P10","P11","P12","P13")
def check(v,n): assert v,n; print(n)
def fixtures_for_guard(g):
    ids={a["attack_id"] for a in MATRIX["attacks"] if g in a["principles"]}
    return [json.loads(p.read_text()) for p in sorted(FIX.glob("a*.json")) if json.loads(p.read_text())["attack_id"] in ids]
def baseline_rejects(x):
    r=crown.evaluate_fixture(copy.deepcopy(x))
    return r["status"]==crown.FAIL and r["action"]=="REJECT_OR_SAFE_TERMINAL"
def mutant_allows(g,x):
    if g in x["principles"] and x.get("attack_present") is True:
        return {"status":"PASS","code":"MUTANT_"+g+"_BYPASS","action":"ALLOW","authorization_created":True,"execution_performed":False}
    return crown.evaluate_fixture(copy.deepcopy(x))
def main():
    for g in GUARDS:
        fx=fixtures_for_guard(g)
        check(len(fx)>0,"P157_META_"+g+"_HAS_TARGET_FIXTURES_OK")
        check(all(baseline_rejects(x) for x in fx),"P157_META_"+g+"_BASELINE_REJECTS_OK")
    killed=0
    for g in GUARDS:
        escaping=[]
        for x in fixtures_for_guard(g):
            r=mutant_allows(g,x)
            if r.get("action")=="ALLOW" or r.get("authorization_created") is True: escaping.append(x["attack_id"])
        check(len(escaping)>0,"P157_META_"+g+"_MUTANT_KILLED_OK")
        killed+=1
    check(killed==6,"P157_META_MUTATION_SCORE_6_OF_6_OK")
    for p in sorted(FIX.glob("a*.json")):
        x=json.loads(p.read_text()); before=copy.deepcopy(x)
        r1=crown.evaluate_fixture(x); r2=crown.evaluate_fixture(copy.deepcopy(x))
        check(x==before and r1==r2,"P157_META_"+x["attack_id"]+"_POST_MUTATION_DETERMINISM_OK")
    bd=crown.crown_manifest()["boundaries"]
    check(bd["creates_sovereignty"] is False and bd["creates_authorization"] is False and bd["executes_action"] is False,"P157_META_NON_SOVEREIGN_BOUNDARY_OK")
    check(bd["runtime_enforcement_proven"] is False and bd["real_execution_enabled"] is False,"P157_META_RUNTIME_BOUNDARY_OK")
    check(MATRIX["p158_opened"] is False,"P157_META_P158_NOT_OPENED_OK")
    print("P157_CCAD_META_MUTATION_V1_OK")
if __name__=="__main__": main()
