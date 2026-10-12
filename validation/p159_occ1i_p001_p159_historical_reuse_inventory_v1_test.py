from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/p001_p159_historical_reuse_inventory_v1.json"
def d(): return json.loads(P.read_text())
def test_exact_open_count(): assert d()["original_f4f1b_inconclusive_count"]==24 and d()["open_inconclusive_count"]==23
def test_resolved_cases(): assert d()["later_resolved"]=={"DM041":"KILLED","DM045":"KILLED"}
def test_no_false_proof(): assert all(x["candidate_matches_are_proof"] is False for x in d()["open_mutations"])
def test_map_identity(): assert len({x["mutation_id"] for x in d()["open_mutations"]})==23
def test_boundaries(): x=d(); assert x["occ1i_closed"] is False and x["p159_final_lock"] is False and x["p160_opened"] is False
