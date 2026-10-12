from pathlib import Path
from ontology.persistent_external_memory_fabric import PersistentExternalMemoryFabric
def test_no_ambient_sqlite_connection():
 s=(Path(__file__).resolve().parents[1]/"ontology/persistent_external_memory_fabric.py").read_text()
 assert "sqlite3.connect" not in s and "import sqlite3" not in s and "self.conn" not in s
 assert "P162_G64C3_DATABASE_MEDIATED = True" in s
def test_fail_closed_without_context(monkeypatch,tmp_path):
 monkeypatch.setattr(Path,"home",lambda:tmp_path)
 m=PersistentExternalMemoryFabric(db_path=str(tmp_path/"m.db")); m.store("k",{"v":1})
 assert m.database_persistence_status=="EXECUTION_BLOCKED_AT_FINAL_RECHECK" and not (tmp_path/"m.db").exists()
def test_scoped_semantics_present():
 s=(Path(__file__).resolve().parents[1]/"ontology/persistent_external_memory_fabric.py").read_text()
 for x in ["memory.pragma_wal","memory.pragma_auto_vacuum","memory.vacuum","memory.create","memory.count","memory.incremental_vacuum","memory.oldest_key","memory.delete","memory.upsert","memory.recall","memory.list_keys"]: assert x in s
 for x in ['"SELECT"','"UPSERT"','"DELETE"','"CREATE_TABLE"','"PRAGMA"','"VACUUM"']: assert x in s
def test_backup_historical():
 s=(Path(__file__).resolve().parents[1]/"ontology/persistent_external_memory_fabric.py.bak.p162g64c3").read_text()
 assert s.count("sqlite3.connect")==1 and "self.conn" in s
