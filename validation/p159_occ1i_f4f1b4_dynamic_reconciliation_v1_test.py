from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/f4f1b4_dynamic_reconciliation_v1.json"
def d(): return json.loads(P.read_text())
def test_historical_snapshot(): assert d()["historical_snapshot"]=={"REUSE":11,"EXTEND":6,"CREATE_CANDIDATE":6}
def test_reuse_partition(): assert d()["reuse_dynamic"]=={"CAUSALLY_KILLED":4,"REUSE_TO_EXTEND":2,"NOT_YET_REPLAYED":5}
def test_killed_ids(): assert d()["ids"]["CAUSALLY_KILLED"]==["DM005","DM007","DM009","DM023"]
def test_extend_ids(): assert d()["ids"]["REUSE_TO_EXTEND"]==["DM011","DM014"]
def test_remaining_ids(): assert d()["ids"]["NOT_YET_REPLAYED"]==["DM013","DM028","DM034","DM037","DM047"]
def test_no_history_rewrite(): assert d()["historical_matrix_modified"] is False and d()["mutation_registry_modified"] is False
def test_boundaries(): x=d(); assert not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"]
