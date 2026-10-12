from copy import deepcopy
from validation import p159_occ1k_r9am2_schema_aware_independent_occ_final_lock_verify_v2 as v

def test_zero_cardinality_schema():
    assert v.zero_cardinality([]) and v.zero_cardinality(0)
    assert not v.zero_cardinality(["x"]) and not v.zero_cardinality(1)

def test_real_evidence_verified():
    x=v.verify(); assert x["status"]=="VERIFIED" and x["lock_ready"] is True

def test_all_checks_pass():
    x=v.verify(); assert x["checks_passed"]==12 and x["checks_total"]==12

def test_crossbinding_actual_list_schema_passes():
    x=deepcopy(v.load(v.PATHS["r9ag_verify"]))
    assert isinstance(x["missing_files"],list) and isinstance(x["hash_mismatches"],list)
    assert v.verify({"r9ag_verify":x})["checks"]["crossbinding_verified"] is True

def test_crossbinding_missing_file_rejected():
    x=deepcopy(v.load(v.PATHS["r9ag_verify"])); x["missing_files"]=["missing"]
    assert v.verify({"r9ag_verify":x})["status"]=="REJECTED"

def test_crossbinding_hash_mismatch_rejected():
    x=deepcopy(v.load(v.PATHS["r9ag_verify"])); x["hash_mismatches"]=["bad"]
    assert v.verify({"r9ag_verify":x})["status"]=="REJECTED"

def test_crossbinding_status_required():
    x=deepcopy(v.load(v.PATHS["r9ag_verify"])); x["status"]="INCONCLUSIVE"
    assert v.verify({"r9ag_verify":x})["status"]=="REJECTED"

def test_mutation_survivor_rejected():
    x=deepcopy(v.load(v.PATHS["r9ak"])); x["mroot_survived"]=1
    assert v.verify({"r9ak":x})["status"]=="REJECTED"

def test_historical_r9am_not_rewritten():
    x=v.verify(); assert x["historical_r9am"]["rewritten"] is False

def test_no_transition_or_lock_grant():
    x=v.verify()
    assert x["transition_receipt_created"] is False
    assert x["lock_granted"] is False and x["p160b_opened"] is False

def test_deterministic():
    assert v.verify()==v.verify()
