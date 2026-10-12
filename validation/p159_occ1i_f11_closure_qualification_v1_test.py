import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; D=json.loads((R/"validation_artifacts/p159/occ1i/f11_closure_qualification_v1.json").read_text())
def test_checks(): assert len(D["checks"])==7 and all(D["checks"].values())
def test_eligible(): assert D["closure_eligible"] is True
def test_qualification(): assert D["qualification"]=="QUALIFIED_FOR_FINAL_CLOSURE"
def test_no_lock(): assert D["final_lock_written"] is False and D["p159_final_lock"] is False
def test_p160(): assert D["p160_opened"] is False
def test_no_runtime(): assert D["production_runtime_modified"] is False
def test_no_history(): assert D["historical_artifacts_modified"] is False
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
def test_next(): assert D["next_required_stage"]=="F12_FINAL_CLOSURE_POST_CLOSE_VERIFICATION"
