import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; D=json.loads((R/"validation_artifacts/p159/occ1i/f7b_meta_mutation_crown_v1.json").read_text())
EXPECTED={"MM01_DROP_MROOT","MM02_FAKE_KILLED","MM03_LOWER_THRESHOLD","MM04_TAMPER_COUNTS","MM05_ALTER_IDENTITY_HASH","MM06_SUBSTITUTE_PROVENANCE"}
def test_cases(): assert set(D["cases"])==EXPECTED
def test_effective(): assert all(x["mutation_effective"] for x in D["cases"].values())
def test_threshold(): assert all(x["minimum_distinct_detectors"]==2 for x in D["cases"].values())
def test_accounting(): assert D["killed_count"]+D["inconclusive_count"]==6
def test_verdict_rule(): assert all(x["causal_verdict"]==("KILLED" if x["distinct_protective_detections"]>=2 else "INCONCLUSIVE") for x in D["cases"].values())
def test_family_accounting(): assert all(x["distinct_protective_detections"]==sum(1 for f in x["protective_families"].values() if f["detected"]) for x in D["cases"].values())
def test_no_history_change(): assert D["historical_artifacts_modified"] is False
def test_no_runtime_change(): assert D["production_runtime_modified"] is False
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
def test_boundaries(): assert D["p159_final_lock"] is False and D["p160_opened"] is False
def test_next(): assert D["next_required_stage"] in {"F7_B_GAP_REFINEMENT","F8_DETECTION_MATRIX_CONSOLIDATION"}
