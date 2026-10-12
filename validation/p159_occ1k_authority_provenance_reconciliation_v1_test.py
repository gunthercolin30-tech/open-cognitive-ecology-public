from validation import p159_occ1k_authority_provenance_reconciliation_v1 as a
def test_exact_two_hashes_are_bound():
    r=a.build(); assert r["authority_source"]["historical_manifest_sha256"]==a.OLD
    assert r["authority_source"]["current_sha256"]==a.CURRENT
def test_occ1i_prior_drift_is_evidence():
    assert a.build()["authority_source"]["drift_already_observed_in_occ1i"]
def test_no_hash_only_historical_reconstruction():
    s=a.build()["scientific_classification"]
    assert not s["historical_source_can_be_reconstructed_from_hash_alone"]
def test_no_automatic_normalization_or_rebinding():
    s=a.build()["scientific_classification"]
    assert not s["manifest_silent_rewrite_permitted"]
    assert not s["automatic_hash_normalization_permitted"]
    assert not s["current_source_can_be_declared_canonical_without_governance"]
def test_default_is_keep_unresolved():
    r=a.build(); assert r["current_decision"]=="KEEP_UNRESOLVED"
    assert r["scientific_classification"]["provenance_debt"]=="OPEN"
def test_boundaries_remain_closed():
    b=a.build()["boundaries"]
    assert not b["canonical_occ1a_modified"] and not b["manifest_modified"]
    assert not b["authority_registry_modified"] and not b["runtime_binding_created"]
    assert not b["p160b_opened"] and b["fl_b3"]=="BLOCKED"
def test_human_governed_decision_is_next():
    r=a.build(); assert r["status"]=="HUMAN_GOVERNED_REBINDING_DECISION_REQUIRED"
    assert r["next_required_step"]=="R9C_HUMAN_GOVERNED_AUTHORITY_REBINDING_DECISION"
def test_deterministic():
    assert a.build()["semantic_hash"]==a.build()["semantic_hash"]
