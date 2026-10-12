from pathlib import Path
from ontology.occ1h_a040_rrp21_governed_expiry_materializer import PASS,run_discriminating_experiment
from ontology.occ1h_a040_rrp22_independent_requalification import independently_requalify
ROOT=Path(__file__).resolve().parents[1]
def test_rrp22_independent_requalification():
    r21=run_discriminating_experiment(ROOT); assert r21["status"]==PASS
    r22=independently_requalify(ROOT,r21); assert r22["status"]==PASS
    assert r22["implementation_module_used_as_oracle"] is False and r22["compiler_used_as_oracle"] is False
    q=r22["qualification"]; assert q["materiality"]=="ROOT"
    assert q["rrp22_status"]=="INDEPENDENT_REQUALIFICATION_PASSED" and q["return_to_rrp9_rrp12"] is True
    assert q["closure_eligible_now"] is False
def test_rrp22_rejects_unproven_rrp21():
    r=independently_requalify(ROOT,{"status":"PASS","rrp21_status":"NOT_PROVEN","evidence":{}})
    assert r["status"]!="PASS"
