import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4h_core_qualification_v1.json").read_text())
def test_status(): assert D["status"]=="F4_H_CORE_QUALIFIED"
def test_checks(): assert D["qualification_passed"] is True and all(D["qualification_checks"].values())
def test_core(): assert D["core_total"]==32 and D["core_killed"]==32
def test_no_survivors(): assert D["core_survived"]==0
def test_no_inconclusive(): assert D["core_inconclusive"]==0
def test_no_unresolved(): assert D["core_unresolved"]==0
def test_ratio(): assert D["core_kill_ratio"]==1.0
def test_blockers_closed(): assert D["blocker_resolution_closed"] is True
def test_f4_qualified(): assert D["f4_core_campaign_qualified"] is True
def test_no_f4h_mutation(): assert D["production_runtime_modified_by_f4h"] is False and D["historical_artifacts_modified_by_f4h"] is False
def test_evidence(): assert len(D["evidence_sha256"])==2 and all(len(x)==64 for x in D["evidence_sha256"].values())
def test_global_validation_required(): assert D["global_validation_required"] is True
def test_next(): assert D["next_required_stage"]=="F5_EXTENDED_CORPUS_EXPANSION"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
def test_no_p160(): assert D["p159_final_lock"] is False and D["p160_opened"] is False
