from validation import p159_occ1k_canonical_completeness_reaudit_v1 as a
def test_preserves_history_and_boundaries():
    r=a.audit(); assert r["historical_lock_preserved"] is True
    assert r["historical_lock"]["lock_exists"] and r["historical_lock"]["postlock_exists"]
    assert not r["p160b_opened"] and not r["authorization_created"] and not r["execution_performed"]
def test_detects_current_annex_completeness_gap():
    r=a.audit(); assert r["status"]=="REVISION_REQUIRED" and r["missing"]
def test_checks_12_blocker_families_and_20_meta_cases():
    r=a.audit(); assert len(r["groups"]["blocker_families"])==12; assert len(r["groups"]["meta_crown"])==20
def test_requires_final_lock_governance_objects():
    r=a.audit(); required={"OCCInvariantRegistry","Final Lock Coverage Matrix","OCCResidualRiskRegister","OCCAssuranceDebtRegistry","FinalLockTransitionReceipt","OCC1FinalLockEvidenceBundle"}
    assert required==set(r["groups"]["evidence_objects"])
