from ontology.occ1h_a101_post_a075_current_evidence import current_evidence
def test_a101_post_a075_current_evidence_contract():
    e=current_evidence()
    assert e["root_id"]=="A101"
    assert e["historical_verdict"]=="INCONCLUSIVE"
    assert e["a075_current_verdict"]=="RESISTED"
    assert e["current_verdict"]=="INCONCLUSIVE"
    assert e["reachability_classification"]=="PATH_NOT_MATERIALIZED"
    assert e["confirmed_executable_a101_edges"]==0
    assert e["root_inconclusive_count_before"]==22
    assert e["root_inconclusive_count_after"]==22
    assert e["a101_promoted"] is False
    assert e["a105_promoted"] is False
    assert e["functional_only"] is True
    assert e["phenomenology_undetermined"] is True
