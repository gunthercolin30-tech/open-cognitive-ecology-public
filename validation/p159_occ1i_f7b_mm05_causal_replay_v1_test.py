import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; D=json.loads((R/"validation_artifacts/p159/occ1i/f7b_mm05_causal_replay_v1.json").read_text())
def test_mutation(): assert D["mutation"]=="MM05_ALTER_IDENTITY_HASH" and D["mutation_effective"] is True
def test_internal(): assert D["protective_families"]["internal_identity_recalculation"]["detected"] is True
def test_external(): assert D["protective_families"]["external_identity_seal"]["detected"] is True
def test_distinct(): assert D["distinct_protective_detections"]==2
def test_threshold(): assert D["minimum_distinct_detectors"]==2
def test_verdict(): assert D["causal_verdict"]=="KILLED"
def test_no_runtime(): assert D["production_runtime_modified"] is False
def test_no_history(): assert D["historical_artifacts_modified"] is False
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
def test_boundaries(): assert D["p159_final_lock"] is False and D["p160_opened"] is False
def test_next(): assert D["next_required_stage"]=="F8_DETECTION_MATRIX_CONSOLIDATION"
