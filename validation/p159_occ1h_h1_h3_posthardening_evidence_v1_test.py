from validation.p159_occ1h_adversarial_crown_h1_h3_v1_test import governed_crown_run
from pathlib import Path
import json
from ontology import occ_constitutional_adversarial_crown_h1_h3 as crown

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "normative/occ1a"
ART = ROOT / "validation_artifacts/p159/occ1h/h1_h3_posthardening_evidence_v1.json"

def test_posthardening_live_verdicts():
    r = governed_crown_run(SRC)
    rows = {x["attack_id"]: x for x in r["rows"]}
    assert rows["A008"]["verdict"] == "DETECTED"
    assert rows["A009"]["verdict"] == "DETECTED"
    assert r["verdict_counts"]["VIOLATED"] == 0
    assert rows["A021"]["verdict"] == "INCONCLUSIVE"

def test_a021_epistemic_boundary_preserved():
    r = governed_crown_run(SRC)
    row = {x["attack_id"]: x for x in r["rows"]}["A021"]
    assert row["observed_reason"] == "NO_MAY_STRENGTH_FIELD_IN_CURRENT_OCC1A_PARTITIONS"
    assert row["verdict"] == "INCONCLUSIVE"

def test_no_premature_closure():
    r = governed_crown_run(SRC)
    assert r["occ1h_closed"] is False
    assert r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False
    assert r["p160_opened"] is False

def test_materialized_evidence_matches_live_run():
    e = json.loads(ART.read_text(encoding="utf-8"))
    assert e["schema"] == "oce.p159.occ1h.h1_h3.posthardening_evidence.v1"
    assert e["violated_count"] == 0
    assert e["a008_verdict"] == "DETECTED"
    assert e["a009_verdict"] == "DETECTED"
    assert e["a021_verdict"] == "INCONCLUSIVE"
    assert e["a021_qualification"] == "CURRENTLY_UNINSTANTIABLE_FROM_CANONICAL_OCC1A_SOURCE_REPRESENTATION"
    assert e["occ1h_closed"] is False
