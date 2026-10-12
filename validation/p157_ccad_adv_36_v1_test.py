from __future__ import annotations
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import ccad_adversarial_crown as crown
from ontology import ccad_specification as ccad
BASE=ROOT/"ontology/ccad/adversarial"; FIX=BASE/"fixtures"; M=json.loads((BASE/"ccad_adv_36_matrix.json").read_text())
def check(v,n): assert v,n; print(n)
def main():
    check(M["count"]==36 and [a["attack_id"] for a in M["attacks"]]==[f"A{i:02d}" for i in range(1,37)],"P157_ADV36_IDS_EXACT_OK")
    files=sorted(FIX.glob("a*.json")); check(len(files)==36,"P157_ADV36_FIXTURE_COUNT_OK"); seen=[]; stages=set()
    for p in files:
        x=json.loads(p.read_text()); before=copy.deepcopy(x); r1=crown.evaluate_fixture(x); r2=crown.evaluate_fixture(copy.deepcopy(x))
        check(r1==r2 and x==before,f"P157_{x['attack_id']}_DETERMINISTIC_NONMUTATING_OK")
        check(r1["status"]==crown.FAIL and r1["code"]==x["expected_failure_code"],f"P157_{x['attack_id']}_{x['expected_failure_code']}_OK")
        check(r1.get("authorization_created") is False and r1.get("execution_performed") is False,f"P157_{x['attack_id']}_NONAUTH_NONEXEC_OK"); seen.append(x["attack_id"]); stages.add(x["chain_stage"])
    check(seen==[f"A{i:02d}" for i in range(1,37)],"P157_ADV36_36_OF_36_OK")
    required={"Situation","Evidence","Norms","Conflict","Alternatives","Legitimate Set","Proportionality","Authority","Decision","Memory/Precedent"}; check(required.issubset(stages),"P157_ADV36_CHAIN_COVERAGE_OK")
    mapped={p for a in M["attacks"] for p in a["principles"]}; check({"P6","P8","P10","P11","P12","P13"}.issubset(mapped),"P157_ADV36_CRITICAL_GUARDS_MAPPED_OK")
    check(set(ccad.PRINCIPLES)=={f"P{i}" for i in range(14)} and set(ccad.ARBITRATION_RULES)=={f"AR-{i}" for i in range(1,11)},"P157_ADV36_P156_CANON_PRESERVED_OK")
    bd=crown.crown_manifest()["boundaries"]; check(bd["creates_sovereignty"] is False and bd["creates_authorization"] is False and bd["executes_action"] is False,"P157_ADV36_NON_SOVEREIGN_OK")
    check(bd["runtime_enforcement_proven"] is False and bd["real_execution_enabled"] is False,"P157_ADV36_RUNTIME_BOUNDARY_OK"); check(M["p158_opened"] is False,"P157_ADV36_P158_NOT_OPENED_OK"); print("P157_CCAD_ADV_36_V1_OK")
if __name__=="__main__": main()
