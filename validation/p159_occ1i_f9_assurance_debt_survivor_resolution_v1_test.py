import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; D=json.loads((R/"validation_artifacts/p159/occ1i/f9_assurance_debt_survivor_resolution_v1.json").read_text())
def test_killed(): assert D["recomputed_counts"]["KILLED"]==49
def test_survived(): assert D["recomputed_counts"]["SURVIVED"]==0
def test_inconclusive(): assert D["recomputed_counts"]["INCONCLUSIVE"]==0
def test_unresolved(): assert D["recomputed_counts"]["UNRESOLVED"]==0
def test_open_ids(): assert D["open_case_ids"]==[]
def test_debt(): assert D["assurance_debt_candidates"]==[]
def test_zero(): assert D["zero_residual_assurance_debt"] is True
def test_qualification(): assert D["qualification"]=="ZERO_RESIDUAL_ASSURANCE_DEBT"
def test_no_new_detector(): assert D["new_detector_created"] is False
def test_no_modification(): assert D["production_runtime_modified"] is False and D["historical_artifacts_modified"] is False
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
def test_boundaries(): assert D["p159_final_lock"] is False and D["p160_opened"] is False
def test_next(): assert D["next_required_stage"]=="F10_MUTATION_CROWN_EVIDENCE_BUNDLE"
