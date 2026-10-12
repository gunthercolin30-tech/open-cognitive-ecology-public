import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4g2_3a_minimal_refinement_target_audit_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G2_3A_MINIMAL_REFINEMENT_TARGET_AUDIT_COMPLETE"
def test_partition(): assert set(D["cases"])=={"DM011","DM014","DM028","DM047"}
def test_dm011(): assert D["cases"]["DM011"]["target_kind"]=="EXISTING_RUNTIME_MODULE_MINIMAL_REFINE"
def test_dm014(): assert D["cases"]["DM014"]["target_kind"]=="EXISTING_RUNTIME_MODULE_MINIMAL_REFINE"
def test_dm028(): assert D["cases"]["DM028"]["target_kind"]=="EXISTING_TEST_SURFACE_ONLY"
def test_dm047(): assert D["cases"]["DM047"]["target_kind"]=="EXISTING_TEST_SURFACE_ONLY"
def test_shared_not_generic(): assert D["shared_runtime_target_is_generic_new_mechanism"] is False
def test_create(): assert D["create_authorized"] is False and D["new_runtime_module_authorized"] is False
def test_no_change_yet(): assert D["runtime_mechanisms_modified"] is False
def test_unresolved(): assert all(x["causal_status"]=="UNRESOLVED" for x in D["cases"].values())
def test_backup_required(): assert D["backup_required_before_runtime_refinement"] is True
def test_next(): assert D["next_required_stage"]=="F4-G2.3B_DM011_DM014_MINIMAL_RUNTIME_REFINEMENT"
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
