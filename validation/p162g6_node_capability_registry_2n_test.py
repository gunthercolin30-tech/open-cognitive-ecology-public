from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.node_capability_registry import NodeCapabilityRegistry as C
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";STAMP="2026-10-07T00:00:00+00:00"
def obj(root):
 o=object.__new__(C);o.root=root;o.ontology_dir=root/"ontology";o.node_dir=root/"distributed_nodes";o.node_identity_path=o.node_dir/"local_node_identity.json";o.registry_path=o.node_dir/"node_capability_registry.json";o.history_path=o.node_dir/"node_capability_history.jsonl";o.node_id="test-node";return o
def ctx(root,o,drop=None):
 b=ScopedHandleBroker();e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b);slots={}
 for i,(slot,op,t) in enumerate((("registry_parent_create","FS_CREATE_DIRS",o.registry_path.parent),("registry_write","FS_WRITE_REPLACE_BYTES",o.registry_path))):
  binding=e.canonical_target(RID,t.resolve().relative_to(root.resolve()).as_posix());lease={"lease_id":f"l{i}","reservation_id":f"r{i}","operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"};claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash=f"c{i}");scope={"ambient_authority":False,"child_inheritance":False,"transferable":False};z=b.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP);assert z["status"]=="HANDLE_ISSUED"
  if slot!=drop:slots[slot]=[z["handle"]]
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
def main():
 with TemporaryDirectory() as d:
  root=Path(d);o=obj(root);c=ctx(root,o);assert o._write_json(o.registry_path,{"x":1},c) is True and o.registry_path.is_file() and all(v==0 for v in c.remaining().values())
 print("FUNCTIONAL_TEST_OK\nEXACT_HANDLE_CONSUMPTION_OK\nREAL_TCB_OK")
 with TemporaryDirectory() as d:
  root=Path(d);o=obj(root);assert o._write_json(o.registry_path,{"x":1},None) is False and not o.registry_path.exists()
 print("BOOLEAN_FAILURE_CONTRACT_OK\nNO_AMBIENT_FALLBACK_OK")
 with TemporaryDirectory() as d:
  root=Path(d);o=obj(root);bad=ctx(root,o,"registry_write");assert o._write_json(o.registry_path,{"x":1},bad) is False and not o.registry_path.exists()
 print("DEGRADATION_TEST_OK\nBROAD_EXCEPTION_CONVERSION_PRESERVED_OK\nNON_REGRESSION_TEST_OK")
if __name__=="__main__":main()
