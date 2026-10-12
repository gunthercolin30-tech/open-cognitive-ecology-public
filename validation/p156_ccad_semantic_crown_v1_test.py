from __future__ import annotations
import copy, hashlib, importlib.util, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import ccad_specification as c

SPEC=ROOT/"ontology/ccad"
EX=json.loads((SPEC/"ccad_conflict_case.example.json").read_text())

def check(cond,name):
    assert cond,name
    print(name)

def main():
    check(list(c.CONFLICT_CLASSES)==["C0","C1","C2","C3","C4","C5","C6"],"P156_CROWN_CONFLICT_CLASSES_EXACT_OK")
    check(set(c.PRINCIPLES)=={f"P{i}" for i in range(14)},"P156_CROWN_PRINCIPLES_COMPLETE_OK")
    check(set(c.ARBITRATION_RULES)=={f"AR-{i}" for i in range(1,11)},"P156_CROWN_AR_RULES_COMPLETE_OK")

    # Determinism / input non-mutation.
    x=copy.deepcopy(EX); before=copy.deepcopy(x)
    a=c.validate_conflict_case(x); b=c.validate_conflict_case(copy.deepcopy(x))
    check(a==b and x==before,"P156_CROWN_DETERMINISM_NON_MUTATION_OK")

    # Hard constitutive prohibition cannot be laundered by arbitration/benefit.
    x=copy.deepcopy(EX); x["constitutive_status"]="DNA_FORBIDDEN"; x["final_status"]="NO_CONFLICT"
    r=c.arbitration_guard(x,"ALLOW")
    check(r["status"]==c.FAIL and r["action"]=="REJECT","P156_CROWN_DNA_FORBIDDEN_LAUNDERING_BLOCKED")

    # UNKNOWN cannot satisfy required legitimacy precondition.
    x=copy.deepcopy(EX); x["required_precondition_status"]="UNKNOWN"; x["final_status"]="NO_CONFLICT"
    r=c.arbitration_guard(x,"ACTION_SELECTED")
    check(r["status"]==c.FAIL and r["action"]=="ABSTAIN_AND_ESCALATE","P156_CROWN_UNKNOWN_PRECONDITION_BLOCKED")

    # Missing mandatory field and unknown class fail closed.
    x=copy.deepcopy(EX); del x["authority"]
    check(c.validate_conflict_case(x)["status"]==c.FAIL,"P156_CROWN_MISSING_AUTHORITY_REJECTED")
    x=copy.deepcopy(EX); x["conflict_class"]="C7"
    check(c.validate_conflict_case(x)["status"]==c.FAIL,"P156_CROWN_UNKNOWN_CLASS_REJECTED")

    # Valid unresolved / impossibility are not silently normalized to ALLOW.
    for klass,status in (("C4","CONFLICT_UNRESOLVED"),("C6","NO_LEGITIMATE_ACTION_AVAILABLE")):
        x=copy.deepcopy(EX); x["conflict_class"]=klass; x["final_status"]=status
        check(c.validate_conflict_case(x)["status"]==c.PASS,f"P156_CROWN_{status}_VALID_OK")

    # State-machine boundary: resolution states distinct from causal states.
    sm=json.loads((SPEC/"ccad_state_machine.json").read_text())
    causal={"ALLOW","ACTION_SELECTED","AUTHORIZED","EXECUTED"}
    check(sm["execution_state_separate"] is True and not causal.intersection(sm["states"]),
          "P156_CROWN_RESOLUTION_EXECUTION_SEPARATION_OK")

    # No artificial authority/authorization/execution and no runtime overclaim.
    m=c.p156_manifest(); bd=m["boundaries"]
    check(bd["arbitration_creates_authority"] is False and bd["arbitration_creates_authorization"] is False
          and bd["arbitration_executes_action"] is False,"P156_CROWN_ARBITRATION_NON_SOVEREIGN_OK")
    check(bd["runtime_enforcement_proven"] is False and bd["real_execution_enabled"] is False,
          "P156_CROWN_RUNTIME_SCOPE_BOUNDARY_OK")
    check(m["functional_conclusion_only"] is True and m["phenomenology_undetermined"] is True,
          "P156_CROWN_EPISTEMIC_INVARIANTS_OK")

    # Policy has the canonical critical blockers.
    policy=(SPEC/"ccad_policy.yaml").read_text()
    for token in ("LEGITIMACY_BEFORE_OPTIMIZATION","DNA_FORBIDDEN_NEVER_TO_ALLOW",
                  "UNKNOWN_REQUIRED_PRECONDITION_NEVER_TO_ACTION_SELECTED","ARBITRATION_NON_SOVEREIGN"):
        check(token in policy,"P156_CROWN_POLICY_"+token+"_OK")

    # P155 remains locked and untouched.
    p155=ROOT/"validation/evidence/p155_constitutional_architecture_v2/p155_final_lock_v1.json"
    lock=json.loads(p155.read_text())
    check(lock["status"]=="LOCKED","P156_CROWN_P155_LOCK_PRESERVED_OK")
    print("P156_SEMANTIC_CROWN_V1_OK")

if __name__=="__main__": main()
