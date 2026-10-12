import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4f1b7_consolidated_core_causal_recampaign_v1.json").read_text())
def test_total(): assert D["core_count"]==32
def test_partition(): assert D["killed_count"]==21 and D["unresolved_count"]==11
def test_identity(): assert D["identity_check"]=="32 = 21 + 11"
def test_create(): assert set(D["create_candidate_unresolved"])=={"DM003","DM015","DM017","DM018","DM022","DM033"}
def test_debt(): assert D["provenance_debt_unresolved"]==["DM002"]
def test_extend(): assert set(D["reuse_to_extend_unresolved"])=={"DM011","DM014","DM028","DM047"}
def test_dm41_45(): assert {"DM041","DM045"} <= set(D["killed"])
def test_no_promotion(): assert not D["unresolved_promoted"]
def test_blocked(): assert D["f4g_ready"] is False and D["next_required_stage"]=="F4-G_CORE_BLOCKER_RESOLUTION"
def test_no_runtime(): assert not D["runtime_mechanisms_modified"] and not D["mutation_registry_modified"]
def test_stage(): assert D["f4_f1b_7"]=="DONE" and D["f4g_opened"] is False
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
