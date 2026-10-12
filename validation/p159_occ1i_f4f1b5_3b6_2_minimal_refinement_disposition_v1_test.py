import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b6_2_minimal_refinement_disposition_v1.json").read_text())
def test_status(): assert D["status"]=="REFINEMENT_NOT_REQUIRED"
def test_basis(): assert D["basis"]["DM038"]["qualified_protective_families"]>=2 and D["basis"]["DM042"]["qualified_protective_families"]>=2
def test_reuse_first(): assert D["decision"]=="REUSE_SUFFICIENT_NO_REFINEMENT"
def test_no_runtime_change(): assert D["runtime_mechanisms_modified"] is False
def test_no_new_detector(): assert D["new_detectors_created"]==0 and D["create_authorized"] is False
def test_no_mutation_promotion(): assert D["mutation_statuses_changed"] is False
def test_b62_done(): assert D["f4_f1b_5_3b6_2"]=="DONE_NOT_REQUIRED"
def test_boundary(): assert D["next_step_not_opened"] is True
def test_epistemic(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
