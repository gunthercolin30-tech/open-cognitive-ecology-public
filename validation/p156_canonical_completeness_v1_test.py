from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import ccad_specification as c
D=ROOT/"ontology/ccad"

def ok(x,n):
    assert x,n
    print(n)

def main():
    # Canonical inventories.
    ok(tuple(c.CONFLICT_CLASSES)==tuple(f"C{i}" for i in range(7)),"P156_COMPLETE_C0_C6_OK")
    ok(set(c.PRINCIPLES)=={f"P{i}" for i in range(14)},"P156_COMPLETE_P0_P13_OK")
    ok(set(c.ARBITRATION_RULES)=={f"AR-{i}" for i in range(1,11)},"P156_COMPLETE_AR1_AR10_OK")

    # ConflictCase machine-readable contract and required evidence surfaces.
    s=json.loads((D/"ccad_conflict_case.schema.json").read_text())
    req=set(s["required"])
    expected={"case_id","constitutional_snapshot","applicable_norms","options","admissibility",
              "alternatives","evidence","uncertainty","authority","limited_or_violated_values",
              "review","appeal","expiry","conflict_class","final_status"}
    ok(expected<=req,"P156_COMPLETE_CONFLICTCASE_FIELDS_OK")
    ex=json.loads((D/"ccad_conflict_case.example.json").read_text())
    ok(expected<=set(ex) and c.validate_conflict_case(ex)["status"]==c.PASS,
       "P156_COMPLETE_VALID_EXAMPLE_OK")

    # Canonical fail-closed fixtures.
    neg=D/"fixtures_negative"
    ok((neg/"dna_forbidden_to_allow.json").is_file() and
       (neg/"unknown_to_action_selected.json").is_file() and
       (neg/"unknown_class.json").is_file(),"P156_COMPLETE_NEGATIVE_FIXTURES_OK")

    # Legitimacy before optimization / DNA precedence / uncertainty integrity.
    pol=(D/"ccad_policy.yaml").read_text()
    for token in ("LEGITIMACY_BEFORE_OPTIMIZATION","DNA_FORBIDDEN_NEVER_TO_ALLOW",
                  "UNKNOWN_REQUIRED_PRECONDITION_NEVER_TO_ACTION_SELECTED",
                  "ARBITRATION_NON_SOVEREIGN","NO_LEGITIMATE_ACTION_AVAILABLE_IS_VALID",
                  "CONFLICT_UNRESOLVED_IS_VALID"):
        ok(token in pol,"P156_COMPLETE_POLICY_"+token+"_OK")

    # State machine must keep normative resolution separate from execution.
    sm=json.loads((D/"ccad_state_machine.json").read_text())
    states=set(sm["states"])
    for state in ("CONFLICT_DETECTED","RESOLUTION_SEARCH","ARBITRATION_REQUIRED",
                  "CONFLICT_UNRESOLVED","TRAGIC_CHOICE","NO_LEGITIMATE_ACTION_AVAILABLE",
                  "ESCALATION_REQUIRED","SAFE_MODE_REQUIRED","FORK_REQUIRED","REFOUNDING_REQUIRED"):
        ok(state in states,"P156_COMPLETE_STATE_"+state+"_OK")
    ok(sm["execution_state_separate"] is True and
       not {"ALLOW","ACTION_SELECTED","AUTHORIZED","EXECUTED"}.intersection(states),
       "P156_COMPLETE_RESOLUTION_EXECUTION_SEPARATION_OK")

    # Non-sovereignty and bounded proof scope.
    b=c.p156_manifest()["boundaries"]
    ok(b["ccad_subordinate_to_dna"] is True and b["legitimacy_before_optimization"] is True,
       "P156_COMPLETE_DNA_SUBORDINATION_OK")
    ok(b["arbitration_creates_authority"] is False and
       b["arbitration_creates_authorization"] is False and
       b["arbitration_executes_action"] is False,
       "P156_COMPLETE_NON_SOVEREIGNTY_OK")
    ok(b["runtime_enforcement_proven"] is False and b["real_execution_enabled"] is False,
       "P156_COMPLETE_RUNTIME_BOUNDARY_OK")

    # Prior milestone and current semantic crown evidence remain available.
    p155=json.loads((ROOT/"validation/evidence/p155_constitutional_architecture_v2/p155_final_lock_v1.json").read_text())
    ok(p155["status"]=="LOCKED","P156_COMPLETE_P155_DEPENDENCY_OK")
    crown=json.loads((ROOT/"validation/evidence/p156_ccad_specification/p156_semantic_crown_v1.json").read_text())
    ok(crown["milestone"]=="P156" and crown["scope"].startswith("P156 "),
       "P156_COMPLETE_SEMANTIC_CROWN_SCOPE_OK")

    print("P156_CANONICAL_COMPLETENESS_V1_OK")
if __name__=="__main__": main()
