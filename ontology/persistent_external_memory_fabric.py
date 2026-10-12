"""PERSISTENT_EXTERNAL_MEMORY_FABRIC — P162-G6.4c3 governed SQLite."""
from __future__ import annotations
import json
import time
from pathlib import Path
from ontology.governed_database_effector import DatabaseEffectRequest
P162_G64C3_DATABASE_MEDIATED = True

class PersistentExternalMemoryFabric:
    MIN_EFFECTIVE_QUOTA_BYTES=100_000
    def __init__(self,db_path=None,quota_bytes=500_000_000,governed_database_context=None):
        root=Path.home()/"open-cognitive-ecology"
        try:
            from ontology.civilizational_storage_router import CivilizationalStorageRouter
            router=CivilizationalStorageRouter(root=root); memory_dir=router.route_directory("external_memory",category="memory")
            self.storage_router=router; self.storage_mode="ssd" if router.ssd_available() else "local_fallback"
        except Exception:
            memory_dir=root/"external_memory"; memory_dir.mkdir(parents=True,exist_ok=True)
            self.storage_router=None; self.storage_mode="legacy_local"
        self.db_path=Path(db_path) if db_path else memory_dir/"memory.db"
        self.quota_bytes=max(int(quota_bytes),self.MIN_EFFECTIVE_QUOTA_BYTES)
        self._governed_database_context=governed_database_context
        self.database_persistence_status="GOVERNED_CONTEXT_REQUIRED"
        if governed_database_context is not None: self._initialize_db()

    def _db(self,operation,statement_id,parameters=(),mutation_class="WRITE"):
        ctx=self._governed_database_context
        if ctx is None:
            self.database_persistence_status="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
            return {"status":self.database_persistence_status,"reason":"governed_database_context_required"}
        effector=ctx["effector"]; adapter_id=ctx["adapter_id"]
        target=effector.canonical_target(self.db_path,"memory")
        handle=ctx["handle_factory"](target=target,operation=operation,adapter_id=adapter_id)
        req=DatabaseEffectRequest(str(self.db_path),operation,"memory",statement_id,tuple(parameters),mutation_class)
        out=effector.execute(request=req,handle=handle,adapter_id=adapter_id)
        self.database_persistence_status=out["status"]; return out

    def _initialize_db(self):
        new=not self.db_path.exists()
        self._db("PRAGMA","memory.pragma_wal")
        if new:
            self._db("PRAGMA","memory.pragma_auto_vacuum"); self._db("VACUUM","memory.vacuum")
        self._db("CREATE_TABLE","memory.create")

    def _rows(self,sid,parameters=()):
        out=self._db("SELECT",sid,parameters,"READ")
        return out.get("result",{}).get("rows",[]) if out.get("status")=="EFFECT_CONFIRMED" else []

    def _db_size(self):
        return sum(p.stat().st_size for p in [Path(str(self.db_path)+s) for s in ("","-wal","-shm")] if p.exists())
    def _entry_count(self):
        r=self._rows("memory.count"); return int(r[0][0]) if r else 0
    def _incremental_vacuum(self):
        self._db("PRAGMA","memory.incremental_vacuum")
    def _enforce_quota(self):
        while self._db_size()>self.quota_bytes and self._entry_count()>1:
            r=self._rows("memory.oldest_key")
            if not r: break
            self._db("DELETE","memory.delete",(r[0][0],)); self._incremental_vacuum()
    def store(self,key,value):
        self._db("UPSERT","memory.upsert",(key,json.dumps(value,ensure_ascii=False),time.time())); self._enforce_quota()
    def recall(self,key,default=None):
        r=self._rows("memory.recall",(key,)); return default if not r else json.loads(r[0][0])
    def delete(self,key):
        self._db("DELETE","memory.delete",(key,)); self._incremental_vacuum()
    def list_keys(self):
        return [r[0] for r in self._rows("memory.list_keys")]
    def close(self):
        return None
