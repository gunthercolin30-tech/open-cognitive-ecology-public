from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.f16_grafana_prometheus_provisioning import F16GrafanaPrometheusProvisioning
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";STAMP="2026-10-07T00:00:00+00:00"
LABELS=("prometheus_scrape_config_json","prometheus_scrape_config_yml","prometheus_file_sd_json","grafana_datasource_json","grafana_dashboard_provider_json","grafana_dashboard_json","state_json","history_jsonl")
def obj(root):
 o=object.__new__(F16GrafanaPrometheusProvisioning);o.root=root;o.ssd_root=root;return o
def targets(o):
 b=o.provisioning_root
 return {"prometheus_scrape_config_json":b/"prometheus"/"prometheus_f16_scrape_config.json","prometheus_file_sd_json":b/"prometheus"/"f16_file_sd.json","grafana_datasource_json":b/"grafana"/"provisioning"/"datasources"/"oce_f16_prometheus_datasource.json","grafana_dashboard_provider_json":b/"grafana"/"provisioning"/"dashboards"/"oce_f16_dashboard_provider.json","grafana_dashboard_json":b/"dashboards"/"oce_f16_distributed_continuity_dashboard.json","state_json":b/"f16_grafana_prometheus_provisioning_state.json","prometheus_scrape_config_yml":b/"prometheus"/"prometheus_f16_scrape_config.yml","history_jsonl":b/"f16_grafana_prometheus_provisioning_history.jsonl"}
def context(root,o,drop=None):
 b=ScopedHandleBroker();e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b);slots={}
 for i,(label,target) in enumerate(targets(o).items()):
  effects=(("_parent_create","FS_CREATE_DIRS",target.parent),("_append","FS_APPEND_BYTES",target)) if label=="history_jsonl" else (("_parent_create","FS_CREATE_DIRS",target.parent),("_write","FS_WRITE_REPLACE_BYTES",target))
  for suffix,op,t in effects:
   slot=label+suffix;rel=t.resolve().relative_to(root.resolve()).as_posix();binding=e.canonical_target(RID,rel)
   lease={"lease_id":f"l{i}{suffix}","reservation_id":f"r{i}{suffix}","operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"}
   claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash=f"c{i}{suffix}")
   scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
   issued=b.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP)
   assert issued["status"]=="HANDLE_ISSUED"
   if slot!=drop:slots[slot]=[issued["handle"]]
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
def main():
 with TemporaryDirectory() as td:
  root=Path(td);o=obj(root);r=o.step({"persist":False});assert r["persisted"] is False;assert not o.provisioning_root.exists()
 print("PERSIST_FALSE_NO_CONTEXT_OK")
 with TemporaryDirectory() as td:
  root=Path(td);o=obj(root);ctx=context(root,o);r=o.step({"persist":True},filesystem_effect_context=ctx)
  assert r["persisted"] is True;assert all(targets(o)[k].is_file() for k in LABELS);assert all(v==0 for v in ctx.remaining().values())
 print("FUNCTIONAL_TEST_OK");print("EXACT_HANDLE_CONSUMPTION_OK");print("REAL_TCB_OK")
 with TemporaryDirectory() as td:
  root=Path(td);o=obj(root)
  try:o.step({"persist":True});raise AssertionError("ambient fallback")
  except RuntimeError as x:assert "context required" in str(x)
  assert not o.provisioning_root.exists()
  bad=context(root,o,drop="state_json_write")
  try:o.step({"persist":True},filesystem_effect_context=bad);raise AssertionError("cardinality loss")
  except RuntimeError as x:assert "cardinality mismatch" in str(x)
  assert not o.provisioning_root.exists()
 print("DEGRADATION_TEST_OK");print("NO_AMBIENT_FALLBACK_OK")
 with TemporaryDirectory() as td:
  root=Path(td);o=obj(root);r=o.step({"persist":False,"metrics_port":9999});assert r["primitive"]=="f16_grafana_prometheus_provisioning" and r["metrics_port"]==9999
 print("NON_REGRESSION_TEST_OK");print("P162G6_F16_GRAFANA_PROMETHEUS_PROVISIONING_2N_ATOMIC_REMEDIATION_TEST_OK")
if __name__=="__main__":main()
