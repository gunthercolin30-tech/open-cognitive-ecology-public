from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

READ_OPS = frozenset({"SELECT"})
WRITE_OPS = frozenset({"INSERT","UPSERT","UPDATE","DELETE","CREATE_TABLE","PRAGMA","VACUUM"})
ALL_OPS = READ_OPS | WRITE_OPS

@dataclass(frozen=True)
class DatabaseEffectRequest:
    database_path: str
    operation: str
    table: str
    statement_id: str
    parameters: Tuple[Any, ...] = ()
    mutation_class: str = "WRITE"

class SqliteTrustedTransport:
    def __call__(self, *, request: DatabaseEffectRequest, statement: str):
        import sqlite3
        path=Path(request.database_path).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        conn=sqlite3.connect(str(path))
        try:
            cur=conn.cursor()
            cur.execute(statement, tuple(request.parameters))
            rows=cur.fetchall() if request.operation=="SELECT" else []
            if request.operation in WRITE_OPS:
                conn.commit()
            return {"rows": rows, "rowcount": cur.rowcount}
        finally:
            conn.close()

class GovernedSqliteEffector:
    EFFECTOR_ID="GOVERNED_SQLITE"
    def __init__(self, *, transport: Callable, statement_registry: Dict[str, Dict[str,str]]):
        if transport is None: raise ValueError("transport_required")
        self._transport=transport
        self._registry=dict(statement_registry or {})

    @staticmethod
    def canonical_target(database_path: str, table: str) -> str:
        p=str(Path(database_path).expanduser().resolve())
        return "sqlite://"+p+"#table="+str(table)

    def execute(self, *, request: DatabaseEffectRequest, handle, adapter_id: str):
        op=str(request.operation).upper()
        if op not in ALL_OPS:
            return self._blocked("operation_not_registered")
        expected_class="READ" if op in READ_OPS else "WRITE"
        if request.mutation_class != expected_class:
            return self._blocked("mutation_class_mismatch")
        spec=self._registry.get(request.statement_id)
        if not spec:
            return self._blocked("statement_id_not_registered")
        if spec.get("operation") != op or spec.get("table") != request.table:
            return self._blocked("statement_binding_mismatch")
        if handle is None:
            return self._blocked("missing_scoped_handle")
        target=self.canonical_target(request.database_path,request.table)
        if getattr(handle,"effector_id",None)!=self.EFFECTOR_ID:
            return self._blocked("effector_mismatch")
        if getattr(handle,"adapter_id",None)!=adapter_id:
            return self._blocked("adapter_mismatch")
        if getattr(handle,"operation_id",None)!=op:
            return self._blocked("operation_scope_mismatch")
        if getattr(handle,"target_binding",None)!=target:
            return self._blocked("database_or_table_scope_mismatch")
        if getattr(handle,"ambient_authority",True) is not False:
            return self._blocked("ambient_authority_forbidden")
        if getattr(handle,"transferable",True) is not False or getattr(handle,"child_inheritance",True) is not False:
            return self._blocked("handle_transfer_or_inheritance_forbidden")
        try:
            result=self._transport(request=request,statement=spec["statement"])
        except Exception as exc:
            return {"status":"EFFECT_STATE_INDETERMINATE","reason":"database_transport_exception",
                    "exception_type":type(exc).__name__,"retry_allowed":False}
        return {"status":"EFFECT_CONFIRMED","reason":None,"operation":op,"table":request.table,
                "target":target,"result":result}

    @staticmethod
    def _blocked(reason):
        return {"status":"EXECUTION_BLOCKED_AT_FINAL_RECHECK","reason":reason}
