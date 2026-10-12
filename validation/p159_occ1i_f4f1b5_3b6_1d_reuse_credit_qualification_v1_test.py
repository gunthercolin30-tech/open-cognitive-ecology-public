import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b6_1d_reuse_credit_qualification_v1.json").read_text())
C={x["mutation_id"]:x for x in D["cases"]}
def test_status(): assert D["status"]=="REUSE_CREDIT_QUALIFIED"
def test_scope(): assert set(C)=={"DM038","DM042"}
def test_dm038(): assert C["DM038"]["qualified_protective_families"]>=2 and C["DM038"]["qualification"]=="QUALIFIED_FOR_EXISTING_THRESHOLD"
def test_dm042(): assert C["DM042"]["qualified_protective_families"]>=2 and C["DM042"]["qualification"]=="QUALIFIED_FOR_EXISTING_THRESHOLD"
def test_independence(): assert all(x["independence_qualified"] for x in C.values())
def test_no_new_detector(): assert D["new_detectors_created"]==0 and D["runtime_mechanisms_modified"] is False
def test_no_status_promotion(): assert D["mutation_statuses_changed"] is False
def test_b62_not_opened(): assert D["b6_2_opened"] is False and D["next_step_not_opened"] is True
def test_epistemic(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
