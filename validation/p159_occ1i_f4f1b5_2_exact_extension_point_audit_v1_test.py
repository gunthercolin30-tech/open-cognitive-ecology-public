from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/f4f1b5_2_exact_extension_point_audit_v1.json"
def d(): return json.loads(P.read_text())
def test_coverage(): assert sorted(i for f in d()["families"] for i in f["mutation_ids"])==sorted(d()["candidates"]) and len(d()["candidates"])==10
def test_seven(): assert len(d()["families"])==7
def test_no_change_yet(): assert d()["mechanisms_modified"] is False and d()["create_authorized"] is False
def test_targets_exist(): assert all(all((ROOT/p).is_file() for p in f["extension_files"]) for f in d()["families"])
def test_decisions(): assert set(f["audit_decision"] for f in d()["families"]) <= {"REFINE_EXISTING_TEST_SURFACE","REFINE_EXISTING_VERIFIER_AND_TEST_SURFACE"}
def test_stage(): assert d()["stage_transition"]=={"F4-F1B.5.2":"DONE","F4-F1B.5.3":"NEXT"}
def test_boundaries(): x=d(); assert not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"]
