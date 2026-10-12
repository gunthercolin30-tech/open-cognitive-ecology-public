from pathlib import Path
import json, shutil
from ontology import occ1h_historical_counterexample_evidence as m
ROOT=Path(__file__).resolve().parents[1]

def test_two_historical_counterexamples_bound():
    r=m.build(ROOT)
    assert r["verified"] is True
    by={x["attack_id"]:x for x in r["records"]}
    assert set(by)=={"A008","A009"}
    assert by["A008"]["historical_verdict"]=="VIOLATED"
    assert by["A008"]["current_verdict"]=="DETECTED"
    assert by["A009"]["historical_verdict"]=="VIOLATED"
    assert by["A009"]["current_verdict"]=="DETECTED"
    assert by["A008"]["classification"]=="FORMALIZATION_GAP"
    assert by["A009"]["classification"]=="SCHEMA_BUG"

def test_materialized_records_are_content_addressed():
    assert m.verify_materialized(ROOT) is True

def test_no_history_rewrite_or_authority():
    r=m.build(ROOT)
    assert r["historical_evidence_rewritten"] is False
    assert r["normative_auto_rewrite"] is False
    assert r["authorization_created"] is False
    assert r["execution_performed"] is False
    assert r["occ1h_closed"] is False and r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False and r["p160_opened"] is False

def test_historical_tamper_fails_closed(tmp_path):
    dst=tmp_path/"repo"
    src=ROOT/"validation_artifacts/p159/occ1h"
    shutil.copytree(src,dst/"validation_artifacts/p159/occ1h")
    p=dst/"validation_artifacts/p159/occ1h/h1_h3_execution_bundle_v1.json"
    d=json.loads(p.read_text()); 
    for row in d["rows"]:
        if row["attack_id"]=="A008": row["verdict"]="DETECTED"
    p.write_text(json.dumps(d))
    r=m.build(dst)
    assert r["verified"] is False
    assert "A008:HISTORICAL_VERDICT_DRIFT" in r["errors"]

def test_posthardening_tamper_fails_closed(tmp_path):
    dst=tmp_path/"repo"
    src=ROOT/"validation_artifacts/p159/occ1h"
    shutil.copytree(src,dst/"validation_artifacts/p159/occ1h")
    p=dst/"validation_artifacts/p159/occ1h/h1_h3_posthardening_evidence_v1.json"
    d=json.loads(p.read_text()); d["a009_verdict"]="RESISTED"
    p.write_text(json.dumps(d))
    r=m.build(dst)
    assert r["verified"] is False
    assert "A009:CURRENT_VERDICT_DRIFT" in r["errors"]
