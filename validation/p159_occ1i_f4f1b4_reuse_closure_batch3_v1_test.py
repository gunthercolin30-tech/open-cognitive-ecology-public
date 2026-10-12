from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/f4f1b4_reuse_closure_batch3_v1.json"
def d(): return json.loads(P.read_text())
def by(i): return next(x for x in d()["results"] if x["mutation_id"]==i)
def test_ids(): assert [x["mutation_id"] for x in d()["results"]]==["DM013","DM028","DM034","DM037","DM047"]
def test_kills_require_effective(): assert all(x["mutation_effective"] and x["protective_detection"] for x in d()["results"] if x["replay_status"]=="KILLED")
def test_no_false_promotion(): assert all(x["replay_status"] in ("KILLED","INCONCLUSIVE") for x in d()["results"])
def test_integrity(): assert d()["canonical_integrity_preserved"] is True
def test_historical_immutable(): assert d()["historical_matrix_modified"] is False
def test_boundaries(): x=d(); assert not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"]
