from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/f4f1b4_reuse_probative_batch2_v1.json"
def d(): return json.loads(P.read_text())
def by(i): return next(x for x in d()["results"] if x["mutation_id"]==i)
def test_dm007(): assert by("DM007")["replay_status"]=="KILLED" and by("DM007")["mutation_effective"] and by("DM007")["protective_detection"]
def test_dm014_conservative(): assert by("DM014")["replay_status"]=="INCONCLUSIVE" and not by("DM014")["mutation_effective"]
def test_dm023(): assert by("DM023")["replay_status"]=="KILLED" and by("DM023")["distinct_protective_detections"]>=2
def test_counts(): assert d()["killed"]==2 and d()["inconclusive"]==1
def test_integrity(): assert d()["canonical_integrity_preserved"] is True
def test_boundaries(): x=d(); assert not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"]
