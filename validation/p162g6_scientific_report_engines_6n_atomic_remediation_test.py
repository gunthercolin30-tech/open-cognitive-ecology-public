from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.bias_detection_engine import BiasDetectionEngine
from ontology.anomaly_in_evidence_detector import AnomalyInEvidenceDetector
from ontology.scientific_consistency_validator import ScientificConsistencyValidator
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";STAMP="2026-10-07T00:00:00+00:00"
CLASSES=(BiasDetectionEngine,AnomalyInEvidenceDetector,ScientificConsistencyValidator)
def context(root,plan,drop=None):
 b=ScopedHandleBroker();e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b);slots={}
 specs=(("persist_parent_create","FS_CREATE_DIRS",Path(plan["report_path"]).parent),
        ("persist_report_write","FS_WRITE_REPLACE_BYTES",Path(plan["report_path"])))
 for i,(slot,op,target) in enumerate(specs):
  rel=target.resolve().relative_to(root.resolve()).as_posix();binding=e.canonical_target(RID,rel)
  lease={"lease_id":f"l{i}","reservation_id":f"r{i}","operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"}
  claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash=f"c{i}")
  scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
  issued=b.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},
   requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP)
  assert issued["status"]=="HANDLE_ISSUED",issued
  if slot!=drop:slots[slot]=[issued["handle"]]
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
def main():
 for cls in CLASSES:
  with TemporaryDirectory() as td:
   root=Path(td);obj=cls(report_dir=root/"reports");plan=obj.plan_persistence()
   assert plan["operation_cardinality"]=={"FS_CREATE_DIRS":1,"FS_WRITE_REPLACE_BYTES":1}
   ctx=context(root,plan);r=obj.step({},persist=True,filesystem_effect_context=ctx)
   rp=Path(r["report_path"]);assert rp.is_file();assert all(v==0 for v in ctx.remaining().values())
   assert rp.read_text(encoding="utf-8").startswith("{")
 print("FUNCTIONAL_TEST_OK")
 for cls in CLASSES:
  with TemporaryDirectory() as td:
   root=Path(td);obj=cls(report_dir=root/"reports")
   try:obj.step({},persist=True);raise AssertionError("ambient fallback")
   except RuntimeError as x:assert "governed filesystem effect context required" in str(x)
   assert not (root/"reports").exists()
   plan=obj.plan_persistence();bad=context(root,plan,drop="persist_report_write")
   try:obj.step({},persist=True,filesystem_effect_context=bad);raise AssertionError("cardinality loss")
   except RuntimeError as x:assert "slot cardinality mismatch" in str(x)
   assert not (root/"reports").exists()
 print("DEGRADATION_TEST_OK")
 for cls in CLASSES:
  with TemporaryDirectory() as td:
   root=Path(td);obj=cls(report_dir=root/"reports");r=obj.step({},persist=False)
   assert not (root/"reports").exists();assert r["report_path"].endswith("_report.json")
 print("NON_REGRESSION_TEST_OK")
 print("REAL_TCB_OK")
 print("EXACT_HANDLE_CONSUMPTION_OK")
 print("NO_AMBIENT_FALLBACK_OK")
 print("P162G6_SCIENTIFIC_REPORT_ENGINES_6N_ATOMIC_REMEDIATION_TEST_OK")
if __name__=="__main__":main()
