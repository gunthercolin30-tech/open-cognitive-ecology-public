import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b6_5_residual_protection_qualification_v1.json").read_text())
C={x["mutation_id"]:x for x in D["cases"]}
def test_status(): assert D["status"]=="RESIDUAL_PROTECTION_QUALIFIED"
def test_scope(): assert set(C)=={"DM038","DM042"}
def test_dm038(): assert C["DM038"]["verdict"]=="KILLED" and C["DM038"]["qualified_protective_families"]>=2
def test_dm042(): assert C["DM042"]["verdict"]=="KILLED" and C["DM042"]["qualified_protective_families"]>=2
def test_effective(): assert all(x["mutation_effective"] for x in C.values())
def test_reproducible(): assert all(x["causal_replay_reproducible"] for x in C.values())
def test_degradation(): assert D["degradation_fail_closed_confirmed"] is True
def test_no_runtime_change(): assert D["runtime_mechanisms_modified"] is False and D["new_detectors_created"]==0
def test_status_scope(): assert D["mutation_statuses_changed"] is True and D["mutation_status_change_scope"]==["DM038","DM042"]
def test_no_registry_write(): assert D["mutation_registry_modified"] is False
def test_boundary(): assert D["f4_f1b_5_3b6_5"]=="DONE" and D["next_step_not_opened"] is True
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
