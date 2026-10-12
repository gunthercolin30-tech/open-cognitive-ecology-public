import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4g0_core_blocker_resolution_intake_v1.json").read_text())
def test_status(): assert D["status"]=="CORE_BLOCKER_RESOLUTION_INTAKE_LOCKED"
def test_count(): assert D["blocker_count"]==11
def test_partition(): assert D["partition_counts"]=={"PROVENANCE_DEBT":1,"REUSE_TO_EXTEND":4,"CREATE_CANDIDATE":6}
def test_dm002(): assert D["work_packages"][0]["ids"]==["DM002"]
def test_reuse(): assert set(D["work_packages"][1]["ids"])=={"DM011","DM014","DM028","DM047"}
def test_create(): assert set(D["work_packages"][2]["ids"])=={"DM003","DM015","DM017","DM018","DM022","DM033"}
def test_order(): assert [x["work_package"] for x in D["work_packages"]]==["G1","G2","G3"]
def test_no_create_auth(): assert D["create_authorized"] is False
def test_no_promotion(): assert D["blockers_promoted"] is False
def test_no_runtime(): assert not D["runtime_mechanisms_modified"]
def test_boundary(): assert D["f4g0"]=="DONE" and D["f4g1_opened"] is False
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
