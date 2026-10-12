import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_2_dm003_dm017_provenance_reconciliation_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G3_2_DM003_DM017_PROVENANCE_RECONCILIATION_COMPLETE"
def test_dm003(): assert D["DM003"]["status"]=="PROVENANCE_RECONCILED" and D["DM003"]["distinct_protective_families"]==2 and D["DM003"]["exact_replay_ready"] is True
def test_dm017(): assert D["DM017"]["status"]=="PROVENANCE_RECONCILED" and D["DM017"]["distinct_protective_families"]==2 and D["DM017"]["exact_replay_ready"] is True
def test_no_verdict(): assert D["DM003"]["causal_verdict_assigned"] is False and D["DM017"]["causal_verdict_assigned"] is False and D["causal_verdicts_assigned"] is False
def test_no_new_norm(): assert D["DM003"]["new_norm_created"] is False and D["DM017"]["new_norm_created"] is False and D["existing_norms_reused"] is True
def test_hash_checker():
 current=hashlib.sha256((ROOT/"ontology/occ_static_constitutional_checker.py").read_bytes()).hexdigest()
 historical=D["source_sha256"]["static_checker"]
 if current==historical: return
 successor=ROOT/"validation_artifacts/p159/occ1i/f4g3_10a_dm015_dm018_dm033_minimal_existing_surface_refinement_v1.json"
 assert successor.is_file()
 S=json.loads(successor.read_text())
 p=str(ROOT/"ontology/occ_static_constitutional_checker.py")
 assert S["before_sha256"][p]==historical
 assert S["after_sha256"][p]==current
 assert S["causal_verdicts_assigned"] is False
 assert S["new_primitive_created"] is False and S["new_norm_created"] is False and S["new_authority_created"] is False
def test_hash_verifier(): assert hashlib.sha256((ROOT/"ontology/occ_independent_constitutional_verifier.py").read_bytes()).hexdigest()==D["source_sha256"]["independent_verifier"]
def test_hash_human(): assert hashlib.sha256((ROOT/"ontology/human_reserved_authority_registry.py").read_bytes()).hexdigest()==D["source_sha256"]["human_reserved_authority_registry"]
def test_no_create_runtime(): assert D["runtime_mechanisms_modified"] is False and D["new_detector_created"] is False and D["create_authorized"] is False
def test_history(): assert D["historical_states_preserved"] is True
def test_next(): assert D["g3_3_ready"] is True and D["g3_closed"] is False and D["next_required_stage"]=="F4-G3.3_DM003_DM017_EXACT_CAUSAL_REPLAYS"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
