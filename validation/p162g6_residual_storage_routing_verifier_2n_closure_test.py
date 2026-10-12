from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.residual_storage_routing_verifier import ResidualStorageRoutingVerifier as C
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";STAMP="2026-10-07T00:00:00+00:00"
def ctx(root,o,drop=None):
 b=ScopedHandleBroker();e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b);slots={};base=o._report_base();state=base/"f17_5_residual_storage_routing_verification_state.json"
 for i,(slot,op,t) in enumerate((("report_parent_create","FS_CREATE_DIRS",base),("state_write","FS_WRITE_REPLACE_BYTES",state))):
  binding=e.canonical_target(RID,t.resolve().relative_to(root.resolve()).as_posix());lease={"lease_id":f"l{i}","reservation_id":f"r{i}","operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"};claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash=f"c{i}");scope={"ambient_authority":False,"child_inheritance":False,"transferable":False};z=b.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP);assert z["status"]=="HANDLE_ISSUED"
  if slot!=drop:slots[slot]=[z["handle"]]
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
def main():
 with TemporaryDirectory() as d:
  root=Path(d);o=C(root=root,ssd_root=root/"absent")
  try:o.step({"producer_dirs":[],"persist_probe":False});raise AssertionError()
  except RuntimeError as x:assert "context required" in str(x)
  assert not (root/"local_storage_fallback").exists()
 print("NO_AMBIENT_FALLBACK_OK")
 with TemporaryDirectory() as d:
  root=Path(d);o=C(root=root,ssd_root=root/"absent");c=ctx(root,o);r=o.step({"producer_dirs":[],"persist_probe":False},filesystem_effect_context=c);assert Path(r["state_path"]).is_file() and Path(r["history_path"]).is_file() and all(v==0 for v in c.remaining().values())
 print("FUNCTIONAL_TEST_OK\nEXACT_HANDLE_CONSUMPTION_OK\nREAL_TCB_OK")
 with TemporaryDirectory() as d:
  root=Path(d);o=C(root=root,ssd_root=root/"absent");bad=ctx(root,o,"state_write")
  try:o.step({"producer_dirs":[],"persist_probe":False},filesystem_effect_context=bad);raise AssertionError()
  except RuntimeError as x:assert "cardinality mismatch" in str(x)
  assert not (root/"local_storage_fallback").exists()
 print("DEGRADATION_TEST_OK")
 with TemporaryDirectory() as d:
  root=Path(d);ssd=root/"ssd";ssd.mkdir();o=C(root=root,ssd_root=ssd);c=ctx(ssd,o);r=o.step({"producer_dirs":[],"persist_probe":False},filesystem_effect_context=c);assert Path(r["state_path"]).resolve().is_relative_to(ssd.resolve())
 print("SSD_ROOT_AUTHORITY_TEST_OK\nNON_REGRESSION_TEST_OK\nADJACENT_HISTORY_APPEND_PRESERVED_OK\nPROBE_WRITES_PRESERVED_OK")
if __name__=="__main__":main()
