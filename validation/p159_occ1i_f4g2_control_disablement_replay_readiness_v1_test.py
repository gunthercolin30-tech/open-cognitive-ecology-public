import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4g2_control_disablement_replay_readiness_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G2_CONTROL_DISABLEMENT_REPLAY_READINESS_COMPLETE"
def test_dm014(): assert D["cases"]["DM014"]["replayability"]=="DIRECT_EXECUTABLE_REPLAY"
def test_dm011(): assert D["cases"]["DM011"]["replayability"]=="REFINEMENT_REQUIRED_BEFORE_EXACT_REPLAY"
def test_dm028(): assert D["cases"]["DM028"]["replayability"]=="REFINEMENT_REQUIRED_BEFORE_EXACT_REPLAY"
def test_dm047(): assert D["cases"]["DM047"]["replayability"]=="REFINEMENT_REQUIRED_BEFORE_EXACT_REPLAY"
def test_no_verdicts(): assert all(x["causal_status"]=="UNRESOLVED" for x in D["cases"].values())
def test_counts(): assert D["direct_replay_count"]==1 and D["refinement_required_count"]==3
def test_create(): assert D["create_authorized"] is False
def test_runtime(): assert D["runtime_mechanisms_modified"] is False
def test_next(): assert D["next_required_stage"]=="F4-G2.2A_DM014_DIRECT_EXACT_REPLAY"
def test_g23(): assert D["g2_3_required_for"]==["DM011","DM028","DM047"]
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
