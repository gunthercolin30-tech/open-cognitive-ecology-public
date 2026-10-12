import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b4_exact_residual_causal_replay_v1.json").read_text())
C={x["mutation_id"]:x for x in D["cases"]}
def test_scope(): assert set(C)=={"DM038","DM042"}
def test_dm038_exact_stimulus(): assert C["DM038"]["mutation_effective"] is True and C["DM038"]["cross_binding_reconciliation"]["binding_equal"] is False
def test_dm038_fail_closed(): assert C["DM038"]["verdict"] in {"KILLED","INCONCLUSIVE"} and C["DM038"]["minimum_distinct_detectors"]==2
def test_dm042_exact_stimulus(): assert C["DM042"]["mutation_effective"] is True and C["DM042"]["mutated_verifier_accepted_false_hash"] is True
def test_dm042_independence(): assert C["DM042"]["mutated_verifier_eligible_as_independent_detector"] is False and C["DM042"]["canonical_verifier_control_eligible_as_independent_detector"] is False
def test_dm042_cnp_independent(): assert C["DM042"]["cnp_independent_check"]["status"]=="FAIL" and C["DM042"]["cnp_independent_check"]["reason"]=="ARTIFACT_HASH_MISMATCH"
def test_no_survivor_promotion(): assert D["summary"]["survived"]==0
def test_no_creation_or_mechanism_change(): assert D["summary"]["new_detectors_created"]==0 and D["summary"]["mechanisms_modified"] is False and D["create_authorized"] is False
def test_next(): assert D["f4_f1b_5_3b4"]=="DONE" and D["f4_f1b_5_3b5"]=="NEXT"
def test_epistemic(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
