import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c2a/git_dynamic_argument_closure_audit.json"
def d(): return json.loads(R.read_text())
def test_audit_has_no_authority_claim(): assert d()["authorization_created"] is False
def test_unresolved_never_becomes_allowed():
 x=d()
 for r in x["helpers"]:
  if r["status"]=="UNRESOLVED": assert r["allowlist_emitted"] is False
def test_closed_requires_literal_callsites():
 for r in d()["helpers"]:
  if r["status"]=="CLOSED_ENUMERABLE":
   assert r["call_sites"] and all(c["literal"] for c in r["call_sites"])
def test_no_migration_or_closure_claim():
 x=d(); assert x["modules_modified"]==0 and x["process_bypass_zero_claimed"] is False and x["p162g_closure_not_claimed"] is True
