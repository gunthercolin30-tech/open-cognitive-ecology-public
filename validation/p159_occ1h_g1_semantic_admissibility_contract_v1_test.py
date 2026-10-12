from pathlib import Path
from ontology import occ1h_g1_semantic_admissibility_contract as q
ROOT=Path(__file__).resolve().parents[1]

def test_semantic_qualification():
    r=q.qualify(ROOT); x=r["records"]
    assert r["decision"]=="G1_SEMANTIC_ADMISSIBILITY_QUALIFIED_FAIL_CLOSED"
    assert x["A021"]["qualification"]=="SEMANTICALLY_ADMISSIBLE_NOT_INSTANTIATED"
    assert x["A041"]["qualification"]=="SYNTACTICALLY_TOLERATED_ONLY"
    assert x["A042"]["qualification"]=="SYNTACTICALLY_TOLERATED_ONLY"

def test_no_false_admissibility_from_parser_or_nir_carrier():
    r=q.qualify(ROOT)
    assert r["parser_acceptance_is_semantic_admissibility"] is False
    assert r["nir_carrier_is_source_admissibility"] is False

def test_current_sources_do_not_instantiate_targets():
    x=q.qualify(ROOT)["records"]
    assert all(x[a]["current_partition_explicit_instance"] is False for a in ("A021","A041","A042"))

def test_degradation_fail_closed_and_a040_preserved():
    r=q.qualify(ROOT)
    assert r["a040_classification"]=="NORMATIVE_GAP"
    assert r["a040_technical_repair_forbidden"] is True
    assert r["root_inconclusive_resolved"]==0
    assert r["applicability_reclassified"] is False

def test_non_regression_boundaries():
    r=q.qualify(ROOT)
    assert r["canonical_sources_modified"] is False
    assert r["builder_modified"] is False
    assert r["historical_verdicts_modified"] is False
    assert r["occ1h_closed"] is False
    assert r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False
    assert r["p160_opened"] is False
