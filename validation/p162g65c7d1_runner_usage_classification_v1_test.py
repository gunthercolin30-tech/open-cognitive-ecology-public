import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def report(): return json.loads((ROOT/"validation_artifacts/p162/p162g/g65c7d1/runner_usage_classification.json").read_text())
def test_single_production_owner():
 r=report(); assert r["production_consumer_count"]==1
 assert r["production_consumers"][0]["file"]=="ontology/acee_installation_executor.py"
 assert r["production_instantiation_count"]==2
def test_harness_not_authority():
 r=report(); assert r["observations"]["test_harness_must_not_create_production_rights"] is True
 assert r["migration_performed"] is False
def test_no_premature_closure():
 r=report(); assert r["process_bypass_zero_claimed"] is False
 assert r["p162g_closure_claimed"] is False
