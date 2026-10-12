import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4g2_dm014_direct_exact_replay_v1.json").read_text())
def test_status(): assert D["status"]=="DM014_DIRECT_EXACT_REPLAY_COMPLETE"
def test_effective(): assert D["mutation_effective"] is True
def test_baseline(): assert D["baseline"]["unknown_preserved"] is True
def test_mutant(): assert D["mutant"]["unknown_preserved"] is False
def test_discrimination_consistency():
    assert D["existing_mechanism_discriminates"] == (D["replay_status"]=="KILLED")
def test_fail_closed():
    if not D["existing_mechanism_discriminates"]: assert D["replay_status"]=="INCONCLUSIVE"
def test_credit(): assert D["causal_credit_rule"]=="EXISTING_OCE_EXECUTABLE_MECHANISM_ONLY"
def test_no_create(): assert D["new_detector_created"] is False
def test_no_runtime(): assert D["runtime_mechanisms_modified"] is False
def test_isolated(): assert D["isolated_replay"] is True
def test_next(): assert D["next_required_stage"]=="F4-G2.3_MINIMAL_REFINEMENT_DM011_DM014_DM028_DM047"
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
