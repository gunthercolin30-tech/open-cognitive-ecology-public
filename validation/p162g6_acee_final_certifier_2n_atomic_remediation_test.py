from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
from ontology.acee_final_certifier import ACEEFinalCertifier
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";STAMP="2026-10-07T00:00:00+00:00"
def ctx(root,runtime,drop=None):
 b=ScopedHandleBroker();e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b);slots={}
 for i,(slot,op,target) in enumerate((("persist_runtime_dir","FS_CREATE_DIRS",runtime),("persist_certification","FS_WRITE_REPLACE_BYTES",runtime/"latest_final_certification.json"))):
  rel=target.resolve().relative_to(root.resolve()).as_posix();binding=e.canonical_target(RID,rel)
  lease={"lease_id":f"l{i}","reservation_id":f"r{i}","operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"}
  claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash=f"c{i}")
  scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
  issued=b.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP)
  assert issued["status"]=="HANDLE_ISSUED"
  if slot!=drop:slots[slot]=[issued["handle"]]
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
def main():
 with TemporaryDirectory() as td:
  root=Path(td);rt=root/"rt";o=ACEEFinalCertifier(root=root,runtime_dir=rt);r=o.step({},persist=False);assert not r["persisted"] and not rt.exists()
 print("NON_REGRESSION_TEST_OK")
 with TemporaryDirectory() as td:
  root=Path(td);rt=root/"rt";o=ACEEFinalCertifier(root=root,runtime_dir=rt)
  try:o.step({},persist=True);raise AssertionError("ambient")
  except RuntimeError as x:assert "governed filesystem effect context required" in str(x)
  assert not rt.exists();bad=ctx(root,rt,"persist_certification")
  try:o.step({},persist=True,filesystem_effect_context=bad);raise AssertionError("cardinality")
  except RuntimeError as x:assert "slot cardinality mismatch" in str(x)
  assert not rt.exists()
 print("DEGRADATION_TEST_OK")
 with TemporaryDirectory() as td:
  root=Path(td);rt=root/"rt";o=ACEEFinalCertifier(root=root,runtime_dir=rt);c=ctx(root,rt);r=o.step({},persist=True,filesystem_effect_context=c);p=rt/"latest_final_certification.json";disk=json.loads(p.read_text())
  assert r==disk and r["persisted"] and all(v==0 for v in c.remaining().values())
 print("FUNCTIONAL_TEST_OK");print("REAL_TCB_OK");print("EXACT_HANDLE_CONSUMPTION_OK");print("NO_AMBIENT_FALLBACK_OK");print("P162G6_ACEE_FINAL_CERTIFIER_2N_ATOMIC_REMEDIATION_TEST_OK")
if __name__=="__main__":main()
