import json
from pathlib import Path
P=Path(__file__).parents[1]/"validation_artifacts/p159/occ1i/f4f1b5_3b2_independent_detector_replay_v1.json"
D=json.loads(P.read_text())
def test_schema(): assert D["schema"]=="oce.p159.occ1i.f4f1b5.3b2.independent_detector_replay.v1"
def test_cases(): assert [x["mutation_id"] for x in D["cases"]]==["DM019","DM020","DM021","DM038","DM042"]
def test_effective(): assert all(x.get("mutation_effective") is True for x in D["cases"])
def test_no_false_survival(): assert D["survived"]==0
def test_threshold(): assert all(x.get("verdict")!="KILLED" or x.get("distinct_protective_detection_count",0)>=2 for x in D["cases"])
def test_dm042_independence():
 x=next(x for x in D["cases"] if x["mutation_id"]=="DM042"); assert x.get("independent_verifier_eligible") is False
def test_boundaries(): assert D["mechanisms_modified"] is False and D["mutation_registry_modified"] is False and D["create_authorized"] is False
def test_epistemic(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
