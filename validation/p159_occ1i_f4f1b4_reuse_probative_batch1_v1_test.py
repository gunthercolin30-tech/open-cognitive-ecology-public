from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/f4f1b4_reuse_probative_batch1_v1.json"
def d(): return json.loads(P.read_text())
def by(i): return next(x for x in d()["results"] if x["mutation_id"]==i)
def test_cardinality(): assert len(d()["results"])==3
def test_dm005(): assert by("DM005")["replay_status"]=="KILLED" and by("DM005")["mutation_effective"] and by("DM005")["protective_detection"]
def test_dm009(): assert by("DM009")["replay_status"]=="KILLED" and by("DM009")["mutation_effective"] and by("DM009")["protective_detection"]
def test_dm011_conservative(): assert by("DM011")["replay_status"]=="INCONCLUSIVE" and not by("DM011")["mutation_effective"]
def test_integrity(): assert d()["canonical_integrity_preserved"] is True
def test_boundaries(): x=d(); assert not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"]
