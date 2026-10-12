import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c9a/process_symbol_binding_audit.json"
def d(): return json.loads(R.read_text())
def test_accounting():
 r=d(); assert r["source_count"]==34
 assert r["source_count"]==r["governed_alias_count"]+r["standard_subprocess_count"]+r["other_or_unresolved_binding_count"]
def test_governed_git_alias_is_recognized():
 r=d(); assert r["governed_alias_count"]>0
 assert all(x["binding"]=="GOVERNED_GIT_SUBPROCESS_ALIAS" for x in r["governed_alias_calls"])
def test_no_migration():
 r=d(); assert r["migration_performed"] is False
 assert r["process_bypass_zero_claimed"] is False
 assert r["p162g_closure_claimed"] is False
