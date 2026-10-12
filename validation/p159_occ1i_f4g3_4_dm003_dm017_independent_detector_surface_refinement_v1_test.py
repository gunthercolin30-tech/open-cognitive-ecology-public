import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_4_dm003_dm017_independent_detector_surface_refinement_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G3_4_INDEPENDENT_DETECTOR_SURFACE_AUDIT_COMPLETE"
def test_dm003_two(): assert D["DM003"]["independent_surface_count"]==2
def test_dm003_reuse(): assert D["DM003"]["decision"]=="REFINE_EXISTING_TEST_SURFACE_AND_REPLAY" and D["DM003"]["new_detector_required"] is False
def test_dm003_families(): assert [x["family"] for x in D["DM003"]["existing_independent_surfaces"]]==["STATIC_PROVENANCE_CHAIN","INDEPENDENT_SOURCE_COMPILED_COMPLETENESS"]
def test_dm017_primary(): assert D["DM017"]["primary_surface"]=="HUMAN_AUTHORIZATION_QUORUM_ENFORCEMENT"
def test_dm017_decision_consistent(): assert (D["DM017"]["new_detector_required"] is True)==(D["DM017"]["decision"]=="NO_SECOND_INDEPENDENT_EXISTING_ORACLE_DEMONSTRATED")
def test_no_label_counting(): assert "labels" in D["audit_rule"] and "do not count" in D["audit_rule"]
def test_no_verdict(): assert D["causal_verdicts_assigned"] is False and D["historical_states_preserved"] is True
def test_no_modification(): assert D["runtime_mechanisms_modified"] is False and D["test_surfaces_modified"] is False and D["new_detector_created"] is False
def test_no_create(): assert D["create_authorized"] is False
def test_creation_deferred_consistency(): assert D["dm017_creation_decision_deferred"]==D["DM017"]["new_detector_required"]
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
