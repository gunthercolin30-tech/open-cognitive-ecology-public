from validation import p159_occ1k_governed_semantic_binding_candidates_v1 as a
def test_semantic_source_hashes_match_manifest():
    assert all(a.build()["semantic_source_integrity"].values())
def test_authority_drift_is_preserved_not_normalized():
    r=a.build(); d=r["authority_dependency_integrity"]
    assert d["HUMAN_RESERVED_AUTHORITY"] is False
    assert d["state"]=="PROVENANCE_DEBT_BLOCKS_AUTHORITY_PREFLIGHT"
    assert r["governance"]["authority_preflight_allowed"] is False
def test_all_candidate_anchors_exist():
    assert all(a.build()["candidate_anchor_checks"].values())
def test_candidates_are_non_adopting():
    r=a.build()
    assert all(c["adoption_status"]=="CANDIDATE_ONLY" for rows in r["candidates"].values() for c in rows)
def test_existing_governance_path_is_reused_without_bypass():
    r=a.build(); assert r["governance"]["existing_occ1a_binding_and_adoption_path_reused"]
    assert r["governance"]["human_or_governed_adoption_not_bypassed"]
def test_no_canonical_or_runtime_mutation():
    g=a.build()["governance"]
    assert not g["canonical_partitions_modified"] and not g["historical_evidence_modified"]
    assert not g["runtime_binding_created"] and not g["p160b_opened"]
def test_flb3_stays_blocked_and_provenance_reconciliation_is_next():
    c=a.build()["conclusion"]
    assert c["fl_b3"]=="BLOCKED" and not c["lock_ready"] and not c["lock_granted"]
    assert c["next_required_step"]=="R9B_AUTHORITY_PROVENANCE_RECONCILIATION"
def test_deterministic():
    assert a.build()["semantic_hash"]==a.build()["semantic_hash"]
