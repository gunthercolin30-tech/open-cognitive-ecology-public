import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b6_4_exact_isolated_causal_replay_v1.json").read_text())
C={x["mutation_id"]:x for x in D["cases"]}
def test_status(): assert D["status"]=="EXACT_ISOLATED_CAUSAL_REPLAY_VALIDATED"
def test_scope(): assert set(C)=={"DM038","DM042"}
def test_dm038(): assert C["DM038"]["mutation_effective"] and C["DM038"]["closing_rejected"] and C["DM038"]["postclose_rejected"]
def test_dm042(): assert C["DM042"]["mutation_effective"] and C["DM042"]["closing_rejected"] and C["DM042"]["postclose_rejected"]
def test_threshold(): assert all(x["qualified_protective_families"]>=2 for x in C.values())
def test_reproducible(): assert all(x["reproducible_with_b61c"] for x in C.values())
def test_degradation_link(): assert D["degradation_fail_closed_confirmed"] is True
def test_no_patch(): assert D["runtime_mechanisms_modified"] is False and D["new_detectors_created"]==0
def test_no_promotion(): assert D["mutation_statuses_changed"] is False
def test_boundary(): assert D["f4_f1b_5_3b6_4"]=="DONE" and D["next_step_not_opened"] is True
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
