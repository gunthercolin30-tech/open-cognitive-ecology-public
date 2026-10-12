from ontology.occ1h_a040_rrp13_rrp16_evidence import current_evidence

def test_a040_rrp13_rrp16_terminal_disposition():
    e=current_evidence()
    assert e['rrp13_status']=='RESOLUTION_SPACE_CANDIDATE_FOUND'
    assert e['rrp14_status']=='CANDIDATE_REJECTED_SEMANTIC_DOMAIN_MISMATCH'
    assert e['rrp15_status']=='SKIPPED_NO_ADMISSIBLE_CANDIDATE'
    assert e['rrp15_experiment_authorized'] is False
    assert e['rrp15_experiment_performed'] is False
    assert e['rrp16_requalification_performed'] is True
    assert e['rrp16_status']=='BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE'
    assert e['rrp16_occ1h_closure_eligible_for_a040'] is False

def test_a040_rrp13_rrp16_fail_closed():
    e=current_evidence()
    assert e['rrp16_blocker_preserved'] is True
    assert e['historical_evidence_modified'] is False
    assert e['normative_source_modified'] is False
    assert e['root_criticality_modified'] is False
    assert e['functional_correction_installed'] is False
    assert e['authorization_created'] is False
    assert e['occ1h_closed'] is False
    assert e['p160_opened'] is False
