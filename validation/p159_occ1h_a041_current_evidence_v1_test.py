from ontology.occ1h_a041_current_evidence import qualification

def test_a041_deferred_evidence_contract():
    e=qualification()
    assert e["root_id"]=="A041" and e["current_verdict"]=="INCONCLUSIVE"
    assert e["rrp3_reproduction_count"]==2
    assert e["rrp4_resolution_contract_frozen"] is True
    assert e["rrp5_impact_surface_mapped"] is True
    assert e["rrp6_dry_run_all_products_valid"] is True
    assert e["functional_correction_installed"] is False
    assert e["positive_resistance_proof_present"] is False
    assert e["occ1h_closed"] is False and e["p160_opened"] is False

def test_a041_reopen_trigger_is_specific():
    e=qualification(); t=e["reopen_trigger"]
    assert "CANONICAL_SOURCE_BACKED_SUNSET_SEMANTICS" in t
    assert "GOVERNED_FUNCTIONAL_SOURCE_TO_NIR_PATH" in t
    assert e["rrp4_resolution_contract"]["synthetic_tolerance_alone_sufficient"] is False
    assert e["rrp4_resolution_contract"]["nir_carrier_alone_sufficient"] is False
