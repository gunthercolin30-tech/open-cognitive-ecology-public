import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/"validation_artifacts/p159/occ1i"
def L(n): return json.loads((A/n).read_text(encoding="utf-8"))

def test_occ1i_f1_functional_registry_manifest():
    r=L("defensive_mutation_operators_registry_v1.json")
    m=L("defensive_mutation_manifest_v1.json")
    assert r["operator_count"]==57==len(r["operators"])
    assert m["case_count"]==57==len(m["cases"])
    assert len({x["operator_id"] for x in r["operators"]})==57
    assert len({x["mutation_id"] for x in m["cases"]})==57
    assert {x["layer"] for x in r["operators"]}=={"M1","M2","M3","M4","M5","M6","M7"}

def test_occ1i_f1_degradation_contract():
    m=L("defensive_mutation_manifest_v1.json")
    x=L("defensive_detection_matrix_v1.json")
    assert all(c["empirical_status"]=="NOT_RUN" and c["causal_detection_evidence"] is None for c in m["cases"])
    assert all(row["empirical_status"]=="NOT_RUN" and row["observed_detectors"]==[] for row in x["rows"])
    assert all(row["minimum_distinct_detectors"]>=2 for row in x["rows"] if row["criticality"]=="MROOT")
    assert x["empirical_claims_made"] is False

def test_occ1i_f1_non_regression_criticality():
    m=L("defensive_mutation_manifest_v1.json")
    assert set(m["criticality_counts"])=={"MROOT","MCRITICAL","MHIGH","MSTANDARD"}
    assert m["criticality_counts"]["MROOT"]>0 and m["criticality_counts"]["MCRITICAL"]>0
    assert sum(m["criticality_counts"].values())==57
    assert m["mutation_score"] is None

def test_occ1i_f1_boundaries():
    r=L("defensive_mutation_operators_registry_v1.json")
    m=L("defensive_mutation_manifest_v1.json")
    assert r["canonical_write_forbidden"] and r["execution_performed"] is False and r["authorization_created"] is False
    assert m["core_selection_status"]=="NOT_SELECTED" and m["extended_selection_status"]=="NOT_SELECTED"
    assert m["occ1i_closed"] is False and m["occ1j_opened"] is False
    assert m["p159_final_lock"] is False and m["p160_opened"] is False
