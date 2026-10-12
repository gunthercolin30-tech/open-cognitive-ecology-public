import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4f1b5_3b6_7_b6_closure_qualification_v1.json").read_text())
def test_status(): assert D["status"]=="B6_CLOSURE_QUALIFIED"
def test_residuals(): assert D["residual_inconclusive_count"]==0 and D["residual_survived_count"]==0
def test_commit(): assert D["residual_verdicts_committed"] is True
def test_reuse(): assert D["reuse_sufficient_no_refinement"] is True
def test_degradation(): assert D["degradation_fail_closed"] is True
def test_replay(): assert D["causal_replay_reproducible"] is True
def test_no_runtime(): assert not D["runtime_mechanisms_modified"] and D["new_detectors_created"]==0
def test_closed(): assert D["b6_closed"] is True and D["f4_f1b_5_3b6_7"]=="DONE"
def test_boundary(): assert D["f4_f1b_6_opened"] is False and D["next_step_not_opened"] is True
def test_no_final_lock(): assert D["p159_final_lock"] is False and D["p160_opened"] is False
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
