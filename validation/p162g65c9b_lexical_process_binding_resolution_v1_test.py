import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c9b/lexical_process_binding_resolution.json"
def d(): return json.loads(R.read_text())
def test_full_accounting():
 r=d(); assert r["source_count"]==34
 assert r["source_count"]==r["governed_alias_count"]+r["standard_subprocess_count"]+r["unresolved_count"]
def test_no_unresolved():
 assert d()["unresolved_count"]==0
def test_local_governed_imports_resolved():
 r=d(); assert r["local_governed_alias_count"]>0
def test_no_premature_migration_or_closure():
 r=d(); assert r["migration_performed"] is False
 assert r["process_bypass_zero_claimed"] is False
 assert r["p162g_closure_claimed"] is False
