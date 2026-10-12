from ontology import occ1h_a021_current_evidence as m

def test_a021_current_evidence_contract():
    e=m.current_evidence()
    assert m.ROOT_ID == 'A021'
    assert m.CURRENT_VERDICT == 'INCONCLUSIVE'
    assert e['source_semantically_admissible'] is True
    assert e['source_object_preserved'] is True
    assert e['source_provenance_preserved'] is True
    assert e['may_modality_projected'] is False
    assert e['permits_materialized'] is False
    assert e['semantic_relations_compiled'] is False
    assert e['builder_repair_authorized'] is False
    assert e['semantic_extension_authorized'] is False
    assert e['positive_non_instantiability_proof_present'] is False
    assert e['positive_resistance_proof_present'] is False
    assert 'REOPEN_A021_WHEN' in m.REOPEN_TRIGGER

def test_a021_no_authority_or_stage_transition():
    assert m.HISTORICAL_EVIDENCE_REWRITTEN is False
    assert m.AUTHORIZATION_CREATED is False
    assert m.ACTIVATION_PERFORMED is False
    assert m.EXECUTION_PERFORMED is False
    assert m.OCC1H_CLOSED is False
    assert m.OCC1I_OPENED is False
    assert m.P159_FINAL_LOCK is False
    assert m.P160_OPENED is False
    assert m.FUNCTIONAL_ONLY is True
    assert m.PHENOMENOLOGY_UNDETERMINED is True
