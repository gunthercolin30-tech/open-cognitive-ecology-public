import ast
from pathlib import Path
import pytest
import ontology.embodied_world_model_update as w
import ontology.reflexive_longitudinal_observatory as o

def test_world_dry_run_no_authority(tmp_path):
    r=w.EmbodiedWorldModelUpdate(root=tmp_path).step({},persist=False)
    assert r["persisted"] is False
    assert not (tmp_path/"embodied_world_model").exists()

def test_world_persist_fails_closed(tmp_path):
    with pytest.raises(RuntimeError,match="governed_filesystem_context_required"):
        w.EmbodiedWorldModelUpdate(root=tmp_path).step({},persist=True)

def test_observatory_dry_run_no_authority(tmp_path):
    payload={"reflexive_threshold_score":0.2,"threshold_probability":0.2,"stability_index":0.8,"regression_risk":0.2}
    r=o.ReflexiveLongitudinalObservatory(root=tmp_path).step(payload,persist=False)
    assert r["success"] is True
    assert not (tmp_path/"reflexive_threshold").exists()

def test_observatory_persist_fails_closed(tmp_path):
    payload={"reflexive_threshold_score":0.2,"threshold_probability":0.2,"stability_index":0.8,"regression_risk":0.2}
    with pytest.raises(RuntimeError,match="governed_filesystem_context_required"):
        o.ReflexiveLongitudinalObservatory(root=tmp_path).step(payload,persist=True)

def test_discovery_world_model_explicitly_nonpersistent():
    p=Path(__file__).resolve().parents[1]/"ontology"/"embodied_runtime_coupling_certifier.py"
    src=p.read_text(encoding="utf-8")
    assert '"embodied_world_model_update": _safe_invoke("embodied_world_model_update", persist=False)' in src
    tree=ast.parse(src)
    matches=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="_safe_invoke":
            if n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=="embodied_world_model_update":
                matches.append(n)
    assert len(matches)==1
    persist=[kw for kw in matches[0].keywords if kw.arg=="persist"]
    assert len(persist)==1 and isinstance(persist[0].value,ast.Constant) and persist[0].value.value is False

def test_no_direct_effects_in_migrated_helpers():
    banned={"mkdir","write_text","write_bytes","open","unlink","rename"}
    for mod in (w,o):
        t=ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
        hits=[]
        for n in ast.walk(t):
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in banned:
                owners=[x for x in ast.walk(t) if isinstance(x,ast.FunctionDef) and x.lineno<=n.lineno<=getattr(x,"end_lineno",x.lineno)]
                if owners:
                    fn=max(owners,key=lambda x:x.lineno)
                    if fn.name in {"_write_json","_append_jsonl","step"}: hits.append((fn.name,n.lineno,n.func.attr))
        assert hits==[]
