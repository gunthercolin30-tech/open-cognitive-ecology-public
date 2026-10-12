import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4g1_dm002_exact_causal_replay_v1.json").read_text())
def test_status(): assert D["status"]=="DM002_EXACT_CAUSAL_REPLAY_COMPLETE"
def test_effective(): assert D["mutation_effective"] is True
def test_isolated(): assert D["isolated_copy_only"] is True
def test_anchor(): assert D["anchor_mutation"]["from"] is False and D["anchor_mutation"]["to"] is True
def test_detectors(): assert D["distinct_protective_detections"]>=2
def test_families(): assert len(set(D["protective_families"]))>=2
def test_verdict(): assert D["replay_status"]=="KILLED"
def test_no_runtime(): assert not D["runtime_mechanisms_modified"]
def test_no_registry(): assert not D["mutation_registry_modified"]
def test_g1(): assert D["g1_resolution_candidate"] is True and D["g1_closed"] is False
def test_boundary(): assert D["f4g2_opened"] is False and D["next_step_not_opened"] is True
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
