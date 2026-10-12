from pathlib import Path
from ontology.occ1h_a040_rrp21_governed_expiry_materializer import PASS,FAIL,materialize_contract,evaluate_exception,run_discriminating_experiment
ROOT=Path(__file__).resolve().parents[1]
def test_rrp21_contract_and_experiment():
    m=materialize_contract(ROOT); assert m["status"]==PASS; assert m["contract"]["norm_ops"]==["CHECK_EXPIRY"]
    r=run_discriminating_experiment(ROOT); assert r["status"]==PASS
    assert r["rrp21_status"]=="REMEDIATION_IMPLEMENTED_AND_EXPERIMENTALLY_DISCRIMINATED"
    assert r["occ1h_closed"] is False and r["p160_opened"] is False
def test_rrp21_degradation_fail_closed():
    c=materialize_contract(ROOT)["contract"]
    bad=evaluate_exception(c,{"exception_id":"x","authorized":True,"clock_consistent":False,"expires_at":"2030-01-01T00:00:00Z","now":"2029-12-31T00:00:00Z"})
    assert bad["status"]==PASS and bad["applicable"] is False
    missing=evaluate_exception(c,{"authorized":True,"clock_consistent":True,"expires_at":"2030-01-01T00:00:00Z","now":"2029-12-31T00:00:00Z"})
    assert missing["status"]==FAIL and missing["applicable"] is False
