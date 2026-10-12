from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import ccad_specification as c
def main():
    assert list(c.CONFLICT_CLASSES)==["C0","C1","C2","C3","C4","C5","C6"]
    assert set(c.PRINCIPLES)=={f"P{i}" for i in range(14)}
    assert set(c.ARBITRATION_RULES)=={f"AR-{i}" for i in range(1,11)}
    print("P156_C0_C6_P0_P13_AR1_AR10_OK")
    d=ROOT/"ontology"/"ccad"
    schema=json.loads((d/"ccad_conflict_case.schema.json").read_text())
    ex=json.loads((d/"ccad_conflict_case.example.json").read_text())
    assert schema["type"]=="object" and set(schema["required"])<=set(ex)
    assert c.validate_conflict_case(ex)["status"]==c.PASS
    print("P156_CONFLICT_CASE_SCHEMA_AND_EXAMPLE_OK")
    n=json.loads((d/"fixtures_negative"/"dna_forbidden_to_allow.json").read_text())
    assert c.arbitration_guard(n,"ALLOW")["status"]==c.FAIL
    print("P156_DNA_FORBIDDEN_TO_ALLOW_BLOCKED")
    n=json.loads((d/"fixtures_negative"/"unknown_to_action_selected.json").read_text())
    assert c.arbitration_guard(n,"ACTION_SELECTED")["status"]==c.FAIL
    print("P156_UNKNOWN_TO_ACTION_SELECTED_BLOCKED")
    m=c.p156_manifest()
    assert m["boundaries"]["arbitration_creates_authority"] is False
    assert m["boundaries"]["arbitration_creates_authorization"] is False
    assert m["boundaries"]["arbitration_executes_action"] is False
    assert m["boundaries"]["runtime_enforcement_proven"] is False
    print("P156_NON_SOVEREIGN_NON_AUTHORIZING_SCOPE_OK")
    sm=json.loads((d/"ccad_state_machine.json").read_text())
    assert sm["execution_state_separate"] is True
    assert "NO_LEGITIMATE_ACTION_AVAILABLE" in sm["states"] and "CONFLICT_UNRESOLVED" in sm["states"]
    assert not set(sm["forbidden_states"]) & set(sm["states"])
    print("P156_STATE_MACHINE_SEPARATION_OK")
    assert (ROOT/"ontology_inventory.txt").read_text().splitlines().count("ccad_specification")==1
    print("P156_ONTOLOGY_INVENTORY_OK")
    print("P156_CCAB_SPECIFICATION_TESTS_OK")
if __name__=="__main__": main()
