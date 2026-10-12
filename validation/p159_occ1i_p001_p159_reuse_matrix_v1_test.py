from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/p001_p159_reuse_matrix_v1.json"
def d(): return json.loads(P.read_text())
def test_23_rows(): assert len(d()["rows"])==23
def test_partition(): assert sum(d()["counts"].values())==23
def test_no_promotion(): assert all(not r["causal_reclassification_to_killed_authorized"] for r in d()["rows"])
def test_evidence_exists(): assert all((ROOT/f).is_file() for r in d()["rows"] for f in r["evidence_files"])
def test_boundaries(): x=d(); assert not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"]
