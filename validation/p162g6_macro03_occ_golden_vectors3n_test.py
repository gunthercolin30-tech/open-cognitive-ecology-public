from types import SimpleNamespace
import ast, inspect, json, textwrap
import pytest
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology import occ_golden_constitutional_vectors as g
RID="r";AD="a";EF="e"
class Broker:
 def __init__(self,ids):self.ids=set(ids);self.used=set()
 def consume_once(self,x):
  if x not in self.ids or x in self.used:return False
  self.used.add(x);return True
def H(i,op,b):return SimpleNamespace(handle_id=i,adapter_id=AD,effector_id=EF,operation_id=op,target_binding=b,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
def B(rel):return "filesystem://"+RID+"/"+rel.as_posix()
def ctx(root,target):
 b=Broker({"w"});e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b)
 c=GovernedFilesystemEffectContext(slots={"occ_golden_vectors_write_replace":[H("w","FS_WRITE_REPLACE_BYTES",B(target.relative_to(root)))]},effector=e,root_id=RID,root_path=root,adapter_id=AD,effector_id=EF)
 c.begin();return c
def test_helper_requires_explicit_authority(tmp_path):
 t=tmp_path/"x.json"
 with pytest.raises(RuntimeError,match="filesystem_effect_context_required"):g._atomic_json(t,{"a":1})
 assert not t.exists()
def test_helper_governed_exact_json(tmp_path):
 t=tmp_path/"x.json";c=ctx(tmp_path,t);g._atomic_json(t,{"é":1,"a":2},c)
 assert t.read_text(encoding="utf-8")==json.dumps({"é":1,"a":2},indent=2,sort_keys=True,ensure_ascii=False)+"\n"
def test_wrong_target_binding_blocked(tmp_path):
 t=tmp_path/"x.json";wrong=tmp_path/"wrong.json";c=ctx(tmp_path,wrong)
 with pytest.raises(RuntimeError,match="governed_filesystem_effect_not_confirmed"):g._atomic_json(t,{"a":1},c)
 assert not t.exists()
def test_helper_has_no_ambient_triad():
 tr=ast.parse(textwrap.dedent(inspect.getsource(g._atomic_json)))
 attrs=[n.func.attr for n in ast.walk(tr) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
 assert not ({"mkdir","replace","unlink","mkstemp"} & set(attrs))
 assert "FS_WRITE_REPLACE_BYTES" in inspect.getsource(g._atomic_json)
def test_materialize_transports_one_context_to_all_writes():
 src=inspect.getsource(g.materialize);tr=ast.parse(textwrap.dedent(src))
 calls=[n for n in ast.walk(tr) if isinstance(n,ast.Call)]
 assert any(isinstance(n.func,ast.Attribute) and n.func.attr=="begin" for n in calls)
 helper=[n for n in calls if isinstance(n.func,ast.Name) and n.func.id=="_atomic_json"]
 assert len(helper)==1 and len(helper[0].args)==3
 assert "FS_CREATE_DIRS" in src
def test_context_replay_is_rejected(tmp_path):
 t=tmp_path/"x.json";c=ctx(tmp_path,t)
 with pytest.raises(RuntimeError,match="filesystem effect context replay"):c.begin()
