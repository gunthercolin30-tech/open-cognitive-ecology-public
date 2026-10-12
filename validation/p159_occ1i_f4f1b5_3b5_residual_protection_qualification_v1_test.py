import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b5_residual_protection_qualification_v1.json").read_text())
C={x["mutation_id"]:x for x in D["cases"]}
def test_scope(): assert set(C)=={"DM038","DM042"}
def test_dm038_gap(): assert C["DM038"]["qualification"]=="EXTEND_REQUIRED" and C["DM038"]["existing_admissible_protection_count"]==0
def test_dm038_diagnostic_not_detector(): assert C["DM038"]["diagnostic_cross_binding_observation_exists"] is True and C["DM038"]["diagnostic_observation_counted_as_detector"] is False
def test_dm042_gap(): assert C["DM042"]["qualification"]=="EXTEND_REQUIRED" and C["DM042"]["existing_admissible_protection_count"]==1 and C["DM042"]["existing_protection"]==["CNP_VERIFY_PROFILE"]
def test_independence_preserved(): assert C["DM042"]["canonical_verifier_control_counted_as_detector"] is False and C["DM042"]["mutated_verifier_counted_as_detector"] is False
def test_no_new_primitive(): assert D["summary"]["new_primitive_required"]==0 and D["summary"]["create_authorized"] is False
def test_no_runtime_change(): assert D["summary"]["runtime_mechanisms_modified"] is False and D["summary"]["mutation_statuses_changed"] is False
def test_next(): assert D["f4_f1b_5_3b5"]=="DONE" and D["f4_f1b_5_3b6"]=="NEXT"
def test_epistemic(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
