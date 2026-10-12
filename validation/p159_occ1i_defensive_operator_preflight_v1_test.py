import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"validation_artifacts/p159/occ1i/defensive_operator_preflight_v1.json"
def L(): return json.loads(P.read_text(encoding="utf-8"))
def test_f4a_functional_accounting():
    x=L(); assert x["core_count"]==32; assert x["ready_count"]+x["unresolved_count"]==32
    assert len(x["results"])==32 and len({r["mutation_id"] for r in x["results"]})==32
    assert all(r["criticality"]=="MROOT" and r["empirical_status"]=="NOT_RUN" for r in x["results"])
def test_f4a_concrete_probe_and_binding_contract():
    x=L()
    for r in x["results"]:
        if r["preflight_status"]=="READY_FOR_ISOLATED_EXECUTION":
            assert r["target"]["exists"] and r["synthetic_probe"]["defined"] and r["synthetic_probe"]["changed_hash"]
            assert all(d["resolved"] for d in r["detector_bindings"])
def test_f4a_fail_closed_gate():
    x=L(); assert x["f4b_allowed"]==(x["unresolved_count"]==0)
    assert (x["status"]=="PREFLIGHT_READY")==x["f4b_allowed"]
    assert x["core_execution"] is False and x["empirical_core_results"]==0 and x["mutation_score"] is None
def test_f4a_boundaries_non_regression():
    x=L(); assert x["preflight_only"] and x["synthetic_probe_only"] and x["canonical_targets_modified"] is False
    assert not x["occ1i_closed"] and not x["occ1j_opened"] and not x["p159_final_lock"] and not x["p160_opened"]
