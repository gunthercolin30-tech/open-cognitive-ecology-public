from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/f4f1b5_extend_functional_dedup_v1.json"
def d(): return json.loads(P.read_text())
def test_ten(): assert len(d()["candidates"])==10 and len(set(d()["candidates"]))==10
def test_sources(): assert d()["origin_counts"]=={"HISTORICAL_EXTEND":6,"REUSE_TO_EXTEND":4}
def test_partition(): assert sum(len(x["mutation_ids"]) for x in d()["families"])==10
def test_unique_partition(): assert sorted(i for x in d()["families"] for i in x["mutation_ids"])==sorted(d()["candidates"])
def test_no_creation(): assert d()["create_authorized"] is False and d()["mechanisms_modified"] is False
def test_stage(): assert d()["stage_transition"]=={"F4-F1B.5":"IN_PROGRESS","F4-F1B.5.1":"DONE","F4-F1B.5.2":"NEXT"}
def test_boundaries(): x=d(); assert not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"]
