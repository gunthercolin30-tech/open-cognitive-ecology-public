import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"validation_artifacts/p162/p162g/g65c10d/remaining_direct_process_classification.json"
def d(): return json.loads(P.read_text())
def test_complete_accounting():
 r=d(); assert r["classified_count"]==r["source_direct_count"]==len(r["sites"])
def test_modules_accounted():
 r=d(); assert r["module_count"]==len(set(x["file"] for x in r["sites"]))
def test_families_accounted():
 r=d(); assert sum(r["family_counts"].values())==r["classified_count"]
def test_context_present():
 assert all(x["context"] and x["effect_class"] for x in d()["sites"])
def test_classification_only():
 r=d(); assert r["migration_performed"] is False and r["process_bypass_zero_claimed"] is False
 assert r["process_migration_complete"] is False and r["p162g_closure_claimed"] is False
