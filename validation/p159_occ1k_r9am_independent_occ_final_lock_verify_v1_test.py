from copy import deepcopy
from validation import p159_occ1k_r9am_independent_occ_final_lock_verify_v1 as v

def test_real_evidence_verified():
    x = v.verify()
    assert x["status"] == "VERIFIED"
    assert x["lock_ready"] is True

def test_all_checks_pass():
    x = v.verify()
    assert x["checks_passed"] == x["checks_total"]

def test_b12_degradation_rejected():
    x = deepcopy(v.load(v.PATHS["r9ai"]))
    x["fl_b12"] = "INCONCLUSIVE"
    assert v.verify({"r9ai": x})["status"] == "REJECTED"

def test_meta_degradation_rejected():
    x = deepcopy(v.load(v.PATHS["r9aj"]))
    x["failed"] = 1
    assert v.verify({"r9aj": x})["status"] == "REJECTED"

def test_mutation_survivor_rejected():
    x = deepcopy(v.load(v.PATHS["r9ak"]))
    x["mroot_survived"] = 1
    assert v.verify({"r9ak": x})["status"] == "REJECTED"

def test_debt_unresolved_rejected():
    x = deepcopy(v.load(v.PATHS["r9al"]))
    x["superseding_debt_assessment"]["status"] = "UNRESOLVED"
    assert v.verify({"r9al": x})["status"] == "REJECTED"

def test_crossbinding_hash_mismatch_rejected():
    x = deepcopy(v.load(v.PATHS["r9ag_verify"]))
    x["hash_mismatches"] = 1
    assert v.verify({"r9ag_verify": x})["status"] == "REJECTED"

def test_read_only_no_repair_or_transition():
    x = v.verify()
    assert not x["repairs_performed"] and not x["transition_receipt_created"]
    assert not x["compiler_invoked"]

def test_no_lock_grant_or_p160b():
    x = v.verify()
    assert x["lock_ready"] is True
    assert x["lock_granted"] is False
    assert x["p160b_opened"] is False

def test_deterministic():
    assert v.verify() == v.verify()
