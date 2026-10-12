from pathlib import Path
import ast,tempfile
import pytest
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.scoped_handle_broker import ScopedEffectHandle
from ontology import occ_constitutional_adversarial_crown_h7 as h7
from validation.p162g6_index75_h7_governance_harness import _Broker,_handle,_dest_binding,_copy_binding,make_h7_leases,run_h7
ROOT=Path(__file__).resolve().parents[1]
def test_missing_governance_fails_before_h7_execution():
 with pytest.raises(PermissionError,match="EXACT_SEVEN"): h7.run(ROOT)
def test_exact_seven_leases_and_nonregression():
 r=run_h7(ROOT); assert r["scenario_count"]==11; assert [x["attack_id"] for x in r["rows"]]==["A%03d"%i for i in range(65,76)]
def test_copy2_target_symlink_fails_closed_before_consumption():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td).resolve(); src=root/"src"; src.write_text("x"); outside=root/"outside"; outside.write_text("o"); dst=root/"dst"; dst.symlink_to(outside)
  b=_Broker(); eff=GovernedFilesystemEffector(root_registry={"r":str(root)},handle_broker=b); target={"source":"filesystem://r/src","destination":"filesystem://r/dst"}; h=_handle(b,"FS_COPY2",target,1)
  from ontology.governed_filesystem_effector import FilesystemEffectRequest
  q=FilesystemEffectRequest("FS_COPY2","r","dst",None,"r","src"); z=eff.execute(request=q,handle=h,adapter_id="h7-adapter",effector_id="filesystem-effector")
  assert z["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK" and z["reason"]=="target_symlink_forbidden"; assert h.handle_id not in b.used; assert outside.read_text()=="o"
def test_copy2_source_destination_binding_mismatch_fails_closed():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td).resolve(); src=root/"src"; src.write_text("x"); dst=root/"dst"
  b=_Broker(); eff=GovernedFilesystemEffector(root_registry={"r":str(root)},handle_broker=b); wrong={"source":"filesystem://r/src","destination":"filesystem://r/wrong"}; h=_handle(b,"FS_COPY2",wrong,2)
  from ontology.governed_filesystem_effector import FilesystemEffectRequest
  q=FilesystemEffectRequest("FS_COPY2","r","dst",None,"r","src"); z=eff.execute(request=q,handle=h,adapter_id="h7-adapter",effector_id="filesystem-effector")
  assert z["reason"]=="target_mismatch" and not dst.exists() and h.handle_id not in b.used
def test_run_has_no_direct_ambient_mutators():
 src=Path(h7.__file__).read_text(encoding="utf-8"); tree=ast.parse(src); run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="run"); bad=[]
 for n in ast.walk(run):
  if isinstance(n,ast.Call):
   f=ast.get_source_segment(src,n.func) or ""
   if f in {"shutil.copy2","sb_ctx.remove_tree"} or f.endswith(".unlink") or f.endswith(".mkdir") or f.endswith(".write_text"): bad.append((n.lineno,f))
 assert bad==[]
def test_a075_parent_chains_are_governed_and_preissued():
 leases=make_h7_leases(ROOT); lease=leases[6]; sb=lease["context"].root/"repo"; fctx=lease["filesystem_context"]
 required=["ontology","validation_artifacts","validation_artifacts/p159","validation_artifacts/p159/occ1f"]
 for rel in required:
  assert rel in lease["parent_slots"]; slot=lease["parent_slots"][rel]; assert len(fctx._queues[slot])==1
 try:
  r=h7.run(ROOT,sandbox_leases=leases); assert r["scenario_count"]==11
  consumed=0
  for rel in required:
   slot=lease["parent_slots"][rel]
   if fctx._queues[slot]==[]: consumed+=1
  assert consumed>=1
 finally:
  for item in leases:
   if item.get("cleaned") is True: continue
   fc=item["filesystem_context"]
   if not fc._begun: fc.begin()
   h7._cleanup(item)

def test_missing_parent_authority_fails_closed():
 leases=make_h7_leases(ROOT); lease=leases[6]; slot=lease["parent_slots"]["validation_artifacts/p159/occ1f"]; lease["filesystem_context"]._queues[slot]=[]
 try:
  with pytest.raises(RuntimeError,match="no remaining handle for filesystem effect slot"): h7.run(ROOT,sandbox_leases=leases)
 finally:
  for item in leases:
   if item.get("cleaned") is True: continue
   fc=item["filesystem_context"]
   if not fc._begun: fc.begin()
   h7._cleanup(item)

def test_missing_parent_handle_does_not_create_target_parent():
 leases=make_h7_leases(ROOT); lease=leases[6]; rel="validation_artifacts/p159/occ1f"; slot=lease["parent_slots"][rel]; target=lease["context"].root/"repo"/rel
 lease["filesystem_context"]._queues[slot]=[]
 try:
  with pytest.raises(RuntimeError,match="no remaining handle for filesystem effect slot"): h7.run(ROOT,sandbox_leases=leases)
  assert not target.exists()
 finally:
  for item in leases:
   if item.get("cleaned") is True: continue
   fc=item["filesystem_context"]
   if not fc._begun: fc.begin()
   h7._cleanup(item)

def test_a075_current_governed_contract_remains_inconclusive():
 r=run_h7(ROOT); row=next(x for x in r["rows"] if x["attack_id"]=="A075")
 assert row["verdict"]=="INCONCLUSIVE"
 assert row["authorization_created"] is False and row["execution_performed"] is False
 assert r["authorization_created"] is False and r["execution_performed"] is False

def test_a075_self_activation_degradation_uses_current_governed_mut_api():
 leases=make_h7_leases(ROOT); lease=leases[6]; ctx,sb=h7._sandbox(ROOT,lease)
 try:
  before=h7.verifier.verify(sb); assert "IVI-11" not in before.get("failed_check_ids",[])
  def attack(x): x.setdefault("lifecycle_model",{})["self_activation"]=True
  h7._mut(ctx,sb,attack,True)
  after=h7.verifier.verify(sb); assert "IVI-11" in after.get("failed_check_ids",[])
 finally:
  if lease.get("cleaned") is not True: h7._cleanup(lease)

def test_lease_cleanup_and_authority_properties():
 leases=make_h7_leases(ROOT); roots=[x["context"].root for x in leases]; r=h7.run(ROOT,sandbox_leases=leases); assert all(x["cleaned"] for x in leases); assert all(not p.exists() for p in roots); assert all(x["filesystem_context"].authority_minting is False for x in leases); assert r["authorization_created"] is False and r["execution_performed"] is False
