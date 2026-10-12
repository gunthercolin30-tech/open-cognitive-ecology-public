import ast,inspect,json,textwrap
from pathlib import Path
from types import SimpleNamespace
import pytest
from ontology import occ_p159_final_lock as fl
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
class Broker:
 def __init__(self,ids):self.ids=set(ids);self.used=set()
 def consume_once(self,h):
  if h not in self.ids or h in self.used:return False
  self.used.add(h);return True
def handle(i,op,b):return SimpleNamespace(handle_id=i,adapter_id="test-adapter",effector_id="test-effector",operation_id=op,target_binding=b,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
def binding(root,path):return "filesystem://p159-final-lock-test/"+Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
def ctx(root,target,dirs=False,wrong=False):
 ids={"w"};slots={"p159_final_lock_write_replace":[handle("w","FS_WRITE_REPLACE_BYTES",binding(root,target.parent if wrong else target))]}
 if dirs:ids.add("d");slots["p159_final_lock_create_dirs"]=[handle("d","FS_CREATE_DIRS",binding(root,target.parent))]
 b=Broker(ids);e=GovernedFilesystemEffector(root_registry={"p159-final-lock-test":str(root)},handle_broker=b)
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id="p159-final-lock-test",root_path=root,adapter_id="test-adapter",effector_id="test-effector")
def test_missing_authority_fails_before_mutation(tmp_path):
 p=tmp_path/"x.json"
 with pytest.raises(RuntimeError,match="occ_p159_final_lock_filesystem_effect_context_required"):fl.atomic_json(p,{"a":1})
 assert not p.exists()
def test_governed_missing_parent_exact_serialization(tmp_path):
 p=tmp_path/"nested"/"x.json";c=ctx(tmp_path,p,True);o={"z":"é","a":1};fl.atomic_json(p,o,c)
 assert p.read_bytes()==(json.dumps(o,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode("utf-8")
 assert c.remaining()=={"p159_final_lock_write_replace":0,"p159_final_lock_create_dirs":0}
def test_wrong_target_binding_fails_closed(tmp_path):
 p=tmp_path/"x.json";c=ctx(tmp_path,p,False,True)
 with pytest.raises(RuntimeError,match="governed_filesystem_effect_not_confirmed"):fl.atomic_json(p,{"a":1},c)
 assert not p.exists()
def test_existing_parent_uses_write_only(tmp_path):
 p=tmp_path/"x.json";fl.atomic_json(p,{"a":1},ctx(tmp_path,p));assert json.loads(p.read_text())=={"a":1}
def test_no_historical_ambient_triad():
 s=inspect.getsource(fl.atomic_json);t=ast.parse(textwrap.dedent(s));attrs={n.func.attr for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
 assert not ({"mkdir","replace","unlink","mkstemp","fdopen"}&attrs)
 assert all(x in s for x in ("FS_CREATE_DIRS","FS_WRITE_REPLACE_BYTES",".begin()"))
def test_operational_callers_transport_context():
 import validation.p159_occ1k_eligibility_v1 as e
 import validation.p159_occ1k_commit_final_lock_v1 as c
 import validation.p159_occ1k_postlock_verification_v1 as p
 for m in (e,c,p):
  assert "filesystem_effect_context" in inspect.signature(m.main).parameters
  assert "filesystem_effect_context)" in inspect.getsource(m.main)
