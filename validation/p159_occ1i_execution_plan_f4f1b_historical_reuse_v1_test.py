from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/occ1i_execution_plan_f4f1b_historical_reuse_v1.json"
def d(): return json.loads(P.read_text())
def test_order(): assert d()["methodological_order"]==["REUSE","EXTEND","CREATE"]
def test_matrix_counts(): assert d()["source_matrix"]["counts"]=={"REUSE":11,"EXTEND":6,"CREATE_CANDIDATE":6}
def test_next_is_reuse_replay(): assert [s["id"] for s in d()["substeps"] if s["status"]=="NEXT"]==["F4-F1B.4"]
def test_no_create_promotion(): assert {s["id"]:s for s in d()["substeps"]}["F4-F1B.6"]["create_candidate_is_create_required"] is False
def test_downstream_preserved(): assert d()["downstream_unchanged"]==["F4-G","F4-H","F5","F6","F7","F8","F9","F10","F11","F12"]
def test_boundaries():
 x=d(); assert x["mutation_statuses_changed_by_plan_update"] is False and not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"]
