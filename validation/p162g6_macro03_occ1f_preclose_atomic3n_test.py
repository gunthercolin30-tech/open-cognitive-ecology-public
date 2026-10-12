from types import SimpleNamespace
import ast, inspect, json, textwrap
import pytest
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology import occ_independent_constitutional_verification_report as m
RID="r"; AD="a"; EF="e"
class Broker:
    def __init__(self,ids): self.ids=set(ids); self.used=set()
    def consume_once(self,x):
        if x not in self.ids or x in self.used:return False
        self.used.add(x); return True
def H(i,op,b): return SimpleNamespace(handle_id=i,adapter_id=AD,effector_id=EF,operation_id=op,target_binding=b,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
def B(rel): return "filesystem://"+RID+"/"+rel.as_posix()
def C(root,targets,parent=False):
    slots={"occ1f_preclose_write_replace":[H("w"+str(i),"FS_WRITE_REPLACE_BYTES",B(t.relative_to(root))) for i,t in enumerate(targets)]}
    ids={"w"+str(i) for i in range(len(targets))}
    if parent:
        p=targets[0].parent;slots["occ1f_preclose_create_dirs"]=[H("p","FS_CREATE_DIRS",B(p.relative_to(root)))];ids.add("p")
    broker=Broker(ids);eff=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker)
    c=GovernedFilesystemEffectContext(slots=slots,effector=eff,root_id=RID,root_path=root,adapter_id=AD,effector_id=EF)
    c.begin();return c
def test_helper_requires_authority(tmp_path):
    t=tmp_path/"x.json"
    with pytest.raises(RuntimeError,match="filesystem_effect_context_required"):m._atomic_json_write(t,{"a":1})
    assert not t.exists()
def test_helper_exact_governed_json(tmp_path):
    t=tmp_path/"x.json";c=C(tmp_path,[t]);m._atomic_json_write(t,{"é":1,"a":2},c)
    assert t.read_text(encoding="utf-8")==json.dumps({"é":1,"a":2},indent=2,sort_keys=True,ensure_ascii=False)+"\n"
def test_two_distinct_write_handles_consumed_in_order(tmp_path):
    a=tmp_path/"a.json";b=tmp_path/"b.json";c=C(tmp_path,[a,b])
    m._atomic_json_write(a,{"n":1},c);m._atomic_json_write(b,{"n":2},c)
    assert json.loads(a.read_text())["n"]==1 and json.loads(b.read_text())["n"]==2
    assert c.remaining()=={"occ1f_preclose_write_replace":0}
def test_wrong_binding_blocked(tmp_path):
    t=tmp_path/"x.json";wrong=tmp_path/"wrong.json";c=C(tmp_path,[wrong])
    with pytest.raises(RuntimeError,match="governed_filesystem_effect_not_confirmed"):m._atomic_json_write(t,{"a":1},c)
    assert not t.exists()
def test_no_ambient_triad_in_helper():
    tr=ast.parse(textwrap.dedent(inspect.getsource(m._atomic_json_write)))
    attrs=[n.func.attr for n in ast.walk(tr) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert not ({"mkdir","replace","unlink","mkstemp"} & set(attrs))
    assert "FS_WRITE_REPLACE_BYTES" in inspect.getsource(m._atomic_json_write)
def test_caller_transports_single_context_to_two_writes():
    src=inspect.getsource(m.materialize_preclose_evidence);tr=ast.parse(textwrap.dedent(src))
    calls=[n for n in ast.walk(tr) if isinstance(n,ast.Call)]
    helper=[n for n in calls if isinstance(n.func,ast.Name) and n.func.id=="_atomic_json_write"]
    assert len(helper)==2 and all(len(x.args)==3 for x in helper)
    assert "FS_CREATE_DIRS" in src and "filesystem_effect_context.begin()" in src
