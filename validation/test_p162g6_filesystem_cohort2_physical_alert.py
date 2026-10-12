import ast
from pathlib import Path
import pytest
import ontology.physical_environment_alert_router as m
def test_no_persist_needs_no_authority():
 r=m.PhysicalEnvironmentAlertRouter().step({},persist=False); assert r["persisted"] is False
def test_persist_fails_closed():
 with pytest.raises(RuntimeError,match="governed_filesystem_context_required"):
  m.PhysicalEnvironmentAlertRouter().step({},persist=True)
def test_persistence_surface_has_no_direct_fs_bypass():
 t=ast.parse(Path(m.__file__).read_text()); banned={"write_text","write_bytes","open","mkdir","replace","rename","unlink"}; hits=[]
 for n in ast.walk(t):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in banned:
   for f in ast.walk(t):
    if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name in {"_persist","_write_json","_append_jsonl"} and f.lineno<=n.lineno<=f.end_lineno: hits.append((f.name,n.func.attr))
 assert hits==[]
