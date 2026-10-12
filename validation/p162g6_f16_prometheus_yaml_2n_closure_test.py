from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.f16_grafana_prometheus_provisioning import F16GrafanaPrometheusProvisioning as C
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";STAMP="2026-10-07T00:00:00+00:00"
def obj(r):o=object.__new__(C);o.root=r;o.ssd_root=r;return o
def tg(o):
 b=o.provisioning_root;return {"prometheus_scrape_config_json":b/"prometheus"/"prometheus_f16_scrape_config.json","prometheus_file_sd_json":b/"prometheus"/"f16_file_sd.json","grafana_datasource_json":b/"grafana"/"provisioning"/"datasources"/"oce_f16_prometheus_datasource.json","grafana_dashboard_provider_json":b/"grafana"/"provisioning"/"dashboards"/"oce_f16_dashboard_provider.json","grafana_dashboard_json":b/"dashboards"/"oce_f16_distributed_continuity_dashboard.json","state_json":b/"f16_grafana_prometheus_provisioning_state.json","prometheus_scrape_config_yml":b/"prometheus"/"prometheus_f16_scrape_config.yml"}
def ctx(root,o,drop=None):
 b=ScopedHandleBroker();e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b);slots={}
 for i,(label,target) in enumerate(tg(o).items()):
  for suf,op,t in (("_parent_create","FS_CREATE_DIRS",target.parent),("_write","FS_WRITE_REPLACE_BYTES",target)):
   slot=label+suf;binding=e.canonical_target(RID,t.resolve().relative_to(root.resolve()).as_posix());lease={"lease_id":f"l{i}{suf}","reservation_id":f"r{i}{suf}","operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"};claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash=f"c{i}{suf}");scope={"ambient_authority":False,"child_inheritance":False,"transferable":False};z=b.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP);assert z["status"]=="HANDLE_ISSUED"
   if slot!=drop:slots[slot]=[z["handle"]]
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
def main():
 with TemporaryDirectory() as d:r=Path(d);o=obj(r);z=o.step({"persist":False});assert z["persisted"] is False and not o.provisioning_root.exists()
 print("PERSIST_FALSE_NO_CONTEXT_OK")
 with TemporaryDirectory() as d:
  r=Path(d);o=obj(r);c=ctx(r,o);z=o.step({"persist":True},filesystem_effect_context=c);assert z["persisted"] is True and all(x.is_file() for x in tg(o).values()) and all(v==0 for v in c.remaining().values());assert tg(o)["prometheus_scrape_config_yml"].read_text().endswith("\n")
 print("FUNCTIONAL_TEST_OK\nEXACT_HANDLE_CONSUMPTION_OK\nREAL_TCB_OK")
 with TemporaryDirectory() as d:
  r=Path(d);o=obj(r)
  try:o.step({"persist":True});raise AssertionError()
  except RuntimeError as x:assert "context required" in str(x)
  assert not o.provisioning_root.exists();bad=ctx(r,o,"prometheus_scrape_config_yml_write")
  try:o.step({"persist":True},filesystem_effect_context=bad);raise AssertionError()
  except RuntimeError as x:assert "cardinality mismatch" in str(x)
  assert not o.provisioning_root.exists()
 print("DEGRADATION_TEST_OK\nNO_AMBIENT_FALLBACK_OK")
 with TemporaryDirectory() as d:r=Path(d);o=obj(r);assert o.step({"persist":False,"metrics_port":9999})["metrics_port"]==9999
 print("NON_REGRESSION_TEST_OK\nP162G6_F16_PROMETHEUS_YAML_2N_TEST_OK")
if __name__=="__main__":main()
