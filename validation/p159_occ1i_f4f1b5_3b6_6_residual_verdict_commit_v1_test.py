import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4f1b5_3b6_6_residual_verdict_commit_v1.json").read_text())
C={x["mutation_id"]:x for x in D["cases"]}
def test_status(): assert D["status"]=="RESIDUAL_VERDICTS_COMMITTED"
def test_scope(): assert set(C)=={"DM038","DM042"}
def test_verdicts(): assert all(x["committed_verdict"]=="KILLED" for x in C.values())
def test_bound(): assert all(x["evidence_bound"] for x in C.values())
def test_zero(): assert D["residual_inconclusive_count"]==D["residual_survived_count"]==0
def test_commit(): assert D["mutation_statuses_committed"] and D["canonical_campaign_evidence_committed"]
def test_no_global(): assert not D["global_mutation_registry_modified"]
def test_no_runtime(): assert not D["runtime_mechanisms_modified"] and D["new_detectors_created"]==0
def test_boundary(): assert D["f4_f1b_5_3b6_6"]=="DONE" and D["next_step_not_opened"]
def test_not_closed(): assert not D["b6_closed"] and not D["f4_f1b_6_opened"]
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
