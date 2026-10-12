from pathlib import Path
from ontology.scoped_handle_broker import ScopedEffectHandle
from ontology.governed_database_effector import DatabaseEffectRequest,GovernedSqliteEffector
def handle(target,op="INSERT",adapter="DBA"):
    return ScopedEffectHandle("h","l","r","c",adapter,"GOVERNED_SQLITE",op,target,"s",adapter,"2999-01-01T00:00:00Z")
class Fake:
    def __init__(self,fail=False): self.calls=[]; self.fail=fail
    def __call__(self,**kw):
        self.calls.append(kw)
        if self.fail: raise RuntimeError("uncertain")
        return {"rowcount":1}
def eff(f):
    return GovernedSqliteEffector(transport=f,statement_registry={
      "causal.insert":{"operation":"INSERT","table":"causal_history","statement":"INSERT INTO causal_history VALUES (?)"},
      "nav.insert":{"operation":"INSERT","table":"navigation_history","statement":"INSERT INTO navigation_history VALUES (?)"},
      "memory.delete":{"operation":"DELETE","table":"memory","statement":"DELETE FROM memory WHERE id=?"}})
def req(path,table="causal_history",op="INSERT",sid="causal.insert",mc="WRITE"):
    return DatabaseEffectRequest(str(path),op,table,sid,("x",),mc)
def test_missing_handle_fails_closed(tmp_path):
    f=Fake(); o=eff(f).execute(request=req(tmp_path/"a.db"),handle=None,adapter_id="DBA")
    assert o["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK" and f.calls==[]
def test_exact_database_and_table_binding(tmp_path):
    f=Fake(); e=eff(f); r=req(tmp_path/"a.db")
    wrong=GovernedSqliteEffector.canonical_target(tmp_path/"b.db","causal_history")
    assert e.execute(request=r,handle=handle(wrong),adapter_id="DBA")["reason"]=="database_or_table_scope_mismatch"
    wrongtable=GovernedSqliteEffector.canonical_target(tmp_path/"a.db","navigation_history")
    assert e.execute(request=r,handle=handle(wrongtable),adapter_id="DBA")["reason"]=="database_or_table_scope_mismatch"
    assert f.calls==[]
def test_operation_and_statement_are_bound(tmp_path):
    f=Fake(); e=eff(f); target=e.canonical_target(tmp_path/"a.db","causal_history")
    assert e.execute(request=req(tmp_path/"a.db"),handle=handle(target,"DELETE"),adapter_id="DBA")["reason"]=="operation_scope_mismatch"
    r=req(tmp_path/"a.db",sid="memory.delete")
    assert e.execute(request=r,handle=handle(target),adapter_id="DBA")["reason"]=="statement_binding_mismatch"
    assert f.calls==[]
def test_mutation_class_cannot_be_laundered(tmp_path):
    f=Fake(); e=eff(f); target=e.canonical_target(tmp_path/"a.db","causal_history")
    o=e.execute(request=req(tmp_path/"a.db",mc="READ"),handle=handle(target),adapter_id="DBA")
    assert o["reason"]=="mutation_class_mismatch" and f.calls==[]
def test_exact_governed_write_reaches_injected_transport(tmp_path):
    f=Fake(); e=eff(f); target=e.canonical_target(tmp_path/"a.db","causal_history")
    o=e.execute(request=req(tmp_path/"a.db"),handle=handle(target),adapter_id="DBA")
    assert o["status"]=="EFFECT_CONFIRMED" and len(f.calls)==1
def test_unknown_transport_outcome_is_indeterminate(tmp_path):
    f=Fake(True); e=eff(f); target=e.canonical_target(tmp_path/"a.db","causal_history")
    o=e.execute(request=req(tmp_path/"a.db"),handle=handle(target),adapter_id="DBA")
    assert o["status"]=="EFFECT_STATE_INDETERMINATE" and o["retry_allowed"] is False
def test_no_arbitrary_sql_from_caller():
    fields=DatabaseEffectRequest.__dataclass_fields__
    assert "statement_id" in fields and "statement" not in fields and "sql" not in fields
def test_transport_is_only_sqlite_connect_owner_in_new_tcb():
    s=Path(__file__).resolve().parents[1].joinpath("ontology/governed_database_effector.py").read_text()
    assert s.count("sqlite3.connect")==1
    assert "eval(" not in s and "exec(" not in s
