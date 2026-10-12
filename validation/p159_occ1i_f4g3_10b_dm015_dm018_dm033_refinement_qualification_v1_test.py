import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_10b_dm015_dm018_dm033_refinement_qualification_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G3_10B_DM015_DM018_DM033_REFINEMENT_QUALIFICATION_COMPLETE"
def test_all_qualified(): assert all(D["results"][x]["qualification"]=="QUALIFIED" for x in ("DM015","DM018","DM033"))
def test_nominal(): assert all(all(v["nominal"]=="PASS" for v in D["results"][x]["surfaces"].values()) for x in D["results"])
def test_degradation(): assert all(all(v["degradation"]=="PASS" for v in D["results"][x]["surfaces"].values()) for x in D["results"])
def test_failclosed(): assert all(all(v["invalid_fail_closed"]=="PASS" for v in D["results"][x]["surfaces"].values()) for x in D["results"])
def test_determinism(): assert all(all(v["determinism"]=="PASS" for v in D["results"][x]["surfaces"].values()) for x in D["results"])
def test_no_drift(): assert D["source_drift"]=="NONE"
def test_lineage(): assert D["lineage_continuity"] is True
def test_no_runtime_change(): assert D["production_runtime_modified"] is False and D["test_only_qualification"] is True
def test_no_create(): assert D["new_detector_created"] is False and D["create_authorized"] is False
def test_no_verdict(): assert D["causal_verdicts_assigned"] is False and all(D["results"][x]["causal_verdict"]=="UNCHANGED_INCONCLUSIVE" for x in D["results"])
def test_next(): assert D["next_required_stage"]=="F4-G3.10C_DM015_DM018_DM033_EXACT_CAUSAL_REPLAYS"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
