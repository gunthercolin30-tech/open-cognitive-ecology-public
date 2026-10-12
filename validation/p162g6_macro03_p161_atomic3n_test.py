import ast,inspect,json,textwrap
from pathlib import Path
from types import SimpleNamespace
import pytest
from ontology import p161_authorization_token_persistence as p
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
class Broker:
 def __init__(self,ids):self.ids=set(ids);self.used=set()
 def consume_once(self,h):
  if h not in self.ids or h in self.used:return False
  self.used.add(h);return True
def handle(i,op,b):return SimpleNamespace(handle_id=i,adapter_id="test-adapter",effector_id="test-effector",operation_id=op,target_binding=b,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
def binding(root,path):return "filesystem://p161-test/"+Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
def ctx(root,target,include_mkdir=False,wrong=False):
 ids={"w"};slots={"p161_atomic_write_replace":[handle("w","FS_WRITE_REPLACE_BYTES",binding(root,target.parent if wrong else target))]}
 if include_mkdir:ids.add("d");slots["p161_atomic_create_dirs"]=[handle("d","FS_CREATE_DIRS",binding(root,target.parent))]
 b=Broker(ids);e=GovernedFilesystemEffector(root_registry={"p161-test":str(root)},handle_broker=b)
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id="p161-test",root_path=root,adapter_id="test-adapter",effector_id="test-effector")
def test_missing_authority_fails_before_mutation(tmp_path):
 target=tmp_path/"x.json"
 with pytest.raises(RuntimeError,match="p161_atomic_filesystem_effect_context_required"):p.atomic(target,{"b":1})
 assert not target.exists()
def test_governed_missing_parent_exact_serialization(tmp_path):
 target=tmp_path/"nested"/"x.json";c=ctx(tmp_path,target,True);p.atomic(target,{"z":"é","a":1},c)
 assert target.read_bytes()==(json.dumps({"z":"é","a":1},sort_keys=True,indent=2)+"\n").encode("utf-8")
 assert c.remaining()=={"p161_atomic_write_replace":0,"p161_atomic_create_dirs":0}
def test_wrong_target_binding_blocked(tmp_path):
 target=tmp_path/"x.json";c=ctx(tmp_path,target,False,True)
 with pytest.raises(RuntimeError,match="governed_filesystem_effect_not_confirmed"):p.atomic(target,{"a":1},c)
 assert not target.exists()
def test_store_and_registry_transport(tmp_path):
 (tmp_path/"store").mkdir();st=p.TokenStore(tmp_path);token={"body":{"token_id":"T"},"token_hash":"h"};target=tmp_path/"store/T.json"
 st.persist(token,ctx(tmp_path,target));assert json.loads(target.read_text())==token
 reg=p.TokenRegistry(tmp_path);rt=tmp_path/"registry.json";reg.write({"version":1,"tokens":{}},ctx(tmp_path,rt));assert json.loads(rt.read_text())["version"]==1
def test_no_historical_ambient_triad():
 s=inspect.getsource(p.atomic);t=ast.parse(textwrap.dedent(s));attrs=[n.func.attr for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
 assert not ({"mkdir","replace","unlink","mkstemp","fdopen"}&set(attrs))
 assert all(x in s for x in ("FS_CREATE_DIRS","FS_WRITE_REPLACE_BYTES",".begin()"))
def test_runtime_transport_parameters():
 checks={"commit_token":["store_filesystem_effect_context","registry_filesystem_effect_context"],"reconstruct":["filesystem_effect_context"],"reserve":["registry_filesystem_effect_context"],"consume":["registry_filesystem_effect_context"],"revoke":["registry_filesystem_effect_context"]}
 for name,params in checks.items():
  sig=inspect.signature(getattr(p.P161JRuntime,name))
  for q in params:assert q in sig.parameters
 assert "filesystem_effect_context" in inspect.signature(p.TokenStore.persist).parameters
 assert "filesystem_effect_context" in inspect.signature(p.TokenRegistry.write).parameters
