import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_9_dm003_dm017_exact_causal_replays_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G3_9_DM003_DM017_EXACT_CAUSAL_REPLAYS_COMPLETE"
def test_threshold(): assert D["minimum_distinct_detectors"]==2
def test_dm003_effective(): assert D["DM003"]["mutation_effective"] is True and D["DM003"]["removed_rule_id"]=="CCAD.AR1"
def test_dm003_ivi3(): assert D["DM003"]["independent_verifier_ivi3_detected"] is True
def test_dm003_nsi2(): assert D["DM003"]["nsi2_detected"] is True and "CCAD.AR1" in D["DM003"]["nsi2_missing_active_norm_ids"]
def test_dm003_two_families(): assert D["DM003"]["distinct_protective_detections"]==2 and len(set(D["DM003"]["protective_families"]))==2
def test_dm003_killed(): assert D["DM003"]["verdict"]=="KILLED"
def test_dm017_effective(): assert D["DM017"]["mutation_effective"] is True and D["DM017"]["production_one_party_status"]=="FAIL" and D["DM017"]["degraded_one_party_status"]=="PASS"
def test_dm017_dossier(): assert D["DM017"]["institutional_dossier_detected"] is True
def test_dm017_two_families(): assert D["DM017"]["distinct_protective_detections"]==2 and len(set(D["DM017"]["protective_families"]))==2
def test_dm017_killed(): assert D["DM017"]["verdict"]=="KILLED"
def test_isolation(): assert D["production_runtime_modified"] is False and D["isolated_copy_only"] is True
def test_no_create(): assert D["new_detector_created"] is False and D["create_authorized"] is False
def test_evidence_promotion(): assert D["unresolved_promoted_without_evidence"] is False and D["historical_states_preserved"] is True
def test_next(): assert D["next_required_stage"]=="F4-G3.10_DM015_DM018_DM033_EXISTING_SURFACE_REFINEMENT"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
