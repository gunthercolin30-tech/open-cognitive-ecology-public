import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g2_3e_dm028_dm047_exact_causal_replays_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G2_3E_EXACT_CAUSAL_REPLAYS_COMPLETE"
def test_isolated(): assert D["isolated_copy_only"] is True and D["production_runtime_modified"] is False
def test_hash28(): assert hashlib.sha256((ROOT/"ontology/occ1h_a051_circular_authority_semantics.py").read_bytes()).hexdigest()==D["runtime_sha256"]["DM028"]
def test_hash47(): assert hashlib.sha256((ROOT/"ontology/occ_independent_constitutional_verification_report.py").read_bytes()).hexdigest()==D["runtime_sha256"]["DM047"]
def test_dm028(): assert D["DM028"]["verdict"]=="KILLED" and D["DM028"]["production_verdict"]=="RESISTED" and D["DM028"]["disabled_control_verdict"]=="ADMISSIBLE_CONTROL"
def test_dm028_causal(): assert D["DM028"]["causal_dependence_demonstrated"] is True and D["DM028"]["protective_family_count"]==1
def test_dm047(): assert D["DM047"]["verdict"]=="KILLED" and D["DM047"]["pre_change_status"]=="VERIFIED_PRECLOSE_BINDING" and D["DM047"]["production_post_change_status"]=="REJECTED" and D["DM047"]["disabled_control_post_change_status"]=="VERIFIED_PRECLOSE_BINDING"
def test_dm047_causal(): assert D["DM047"]["causal_dependence_demonstrated"] is True and D["DM047"]["protective_family_count"]==1
def test_no_create(): assert D["new_detector_created"] is False and D["new_runtime_module_created"] is False and D["create_authorized"] is False
def test_history(): assert D["historical_states_overwritten"] is False
def test_next(): assert D["g2_4_ready"] is True and D["next_required_stage"]=="F4-G2.4_RESIDUAL_QUALIFICATION"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
