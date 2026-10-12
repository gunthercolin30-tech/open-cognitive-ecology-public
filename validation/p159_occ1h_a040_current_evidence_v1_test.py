from ontology import occ1h_a040_current_evidence as m

def test_a040_deferred_contract():
    e=m.current_evidence()
    assert m.CURRENT_VERDICT=='INCONCLUSIVE'
    assert e['classification']=='NORMATIVE_EXPIRY_SEMANTICS_GAP_REPRODUCED'
    assert e['principle_present'] is True
    assert e['source_backed_temporal_parameter_absent'] is True
    assert e['executable_expiry_removal_fixture_without_normative_invention'] is False
    assert e['normative_invention_permitted'] is False
    assert e['compiler_repair_authorized'] is False
    assert e['normative_source_rewrite_authorized'] is False
    assert e['positive_resistance_proof_present'] is False
    assert e['rrp']['rrp3_fresh_runs']==2
    assert e['rrp']['rrp4_resolution_contract_frozen'] is True
    assert e['rrp']['rrp5_impact_surface_mapped'] is True
    assert 'REOPEN_A040_WHEN' in m.REOPEN_TRIGGER

def test_a040_no_stage_or_verdict_transition():
    assert m.HISTORICAL_EVIDENCE_REWRITTEN is False
    assert m.VERDICTS_MODIFIED is False
    assert m.OCC1H_CLOSED is False
    assert m.OCC1I_OPENED is False
    assert m.P159_FINAL_LOCK is False
    assert m.P160_OPENED is False
    assert m.FUNCTIONAL_ONLY is True
    assert m.PHENOMENOLOGY_UNDETERMINED is True
