import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; D=json.loads((R/"validation_artifacts/p159/occ1i/f8_detection_matrix_consolidation_v1.json").read_text()); rows=D["rows"]
def test_total(): assert len(rows)==49 and D["coverage"]["total_expected"]==D["coverage"]["total_killed"]==49
def test_mroot(): assert sum(x["class"]=="MROOT" for x in rows)==43
def test_meta(): assert sum(x["class"]=="META_MUTATION" for x in rows)==6
def test_all_killed(): assert all(x["verdict"]=="KILLED" for x in rows)
def test_no_open_cases(): assert D["coverage"]["inconclusive"]==0 and D["coverage"]["unresolved"]==0
def test_threshold(): assert all(x["minimum_distinct_detectors"]==2 for x in rows)
def test_meta_detectors(): assert all(x["distinct_protective_detections"]>=2 for x in rows if x["class"]=="META_MUTATION")
def test_unique(): assert len({x["id"] for x in rows})==49
def test_debt(): assert D["assurance_debt_candidates"]==[]
def test_no_new_detector(): assert D["new_detector_created"] is False
def test_no_modification(): assert D["production_runtime_modified"] is False and D["historical_artifacts_modified"] is False
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
def test_boundaries(): assert D["p159_final_lock"] is False and D["p160_opened"] is False
def test_next(): assert D["next_required_stage"]=="F9_ASSURANCE_DEBT_SURVIVOR_RESOLUTION"
