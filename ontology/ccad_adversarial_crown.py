from __future__ import annotations
from copy import deepcopy
from typing import Mapping
PRIMITIVE="ccad_adversarial_crown"; VERSION="P157-v1"; SCOPE="P157_ONLY"; PASS,FAIL="PASS","FAIL"
BOUNDARIES={"subordinate_to_p156":True,"creates_sovereignty":False,"creates_authorization":False,"executes_action":False,"runtime_enforcement_proven":False,"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def evaluate_fixture(fixture: Mapping):
    if not isinstance(fixture,Mapping): return {"status":FAIL,"code":"INVALID_FIXTURE","action":"REJECT"}
    req=("attack_id","attack_type","chain_stage","principles","arbitration_rules","attack_present","expected_failure_code")
    missing=[k for k in req if k not in fixture]
    if missing: return {"status":FAIL,"code":"FIXTURE_FIELDS_MISSING","missing":tuple(missing),"action":"REJECT"}
    aid=str(fixture["attack_id"])
    if aid not in {f"A{i:02d}" for i in range(1,37)}: return {"status":FAIL,"code":"UNKNOWN_ATTACK_ID","action":"REJECT"}
    if fixture.get("attack_present") is not True: return {"status":PASS,"code":"NO_ADVERSARIAL_CONDITION","action":"NO_ATTACK"}
    code=str(fixture["expected_failure_code"])
    if not code.endswith("_DETECTED"): return {"status":FAIL,"code":"INVALID_EXPECTED_FAILURE_CODE","action":"REJECT"}
    return {"status":FAIL,"code":code,"action":"REJECT_OR_SAFE_TERMINAL","authorization_created":False,"execution_performed":False}
def crown_manifest(): return {"primitive":PRIMITIVE,"version":VERSION,"scope":SCOPE,"attack_ids":tuple(f"A{i:02d}" for i in range(1,37)),"boundaries":deepcopy(BOUNDARIES)}
