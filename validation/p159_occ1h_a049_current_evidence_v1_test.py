import json
from pathlib import Path
from ontology import occ1h_a049_current_evidence as e
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"validation_artifacts"/"p159"/"occ1h"/"a049_current_evidence_v1.json"
def test_a049_current_evidence_contract():
    d=json.loads(ART.read_text(encoding="utf-8"))
    assert d["root_id"]=="A049" and d["scenario"]=="purpose laundering"
    assert d["current_verdict"]=="INCONCLUSIVE"
    assert d["classification"]=="PURPOSE_SCOPE_SEMANTICS_NOT_PROJECTED_IN_GOVERNED_COMPILATION_CHAIN"
    assert d["a042_is_distinct_root"] and d["a042_evidence_not_substituted_for_a049"]
    assert d["rrp4_resolution_contract_frozen"] and d["rrp5_impact_surface_mapped"] and d["rrp6_dry_run_all_products_valid"]
    assert d["functional_correction_installed"] is False and d["verdicts_modified"] is False
    assert d["occ1h_closed"] is False and d["p160_opened"] is False
def test_a049_module_matches_artifact():
    d=json.loads(ART.read_text(encoding="utf-8"))
    assert e.CURRENT_VERDICT==d["current_verdict"]
    assert e.CLASSIFICATION==d["classification"]
    assert e.PROBE_EVIDENCE_SHA256==d["probe_evidence_sha256"]
    assert e.REOPEN_TRIGGER==d["reopen_trigger"]
    assert e.A042_IS_DISTINCT_ROOT and e.A042_EVIDENCE_NOT_SUBSTITUTED_FOR_A049
    assert e.FUNCTIONAL_ONLY and e.PHENOMENOLOGY_UNDETERMINED
