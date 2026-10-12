import ast
from pathlib import Path
import pytest
import ontology.post_succession_verification as m
def test_constructor_is_pure(tmp_path):
    d=tmp_path/"state"; m.PostSuccessionVerification(state_dir=d); assert not d.exists()
def test_dry_run_needs_no_authority(tmp_path):
    x=m.PostSuccessionVerification(state_dir=tmp_path/"state"); r=x.step({},dry_run=True); assert r["success"] is True; assert not (tmp_path/"state").exists()
def test_persist_fails_closed_without_context(tmp_path):
    x=m.PostSuccessionVerification(state_dir=tmp_path/"state")
    with pytest.raises(RuntimeError,match="governed_filesystem_context_required"): x.step({})
def test_no_direct_effects_in_migrated_surface():
    t=ast.parse(Path(m.__file__).read_text()); banned={"write_text","write_bytes","open","mkdir","replace","rename","unlink"}; hits=[]
    for n in ast.walk(t):
      if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in banned:
       owners=[x for x in ast.walk(t) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.lineno<=n.lineno<=getattr(x,"end_lineno",x.lineno)]
       if owners:
        fn=max(owners,key=lambda x:x.lineno)
        if fn.name in {"__init__","step","_write_json","_append_jsonl"}: hits.append((fn.name,n.lineno,n.func.attr))
    assert hits==[]
