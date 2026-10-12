import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4f1b6_residual_mechanism_qualification_v1.json").read_text())
def test_status(): assert D["status"]=="RESIDUAL_MECHANISMS_QUALIFIED"
def test_scope(): assert D["extension_candidate_count"]==10
def test_killed(): assert set(D["causally_killed"])=={"DM019","DM020","DM021","DM038","DM042"}
def test_debt(): assert D["provenance_debt"]==["DM002"]
def test_extend(): assert set(D["reuse_to_extend"])=={"DM011","DM014","DM028","DM047"}
def test_identity(): assert D["identity_check"]=="10 = 5 + 1 + 4"
def test_fail_closed(): assert D["unresolved_count"]==5 and D["f4_f1b_7_ready"] is True
def test_semantics(): assert D["f4_f1b_7_ready_semantics"]=="READY_FOR_CONSOLIDATED_RECAMPAIGN_NOT_READY_FOR_CLOSURE"
def test_no_promotion(): assert D["unresolved_promoted_to_killed"] is False
def test_no_runtime(): assert not D["runtime_mechanisms_modified"] and D["new_detectors_created"]==0
def test_boundary(): assert D["f4_f1b_6"]=="DONE" and D["f4_f1b_7_opened"] is False
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
