from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/f4f1b4_final_reconciliation_close_v1.json"
def d(): return json.loads(P.read_text())
def test_partition(): assert d()["historical_reuse"]==11 and d()["causally_killed"]==7 and d()["reuse_to_extend"]==4 and d()["not_yet_replayed"]==0
def test_identity(): assert d()["historical_reuse"]==d()["causally_killed"]+d()["reuse_to_extend"]+d()["not_yet_replayed"]
def test_killed_ids(): assert d()["ids"]["CAUSALLY_KILLED"]==["DM005","DM007","DM009","DM013","DM023","DM034","DM037"]
def test_extend_ids(): assert d()["ids"]["REUSE_TO_EXTEND"]==["DM011","DM014","DM028","DM047"]
def test_transition(): assert d()["stage_transition"]=={"F4-F1B.4":"CLOSED","F4-F1B.5":"NEXT"}
def test_no_create(): assert d()["create_authorized"] is False
def test_boundaries(): x=d(); assert not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"] and not x["f4g_opened"]
