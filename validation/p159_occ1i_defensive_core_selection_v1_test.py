import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"validation_artifacts/p159/occ1i/defensive_core_selection_v1.json"
def L(): return json.loads(P.read_text(encoding="utf-8"))

def test_occ1i_f2_functional_core_seal():
    x=L(); assert x["status"]=="CORE_SELECTED_AND_SEALED_PRE_EXECUTION"
    assert x["core_count"]==32==len(x["core_ids"])
    assert len(set(x["core_ids"]))==32
    assert set(x["layer_counts"])=={"M1","M2","M3","M4","M5","M6","M7"}
    assert all(v>0 for v in x["layer_counts"].values())
    assert {"DM050","DM055"}.issubset(set(x["core_ids"]))

def test_occ1i_f2_degradation_pending_extended():
    x=L()
    assert x["empirical_execution"] is False and x["mutation_score"] is None
    assert x["deferred_mroot_count"]>0
    assert all(v=="PENDING_EXTENDED" for v in x["deferred_mroot_disposition"].values())
    assert not set(x["core_ids"]) & set(x["deferred_mroot_ids"])

def test_occ1i_f2_non_regression_bindings():
    x=L()
    assert x["registry_sha256"]=="7751c75ef846bbb3f3ded595ab525d725a1359874735a19054af571868945720"
    assert x["manifest_sha256"]=="17b33b07763470fbc760d4260df02187d6e74587e1f6486824ff357f64af64e9"
    assert x["matrix_sha256"]=="210c9637ae97a7700fde9e3f9555c5e577ff8d4a6fdd69b245f074888e927e67"
    assert x["all_core_status"]=="NOT_RUN"
    assert x["all_deferred_mroot_status"]=="PENDING_EXTENDED"

def test_occ1i_f2_boundaries():
    x=L()
    assert x["canonical_write_forbidden"] is True
    assert x["authorization_created"] is False
    assert x["execution_performed"] is False
    assert x["occ1i_closed"] is False and x["occ1j_opened"] is False
    assert x["p159_final_lock"] is False and x["p160_opened"] is False
