from pathlib import Path
from ontology.advanced_causal_reasoning_engine import AdvancedCausalReasoningEngine

def test_source_mediated():
    s=(Path(__file__).resolve().parents[1]/"ontology/advanced_causal_reasoning_engine.py").read_text()
    assert "sqlite3.connect" not in s and "import sqlite3" not in s
    assert "P162_G64C1_DATABASE_MEDIATED = True" in s

def test_fail_closed_without_context(monkeypatch,tmp_path):
    monkeypatch.setattr(Path,"home",lambda:tmp_path)
    e=AdvancedCausalReasoningEngine(); e.add_causal_relation("rain","wet",0.8)
    assert e.database_persistence_status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
    assert e.predict_consequences("rain")==["wet"]

def test_backup_pristine():
    s=(Path(__file__).resolve().parents[1]/"ontology/advanced_causal_reasoning_engine.py.bak.p162g64c1").read_text()
    assert s.count("sqlite3.connect")==2 and "import sqlite3" in s
