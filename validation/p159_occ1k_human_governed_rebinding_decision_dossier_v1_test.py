from validation import p159_occ1k_human_governed_rebinding_decision_dossier_v1 as a
def test_current_source_semantics_are_extracted_not_invented():
    r=a.build(); o=r["semantic_observations"]
    assert o["functional_only"] and o["real_execution_disabled"] and o["root_override_all_disabled"]
def test_initial_authority_semantics_are_explicit():
    o=a.build()["semantic_observations"]
    assert o["initial_development_authority_enabled"]
    assert o["authority_regime"]=="INITIAL_DEVELOPMENT"
    assert o["authority_role"]=="CONSTITUTIONAL_AUTHORITY"
def test_historical_semantic_equivalence_is_not_claimed():
    e=a.build()["epistemic_limit"]
    assert not e["historical_bytes_available"] and not e["historical_semantic_diff_possible"]
    assert not e["claim_current_semantics_equal_historical"]
def test_rebind_is_superseding_not_retroactive_repair():
    x=a.build()["decision_options"]["REBIND_CURRENT"]
    assert x["requires_explicit_human_confirmation"]
    assert "historical irregularity erased" in x["does_not_mean"]
def test_default_is_keep_unresolved():
    assert a.build()["default_without_confirmation"]=="KEEP_UNRESOLVED"
def test_no_authority_or_runtime_side_effect():
    b=a.build()["boundaries"]
    assert not b["canonical_occ1a_modified"] and not b["manifest_modified"]
    assert not b["authority_registry_modified"] and not b["runtime_binding_created"]
    assert not b["p160b_opened"] and b["fl_b3"]=="BLOCKED"
def test_deterministic():
    assert a.build()["semantic_hash"]==a.build()["semantic_hash"]
