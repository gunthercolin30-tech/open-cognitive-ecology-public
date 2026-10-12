from validation import p159_occ1k_evidence_foundation_v1 as f

def test_all_canonical_invariant_families_registered_exactly():
    x=f.build_foundation()
    expected=sum(f.FAMILY_COUNTS.values())
    assert len(x["invariant_registry"])==expected
    assert len({r["invariant_id"] for r in x["invariant_registry"]})==expected

def test_coverage_is_non_certifying_and_explicit():
    x=f.build_foundation()
    assert len(x["coverage_matrix"])==len(x["invariant_registry"])
    assert all(r["semantic_coverage"]=="TO_BE_QUALIFIED" for r in x["coverage_matrix"])
    assert all(r["lock_credit"]=="NOT_YET_GRANTED" for r in x["coverage_matrix"])

def test_exhaustive_final_lock_gap_remains_open():
    x=f.build_foundation()
    rr={r["risk_id"]:r for r in x["residual_risk_register"]}
    ad={r["debt_id"]:r for r in x["assurance_debt_registry"]}
    assert rr["RR-FLI-EXHAUSTIVE-CERTIFICATION"]["status"]=="OPEN"
    assert ad["AD-FLI-EXHAUSTIVE-CERTIFICATION"]["blocks_lock"] is True

def test_historical_lock_and_runtime_boundaries_preserved():
    x=f.build_foundation()
    assert x["historical_lock_preserved"] is True
    assert x["lock_granted"] is False
    assert x["p160b_opened"] is False
    assert x["authorization_created"] is False
    assert x["execution_performed"] is False

def test_deterministic_foundation():
    assert f.build_foundation()["semantic_hash"]==f.build_foundation()["semantic_hash"]

def test_artifact_write_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(f,"OUT",tmp_path)
    x,m=f.write_artifacts()
    assert x["status"]=="EVIDENCE_FOUNDATION_READY"
    assert len(m)==5
    assert (tmp_path/"occ1k_r1_sha256_manifest_v1.json").is_file()
