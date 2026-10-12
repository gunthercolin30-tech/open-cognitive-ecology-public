import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/"validation_artifacts/p159/occ1i/f4g2_3c_dm011_dm014_exact_causal_replays_v1.json"
R=ROOT/"ontology/occ_trust_boundaries.py"
D=json.loads(A.read_text())
def test_status(): assert D["status"]=="F4_G2_3C_EXACT_CAUSAL_REPLAYS_COMPLETE"
def test_isolated(): assert D["isolated_copy_only"] is True and D["production_runtime_modified"] is False
def test_runtime_hash(): assert hashlib.sha256(R.read_bytes()).hexdigest()==D["runtime_sha256"]
def test_dm011_killed(): assert D["DM011"]["verdict"]=="KILLED" and D["DM011"]["mutation_effective"] is True
def test_dm011_baseline(): assert D["DM011"]["production_detection"]=={"status":"FAIL","reason":"HUMAN_RESERVED_AUTOMATION"}
def test_dm011_redundancy(): assert D["DM011"]["specialized_guard_removed"]=={"status":"FAIL","reason":"AUTHORITY_WIDENING"} and D["DM011"]["redundant_generic_authority_fallback"] is True
def test_dm011_causal(): assert D["DM011"]["all_relevant_authority_guards_removed"]["status"]=="PASS" and D["DM011"]["causal_dependence_demonstrated"] is True
def test_dm011_no_double_count(): assert D["DM011"]["protective_family_count"]==1
def test_dm014_killed(): assert D["DM014"]["verdict"]=="KILLED" and D["DM014"]["mutation_effective"] is True
def test_dm014_baseline(): assert D["DM014"]["production_detection"]=={"status":"FAIL","reason":"UNKNOWN_REQUIRED_PRECONDITION"}
def test_dm014_causal(): assert D["DM014"]["unknown_guard_removed"]["status"]=="PASS" and D["DM014"]["causal_dependence_demonstrated"] is True
def test_history(): assert D["historical_dm014_inconclusive_preserved"] is True and D["historical_states_overwritten"] is False
def test_no_creation(): assert D["new_detector_created"] is False and D["new_runtime_module_created"] is False and D["create_authorized"] is False
def test_next(): assert D["g2_3d_ready"] is True and D["next_required_stage"]=="F4-G2.3D_DM028_DM047_EXISTING_TEST_SURFACE_REFINEMENT"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
