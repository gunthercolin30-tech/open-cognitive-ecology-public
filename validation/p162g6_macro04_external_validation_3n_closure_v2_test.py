from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
from ontology.external_validation_dashboard import ExternalValidationDashboard
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";NOW="2026-10-07T00:00:00+00:00"
def make_provider(root):
 contexts=[]
 def provider(op,target,slot):
  assert op=="FS_WRITE_REPLACE_BYTES"
  target=Path(target);broker=ScopedHandleBroker()
  eff=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker)
  binding=eff.canonical_target(RID,target.resolve().relative_to(root.resolve()).as_posix())
  lease={"lease_id":"l-"+slot,"reservation_id":"r-"+slot,"operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"}
  claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash="c-"+slot)
  scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
  issued=broker.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=NOW)
  assert issued["status"]=="HANDLE_ISSUED"
  ctx=GovernedFilesystemEffectContext(slots={slot:[issued["handle"]]},effector=eff,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
  contexts.append(ctx);return ctx
 return provider,contexts
def main():
 with TemporaryDirectory() as td:
  root=Path(td);obj=ExternalValidationDashboard(root=root)
  p=root/"x.prom"
  try:obj._write_prometheus(p,{"external_validation_composite_index":1,"external_validation_readiness":1,"repository_governance_score":1,"replication_readiness_score":1,"publication_traceability_score":1,"scientific_traceability":1,"dashboard_integrity":1});raise AssertionError
  except RuntimeError as e:assert "provider_required" in str(e)
  assert not p.exists()
 print("DEGRADATION_TEST_OK")
 with TemporaryDirectory() as td:
  root=Path(td);provider,contexts=make_provider(root);obj=ExternalValidationDashboard(root=root,filesystem_effect_context_provider=provider)
  scores={k:1.0 for k in ("external_validation_composite_index","external_validation_readiness","repository_governance_score","replication_readiness_score","publication_traceability_score","scientific_traceability","dashboard_integrity")}
  p1=root/"a.prom";p2=root/"a.html";p3=root/"a.json"
  obj._write_prometheus(p1,scores)
  result={"component_scores":scores,"primitive":"x","refinement":"x","success":True,"timestamp_utc":"x"}
  obj._write_html(p2,result);obj._write_grafana_json(p3)
  assert p1.exists() and p2.exists() and p3.exists()
  assert json.loads(p3.read_text())["schemaVersion"]==39
  assert len(contexts)==3 and all(sum(c.remaining().values())==0 for c in contexts)
 print("FUNCTIONAL_TEST_OK");print("REAL_TCB_OK");print("EXACT_HANDLE_CONSUMPTION_OK")
 with TemporaryDirectory() as td:
  obj=ExternalValidationDashboard(root=Path(td))
  r=obj.step(external_validation_context={},persist=False)
  assert r["diagnostics"]["persist_requested"] is False
 print("NON_REGRESSION_TEST_OK");print("P162G6_MACRO04_EXTERNAL_VALIDATION_3N_TEST_OK")
if __name__=="__main__":main()
