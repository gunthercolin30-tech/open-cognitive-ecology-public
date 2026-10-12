from ontology.occ1h_g1_source_to_nir_semantic_resolution import qualification

def test_g1_exact_scope_and_no_invention():
    q=qualification()
    assert set(q["scope"])=={"A021","A040","A041","A042"}
    assert q["invented_norms"]==0 and q["verdicts_modified"] is False
    assert q["canonical_sources_modified"] is False

def test_a040_source_bounded():
    r=qualification()["records"]["A040"]
    assert r["source_id"]=="CCAD.P7" and r["source_text"]=="Exception Expiry"
    assert r["classification"]=="SOURCE_PRESENT_OPERATIONALLY_UNDERSPECIFIED"
    assert r["invent_duration_or_clock"] is False

def test_absent_semantics_not_invented():
    r=qualification()["records"]
    assert r["A021"]["source_explicit_may"] is False
    assert r["A041"]["source_explicit_sunset"] is False
    assert r["A042"]["source_explicit_purpose"] is False
    assert all(r[x]["invent_semantics"] is False for x in ("A021","A041","A042"))

def test_boundaries_closed():
    q=qualification()
    for k in ("authority_created","authorization_created","execution_created","occ1h_closed",
              "occ1i_opened","p159_final_lock","p160_opened"):
        assert q[k] is False
    assert q["functional_conclusion_only"] is True
    assert q["phenomenology_undetermined"] is True
