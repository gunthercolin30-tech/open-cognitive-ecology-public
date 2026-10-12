import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b6_1b_dm042_surface_discovery_v1.json").read_text())
def test_status(): assert D["status"]=="REUSE_CANDIDATES_IDENTIFIED"
def test_two_families(): assert len(D["surfaces"])==2 and len({x["family"] for x in D["surfaces"]})==2
def test_postclose_independent(): assert D["surfaces"][1]["independent_from_closing_transaction_execution"] is True
def test_dm038_reuse(): assert D["DM038"]["refined_disposition"]=="REUSE_REPLAY_REQUIRED"
def test_dm042_reuse(): assert D["DM042"]["refined_disposition"]=="REUSE_REPLAY_REQUIRED"
def test_no_credit_yet(): assert D["detector_credit_assigned"] is False and D["mutation_statuses_changed"] is False
def test_no_extension_yet(): assert D["new_primitive_required"] is False and D["runtime_mechanisms_modified"] is False and D["create_authorized"] is False
def test_next(): assert D["f4_f1b_5_3b6_1b"]=="DONE" and D["f4_f1b_5_3b6_1c"]=="NEXT_CAUSAL_REUSE_REPLAY"
def test_epistemic(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
