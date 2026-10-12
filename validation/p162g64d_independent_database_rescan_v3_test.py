import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g64d_v3/independent_database_rescan.json"
def d(): return json.loads(R.read_text())
def test_database_zero_verified():
 x=d(); assert x["status"]=="DATABASE_ZERO_VERIFIED"
 assert x["direct_database_bypass_remaining"]==0 and x["review_required"]==0
 assert x["database_bypass_zero_verified"] is True and x["database_migration_complete"] is True
def test_archives_excluded():
 x=d(); assert x["archive_parse_errors_excluded"]>=6
 assert ".oif_backups" in x["excluded_archive_roots"] and "replication_packages" in x["excluded_archive_roots"]
def test_active_parse_errors_are_database_qualified():
 x=d()
 for e in x["active_parse_errors"]:
  assert "database_lexical_indicators" in e
 assert x["database_relevant_parse_errors"]==[]
def test_migrations_and_tcb():
 x=d(); assert x["known_migrated_modules_direct_database"]==0
 assert x["database_tcb_confined"] is True
 assert x["unauthorized_findings"]==[]
def test_historical_evidence_preserved():
 x=d(); assert x["historical_g64a_preserved"] is True
 assert x["p162g_closure_not_claimed"] is True and x["p162h_opened"] is False
