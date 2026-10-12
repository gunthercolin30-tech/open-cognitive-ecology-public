from pathlib import Path
import hashlib,json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/m5_cnp_probative_replay_v1.json"
T=ROOT/"ontology/occ_compiled_normative_profile.py"
EXPECTED="aac11122cf2f8aa71140efa5af3cb650cab8f20cf7f2bcb7c6e0854f4684ac09"
def d(): return json.loads(P.read_text())
def test_canonical_unchanged(): assert hashlib.sha256(T.read_bytes()).hexdigest()==EXPECTED==d()["canonical_target_sha256"]
def test_four_mroot_cases_preserved(): assert {x["mutation_id"] for x in d()["results"]}=={"DM034","DM037","DM038","DM041"} and all(x["historical_status"]=="INCONCLUSIVE" for x in d()["results"])
def test_non_compensatory_two_detector_rule(): assert all((x["replay_status"]=="KILLED")== (x["distinct_protective_detections"]>=2) for x in d()["results"])
def test_no_false_kill(): assert all(x["replay_status"]=="INCONCLUSIVE" for x in d()["results"] if x["distinct_protective_detections"]<2)
def test_boundaries(): x=d();assert x["occ1i_closed"] is False and x["p159_final_lock"] is False and x["p160_opened"] is False
