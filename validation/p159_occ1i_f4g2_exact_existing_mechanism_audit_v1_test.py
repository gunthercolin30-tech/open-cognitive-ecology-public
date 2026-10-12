import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4g2_exact_existing_mechanism_audit_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G2_EXACT_EXISTING_MECHANISM_AUDIT_COMPLETE"
def test_ids(): assert set(D["cases"])=={"DM011","DM014","DM028","DM047"}
def test_no_kills(): assert all(x["causal_status"]=="UNRESOLVED" for x in D["cases"].values())
def test_dm011(): assert D["cases"]["DM011"]["disposition"]=="REFINE_EXISTING_VERIFIER_AND_TEST_SURFACE"
def test_dm014(): assert D["cases"]["DM014"]["disposition"]=="REFINE_EXISTING_VERIFIER_AND_TEST_SURFACE"
def test_dm028(): assert D["cases"]["DM028"]["disposition"]=="REFINE_EXISTING_TEST_SURFACE"
def test_dm047(): assert D["cases"]["DM047"]["disposition"]=="REFINE_EXISTING_TEST_SURFACE"
def test_create(): assert D["create_authorized"] is False
def test_runtime(): assert D["runtime_mechanisms_modified"] is False
def test_history(): assert D["historical_evidence_preserved"] is True
def test_next(): assert D["next_required_stage"]=="F4-G2.2_EXACT_CONTROL_DISABLEMENT_REPLAYS"
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
