from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import ontology.consciousness_public_dashboard as m
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";STAMP="2026-10-07T00:00:00+00:00"
def context(root,public_dir,drop=None):
 b=ScopedHandleBroker();e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b);slots={}
 targets={"latest_json":public_dir/"latest_consciousness_public_dashboard.json","archival_json":public_dir/"consciousness_public_dashboard_20000101T000000Z.json"}
 for i,(label,target) in enumerate(targets.items()):
  for suffix,op,t in (("_parent_create","FS_CREATE_DIRS",target.parent),("_write","FS_WRITE_REPLACE_BYTES",target)):
   slot=label+suffix;binding=e.canonical_target(RID,t.resolve().relative_to(root.resolve()).as_posix())
   lease={"lease_id":f"l{i}{suffix}","reservation_id":f"r{i}{suffix}","operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"}
   claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash=f"c{i}{suffix}")
   scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
   issued=b.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP);assert issued["status"]=="HANDLE_ISSUED"
   if slot!=drop:slots[slot]=[issued["handle"]]
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
def main():
 old_public=m.PUBLIC_DIR;old_stamp=m._stamp
 try:
  with TemporaryDirectory() as td:
   root=Path(td);public_dir=root/"public";m.PUBLIC_DIR=public_dir;m._stamp=lambda:"20000101T000000Z";o=m.ConsciousnessPublicDashboard()
   r=o.step({},persist=False);assert r["json_path"] is None and not public_dir.exists()
  print("PERSIST_FALSE_NO_CONTEXT_OK")
  with TemporaryDirectory() as td:
   root=Path(td);public_dir=root/"public";m.PUBLIC_DIR=public_dir;m._stamp=lambda:"20000101T000000Z";o=m.ConsciousnessPublicDashboard();ctx=context(root,public_dir)
   r=o.step({},persist=True,filesystem_effect_context=ctx);assert Path(r["json_path"]).is_file() and Path(r["archival_json_path"]).is_file()
   assert Path(r["html_path"]).is_file() and Path(r["prometheus_path"]).is_file();assert all(v==0 for v in ctx.remaining().values())
  print("FUNCTIONAL_TEST_OK");print("EXACT_HANDLE_CONSUMPTION_OK");print("REAL_TCB_OK")
  with TemporaryDirectory() as td:
   root=Path(td);public_dir=root/"public";m.PUBLIC_DIR=public_dir;m._stamp=lambda:"20000101T000000Z";o=m.ConsciousnessPublicDashboard()
   try:o.step({},persist=True);raise AssertionError("ambient fallback")
   except RuntimeError as x:assert "context required" in str(x)
   assert not public_dir.exists()
   bad=context(root,public_dir,drop="archival_json_write")
   try:o.step({},persist=True,filesystem_effect_context=bad);raise AssertionError("cardinality loss")
   except RuntimeError as x:assert "cardinality mismatch" in str(x)
   assert not public_dir.exists()
  print("DEGRADATION_TEST_OK");print("NO_AMBIENT_FALLBACK_OK")
  with TemporaryDirectory() as td:
   root=Path(td);public_dir=root/"public";m.PUBLIC_DIR=public_dir;m._stamp=lambda:"20000101T000000Z";o=m.ConsciousnessPublicDashboard();r=o.step({"event_count":2},persist=False)
   assert r["primitive"]=="CONSCIOUSNESS_PUBLIC_DASHBOARD" and r["dashboard_sanitized"] is True
  print("NON_REGRESSION_TEST_OK");print("ADJACENT_EFFECTS_PRESERVED_OK")
 finally:m.PUBLIC_DIR=old_public;m._stamp=old_stamp
 print("P162G6_CONSCIOUSNESS_PUBLIC_DASHBOARD_2N_ATOMIC_REMEDIATION_TEST_OK")
if __name__=="__main__":main()
