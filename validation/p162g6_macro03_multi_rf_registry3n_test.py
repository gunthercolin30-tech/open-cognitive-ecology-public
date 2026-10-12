from pathlib import Path
from types import SimpleNamespace
import ast, inspect, json, textwrap
import pytest
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.multi_rf_registry import MultiRFRegistry
RID="r"; AD="a"; EF="e"
class Broker:
 def __init__(self,ids): self.ids=set(ids); self.used=set()
 def consume_once(self,x):
  if x not in self.ids or x in self.used:return False
  self.used.add(x);return True
def H(i,op,b): return SimpleNamespace(handle_id=i,adapter_id=AD,effector_id=EF,operation_id=op,target_binding=b,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
def B(rel): return "filesystem://"+RID+"/"+rel.as_posix()
def C(root,target,parent):
 slots={"multi_rf_registry_write_replace":[H("w","FS_WRITE_REPLACE_BYTES",B(target.relative_to(root)))]};ids={"w"}
 if parent: slots["multi_rf_registry_parent_create"]=[H("p","FS_CREATE_DIRS",B(target.parent.relative_to(root)))];ids.add("p")
 broker=Broker(ids);eff=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker)
 return GovernedFilesystemEffectContext(slots=slots,effector=eff,root_id=RID,root_path=root,adapter_id=AD,effector_id=EF)
def inp():
 return {"rf_records":[{"rf_id":"RF-T","rf_type":"INDIVIDUAL","status":"ACTIVE","architecture_id":"GENERIC_AGENTIC_SYSTEM","individual_id":"I-T","representative_id":None,"node_ids":["N-T"],"aliases":["t"],"parent_rf_ids":[],"successor_rf_ids":[],"evidence_refs":["test"],"metadata":{"functional_only":True}}]}
def test_nonpersist_unchanged(tmp_path):
 r=MultiRFRegistry(root=tmp_path).step(inputs=inp(),persist=False);assert r["persisted"] is False
def test_missing_authority_fails_before_mutation(tmp_path):
 m=MultiRFRegistry(root=tmp_path);t=m.output_dir/"latest_multi_rf_registry.json"
 with pytest.raises(RuntimeError,match="filesystem_effect_context_required"):m.step(inputs=inp(),persist=True)
 assert not t.exists() and not t.parent.exists()
def test_governed_parent_and_replace(tmp_path):
 m=MultiRFRegistry(root=tmp_path);t=m.output_dir/"latest_multi_rf_registry.json";c=C(tmp_path,t,True)
 r=m.step(inputs=inp(),persist=True,filesystem_effect_context=c);assert r["persisted"] and t.is_file()
 d=json.loads(t.read_text());assert d["persisted"] is True and d["output_path"]==str(t)
 assert c.remaining()=={"multi_rf_registry_write_replace":0,"multi_rf_registry_parent_create":0}
def test_existing_parent_only_write(tmp_path):
 m=MultiRFRegistry(root=tmp_path);m.output_dir.mkdir(parents=True);t=m.output_dir/"latest_multi_rf_registry.json";c=C(tmp_path,t,False)
 assert m.step(inputs=inp(),persist=True,filesystem_effect_context=c)["persisted"];assert c.remaining()=={"multi_rf_registry_write_replace":0}
def test_wrong_target_blocked(tmp_path):
 m=MultiRFRegistry(root=tmp_path);t=m.output_dir/"latest_multi_rf_registry.json";wrong=tmp_path/"wrong.json"
 slots={"multi_rf_registry_parent_create":[H("p","FS_CREATE_DIRS",B(t.parent.relative_to(tmp_path)))],"multi_rf_registry_write_replace":[H("w","FS_WRITE_REPLACE_BYTES",B(wrong.relative_to(tmp_path)))]}
 broker=Broker({"p","w"});eff=GovernedFilesystemEffector(root_registry={RID:str(tmp_path)},handle_broker=broker)
 c=GovernedFilesystemEffectContext(slots=slots,effector=eff,root_id=RID,root_path=tmp_path,adapter_id=AD,effector_id=EF)
 with pytest.raises(RuntimeError,match="governed_filesystem_effect_not_confirmed"):m.step(inputs=inp(),persist=True,filesystem_effect_context=c)
 assert not t.exists()
def test_no_ambient_triad():
 tr=ast.parse(textwrap.dedent(inspect.getsource(MultiRFRegistry._atomic_json_write)))
 attrs=[n.func.attr for n in ast.walk(tr) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
 assert not ({"mkdir","replace","unlink","mkstemp"} & set(attrs))
