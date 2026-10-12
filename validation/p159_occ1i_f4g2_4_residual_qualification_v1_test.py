import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g2_4_residual_qualification_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G2_4_RESIDUAL_QUALIFICATION_COMPLETE"
def test_scope(): assert D["expected_mutations"]==["DM011","DM014","DM028","DM047"] and D["total"]==4
def test_all_killed(): assert D["causally_killed"]==["DM011","DM014","DM028","DM047"] and D["causally_killed_count"]==4
def test_residual_zero(): assert D["residual"]==[] and D["residual_count"]==0
def test_identity(): assert D["identity"]=="4=4+0" and D["identity_valid"] is True
def test_no_promotion(): assert D["historical_states_preserved"] is True and D["unresolved_promoted"] is False and D["inconclusive_promoted"] is False
def test_no_runtime_or_create(): assert D["runtime_mechanisms_modified"] is False and D["new_detector_created"] is False and D["create_authorized"] is False
def test_not_closed(): assert D["g2_5_ready"] is True and D["g2_closed"] is False
def test_next(): assert D["next_required_stage"]=="F4-G2.5_REUSE_TO_EXTEND_RESOLUTION_COMMIT"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
