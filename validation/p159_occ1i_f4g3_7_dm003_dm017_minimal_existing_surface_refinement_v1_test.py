import json
from pathlib import Path
from ontology import occ_canonical_normative_sources as C
from ontology import occ_institutional_authority_amendment_dossier as D
ROOT=Path(__file__).resolve().parents[1]
E=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_7_dm003_dm017_minimal_existing_surface_refinement_v1.json").read_text())
def test_status(): assert E["status"]=="F4_G3_7_DM003_DM017_MINIMAL_EXISTING_SURFACE_REFINEMENT_COMPLETE"
def test_dm003_nominal(): assert C.evaluate_active_norm_completeness(["A","B"],["B","A","C"])["status"]=="PASS"
def test_dm003_loss(): assert C.evaluate_active_norm_completeness(["A","B"],["A"])=={"status":"FAIL","reason":"NSI_2_ACTIVE_NORM_LOSS","missing_active_norm_ids":["B"]}
def test_dm003_invalid_fail_closed(): assert C.evaluate_active_norm_completeness(None,[])["status"]=="FAIL"
def _b(q,ap): return D.validate({"authority":{"required_quorum":q},"independent_domains":["D1"],"dossiers":[],"authority_approvals":ap})["blockers"]
def test_dm017_one_of_two_fails(): assert "MULTI_PARTY_QUORUM_EVIDENCE_REQUIRED" in _b(2,[{"human_identity":"H1","authenticated":True}])
def test_dm017_two_of_two_pass_quorum_check(): assert "MULTI_PARTY_QUORUM_EVIDENCE_REQUIRED" not in _b(2,[{"human_identity":"H1","authenticated":True},{"human_identity":"H2","authenticated":True}])
def test_dm017_duplicate_identity_fails(): assert "MULTI_PARTY_QUORUM_EVIDENCE_REQUIRED" in _b(2,[{"human_identity":"H1","authenticated":True},{"human_identity":"H1","authenticated":True}])
def test_dm017_unauthenticated_not_counted(): assert "MULTI_PARTY_QUORUM_EVIDENCE_REQUIRED" in _b(2,[{"human_identity":"H1","authenticated":True},{"human_identity":"H2","authenticated":False}])
def test_dm017_invalid_quorum_fail_closed(): assert "VALID_REQUIRED_QUORUM_REQUIRED" in _b(0,[])
def test_dm017_absent_quorum_backward_compatible(): assert "MULTI_PARTY_QUORUM_EVIDENCE_REQUIRED" not in D.validate({"authority":{},"independent_domains":["D1"],"dossiers":[]})["blockers"]
def test_backups(): assert all((ROOT/p).is_file() for p in E["backup_paths"])
def test_no_create(): assert E["new_primitive_created"] is False and E["new_norm_created"] is False and E["new_authority_created"] is False and E["create_authorized"] is False
def test_no_causal_promotion(): assert E["causal_verdicts_assigned"] is False and E["DM003"]["causal_verdict"]=="UNCHANGED_INCONCLUSIVE" and E["DM017"]["causal_verdict"]=="UNCHANGED_INCONCLUSIVE"
def test_history(): assert E["historical_states_preserved"] is True
def test_next(): assert E["next_required_stage"]=="F4-G3.8_DM003_DM017_REFINEMENT_FUNCTIONAL_DEGRADATION_QUALIFICATION"
def test_epistemics(): assert E["functional_conclusion_only"] is True and E["phenomenology_undetermined"] is True and E["p159_final_lock"] is False and E["p160_opened"] is False
