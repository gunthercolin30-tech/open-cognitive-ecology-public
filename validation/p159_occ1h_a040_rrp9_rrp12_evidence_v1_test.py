from ontology.occ1h_a040_rrp9_rrp12_evidence import current_evidence

def test_a040_rrp9_rrp12_disposition():
    e=current_evidence()
    assert e['rrp9_root_materiality_resolved'] is True
    assert e['rrp9_materiality_disposition']=='ROOT_UNDETERMINED'
    assert e['rrp9_existing_root_declaration_causally_sufficient'] is False
    assert e['rrp10_inconclusive_elimination_exhausted'] is True
    assert e['rrp11_occ1h_closure_eligible_for_a040'] is False
    assert e['rrp12_final_disposition_recorded'] is True
    assert e['rrp12_status']=='ROOT_UNDETERMINED_BLOCKING'

def test_a040_rrp9_rrp12_fail_closed_nonmutation():
    e=current_evidence()
    assert e['historical_evidence_modified'] is False
    assert e['root_criticality_table_modified'] is False
    assert e['normative_source_modified'] is False
    assert e['functional_correction_installed'] is False
    assert e['authorization_created'] is False
    assert e['execution_performed'] is False
    assert e['occ1h_closed'] is False
    assert e['p160_opened'] is False
