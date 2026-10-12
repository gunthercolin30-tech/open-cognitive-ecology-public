from pathlib import Path
from ontology.autonomous_web_navigation_engine import AutonomousWebNavigationEngine

def test_database_direct_transport_removed_and_network_preserved():
 s=(Path(__file__).resolve().parents[1]/"ontology/autonomous_web_navigation_engine.py").read_text()
 assert "sqlite3.connect" not in s and "import sqlite3" not in s
 assert "P162_G64C2_DATABASE_MEDIATED = True" in s
 assert "P162_G63B3_NETWORK_MEDIATED = True" in s
 for x in ["GovernedNetworkEffector","GovernedNetworkRequest","_p162_network_context","_p162_require_playwright_target","_p162_direct_urlopen_removed"]: assert x in s

def test_database_fails_closed_without_context(monkeypatch,tmp_path):
 monkeypatch.setattr(Path,"home",lambda:tmp_path)
 e=AutonomousWebNavigationEngine()
 assert e.database_persistence_status=="GOVERNED_CONTEXT_REQUIRED"
 r=e._log_visit("https://example.invalid",3,True)
 assert r["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"

def test_backup_contains_historical_sqlite_and_network_marker():
 s=(Path(__file__).resolve().parents[1]/"ontology/autonomous_web_navigation_engine.py.bak.p162g64c2").read_text()
 assert s.count("sqlite3.connect")==2 and "P162_G63B3_NETWORK_MEDIATED = True" in s

def test_only_navigation_history_statements_exposed():
 s=(Path(__file__).resolve().parents[1]/"ontology/autonomous_web_navigation_engine.py").read_text()
 assert "navigation_history.create" in s and "navigation_history.insert" in s
 assert "DELETE" not in s and "VACUUM" not in s
