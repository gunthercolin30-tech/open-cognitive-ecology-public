import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c8/process_residual_semantic_classification.json"
def data(): return json.loads(R.read_text())
def test_source_accounting():
 r=data(); assert r["source_residual_count"]==r["classified_count"]
 assert sum(r["family_counts"].values())==r["classified_count"]
def test_no_migration_or_zero_claim():
 r=data(); assert r["migration_performed"] is False
 assert r["process_bypass_zero_claimed"] is False
 assert r["p162g_closure_claimed"] is False
def test_runner_is_explicit_family():
 r=data(); assert any(x["family"]=="ACEE_RUNNER_BACKEND" and x["file"]=="ontology/acee_validation_runner.py" for x in r["classified_residuals"])
def test_unknowns_are_not_silently_closed():
 r=data(); assert "REVIEW_REQUIRED" in r["family_counts"]
