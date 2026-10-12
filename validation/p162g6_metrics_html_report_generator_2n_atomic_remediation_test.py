from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.metrics_html_report_generator import MetricsHTMLReportGenerator
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";STAMP="2026-10-07T00:00:00+00:00"
P=("metrics_report","longitudinal_metrics_dashboard","conversation_metrics_report","runtime_metrics_report","state")
def context(root,reports,metrics,drop=None):
 b=ScopedHandleBroker();e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b);slots={}
 names={"metrics_report":"metrics_report.html","longitudinal_metrics_dashboard":"longitudinal_metrics_dashboard.html","conversation_metrics_report":"conversation_metrics_report.html","runtime_metrics_report":"runtime_metrics_report.html"}
 targets={p:reports/names[p] for p in P[:-1]};targets["state"]=metrics/"metrics_html_report_generator_state.json"
 specs=[]
 for p in P: specs += [(p+"_parent_create","FS_CREATE_DIRS",targets[p].parent),(p+"_write","FS_WRITE_REPLACE_BYTES",targets[p])]
 for i,(slot,op,target) in enumerate(specs):
  rel=target.resolve().relative_to(root.resolve()).as_posix();binding=e.canonical_target(RID,rel)
  lease={"lease_id":f"l{i}","reservation_id":f"r{i}","operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"}
  claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash=f"c{i}")
  scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
  issued=b.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP)
  assert issued["status"]=="HANDLE_ISSUED",issued
  if slot!=drop:slots[slot]=[issued["handle"]]
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
def main():
 with TemporaryDirectory() as td:
  root=Path(td);metrics=root/"metrics";reports=metrics/"reports";obj=MetricsHTMLReportGenerator(metrics,reports);ctx=context(root,reports,metrics);r=obj.step(filesystem_effect_context=ctx)
  assert r["metrics_html_report_generator_operational"] is True and r["report_count"]==4 and Path(r["state_path"]).is_file() and all(v==0 for v in ctx.remaining().values())
 print("FUNCTIONAL_TEST_OK")
 with TemporaryDirectory() as td:
  root=Path(td);metrics=root/"metrics";reports=metrics/"reports";obj=MetricsHTMLReportGenerator(metrics,reports)
  try:obj.step();raise AssertionError("ambient fallback")
  except RuntimeError as x:assert "governed filesystem effect context required" in str(x)
  assert not reports.exists();bad=context(root,reports,metrics,drop="state_write")
  try:obj.step(filesystem_effect_context=bad);raise AssertionError("cardinality loss")
  except RuntimeError as x:assert "slot cardinality mismatch" in str(x)
  assert not reports.exists()
 print("DEGRADATION_TEST_OK")
 with TemporaryDirectory() as td:
  root=Path(td);metrics=root/"metrics";reports=metrics/"reports";obj=MetricsHTMLReportGenerator(metrics,reports);ctx=context(root,reports,metrics);r=obj.step(inputs={"ignored":"compatible"},filesystem_effect_context=ctx)
  assert r["primitive"]=="metrics_html_report_generator" and r["error_count"]==0 and r["diagnostics"]["html_escaped"] is True
 print("NON_REGRESSION_TEST_OK");print("REAL_TCB_OK");print("EXACT_HANDLE_CONSUMPTION_OK");print("NO_AMBIENT_FALLBACK_OK");print("P162G6_METRICS_HTML_REPORT_GENERATOR_2N_ATOMIC_REMEDIATION_TEST_OK")
if __name__=="__main__":main()
