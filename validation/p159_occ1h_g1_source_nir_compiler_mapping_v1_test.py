from pathlib import Path
from ontology import occ1h_g1_source_nir_compiler_mapping as m

ROOT = Path(__file__).resolve().parents[1]

def test_mapping_functional():
    out = m.run(ROOT)
    assert out["decision"] == "G1_SOURCE_TO_NIR_PROJECTION_GAP_CONFIRMED"
    assert set(out["mapping"]) == {"A021", "A041", "A042"}
    assert all(v["classification"] == "SOURCE_TO_NIR_PROJECTION_GAP" for v in out["mapping"].values())

def test_real_builder_does_not_project_target_dimensions():
    out = m.run(ROOT)
    assert all(v["real_builder_projects_dimension"] is False for v in out["mapping"].values())

def test_existing_nir_has_relevant_carriers():
    out = m.run(ROOT)
    assert out["mapping"]["A021"]["nir_explicit_carrier"] is True
    assert out["mapping"]["A041"]["nir_explicit_carrier"] is True
    assert out["mapping"]["A042"]["nir_explicit_carrier"] is True

def test_degradation_no_root_resolution_or_semantic_invention():
    out = m.run(ROOT)
    assert out["builder_change_authorized"] is False
    assert out["normative_semantics_invented"] is False
    assert out["root_inconclusive_resolved"] == 0
    assert out["a040_technical_repair_forbidden"] is True

def test_non_regression_downstream_remains_closed():
    out = m.run(ROOT)
    assert out["occ1h_closed"] is False
    assert out["occ1i_opened"] is False
    assert out["p159_final_lock"] is False
    assert out["p160_opened"] is False
