import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b6_3_functional_degradation_validation_v1.json").read_text())
def test_status(): assert D["status"]=="FUNCTIONAL_DEGRADATION_VALIDATED"
def test_nominal(): assert D["functional"]["reuse_sufficient"] is True
def test_dm038(): assert D["functional"]["DM038"]["families"]>=2
def test_dm042(): assert D["functional"]["DM042"]["families"]>=2
def test_degradation_one_family(): assert D["degradation"]["single_family_loss"]["reuse_sufficient"] is False
def test_degradation_credit_loss(): assert D["degradation"]["credit_revoked"]["reuse_sufficient"] is False
def test_fail_closed(): assert D["degradation"]["fail_closed"] is True
def test_no_runtime_change(): assert D["runtime_mechanisms_modified"] is False and D["mutation_statuses_changed"] is False
def test_boundary(): assert D["f4_f1b_5_3b6_3"]=="DONE" and D["next_step_not_opened"] is True
def test_epistemic(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
