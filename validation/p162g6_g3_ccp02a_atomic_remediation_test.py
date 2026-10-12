from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.best_explanation_status_resolver import BestExplanationStatusResolver
from ontology.refusal_cost_reporter import RefusalCostReporter
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R"; A="A"; E="E"; STAMP="2026-10-07T00:00:00+00:00"
SLOTS=[("persist_parent_create","FS_CREATE_DIRS","out_dir"),("persist_json_snapshot","FS_WRITE_REPLACE_BYTES","json_path"),("persist_json_latest","FS_WRITE_REPLACE_BYTES","latest_json_path"),("persist_markdown_snapshot","FS_WRITE_REPLACE_BYTES","markdown_path"),("persist_markdown_latest","FS_WRITE_REPLACE_BYTES","latest_markdown_path"),("persist_prometheus_snapshot","FS_WRITE_REPLACE_BYTES","prometheus_path"),("persist_prometheus_latest","FS_WRITE_REPLACE_BYTES","latest_prometheus_path"),("persist_history_append","FS_APPEND_BYTES","history_path")]
def context(root,plan):
 b=ScopedHandleBroker(); e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b); slots={}
 for i,(slot,op,key) in enumerate(SLOTS):
  target=Path(plan["out_dir"] if key=="out_dir" else plan["paths"][key]); rel=target.resolve().relative_to(root.resolve()).as_posix(); binding=e.canonical_target(RID,rel)
  lease={"lease_id":f"l{i}","reservation_id":f"r{i}","operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"}; claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash=f"c{i}")
  scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}; x=b.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP); assert x["status"]=="HANDLE_ISSUED",x; slots[slot]=[x["handle"]]
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
def inputs():
 c={"consciousness_proven":False,"qualia_proven":False,"subjectivity_proven":False,"phenomenology_undetermined":True,"functional_conclusion_only":True}
 return {"aq1":{**c,"taxonomy_initialized":True,"refusal_taxonomy":[{}]},"aq2":{**c,"cost_analysis_completed":True,"rival_theory_costs":[]},"aq3":{**c,"extra_entity_detection_completed":True,"phenomenal_extra_entities":[]},"aq4":{**c,"penalty_check_completed":True,"no_difference_penalties":[]},"aq5":{**c,"minimal_property_denial_check_completed":True,"minimal_property_denials":[]},"aq6":{**c,"rival_explanatory_cost_completed":True,"rival_explanatory_costs":[]},"ap10":{**c,"rf_star_status":"RF_STAR_VALIDATED"}}
def run(cls,inp):
 with TemporaryDirectory() as td:
  root=Path(td); o=cls(root=root); p=o.plan_persistence(STAMP); assert p["operation_cardinality"]=={"FS_CREATE_DIRS":1,"FS_WRITE_REPLACE_BYTES":6,"FS_APPEND_BYTES":1}; ctx=context(root,p); r=o.step(inputs=inp,persist=True,effect_context=ctx,persistence_plan=p); assert all(v==0 for v in ctx.remaining().values()); assert all(Path(x).exists() for x in p["paths"].values()); return r
def main():
 i=inputs(); a7=run(BestExplanationStatusResolver,i); j=dict(i); j["aq7"]=a7; run(RefusalCostReporter,j); print("FUNCTIONAL_TEST_OK")
 with TemporaryDirectory() as td:
  root=Path(td); o=BestExplanationStatusResolver(root=root); p=o.plan_persistence(STAMP)
  try:o.step(inputs=i,persist=True,persistence_plan=p);raise AssertionError("ambient fallback")
  except RuntimeError as x: assert "governed filesystem effect context required" in str(x)
  c=context(root,p); c._queues["persist_json_latest"].clear()
  try:o.step(inputs=i,persist=True,effect_context=c,persistence_plan=p);raise AssertionError("cardinality loss")
  except RuntimeError as x: assert "slot cardinality mismatch" in str(x)
  assert not o.out_dir.exists()
 print("DEGRADATION_TEST_OK")
 r=BestExplanationStatusResolver().step(inputs=i,persist=False); j=dict(i);j["aq7"]=r; q=RefusalCostReporter().step(inputs=j,persist=False)
 for x in (r,q): assert x["consciousness_proven"] is False and x["functional_conclusion_only"] is True and x["phenomenology_undetermined"] is True
 print("NON_REGRESSION_TEST_OK\nREAL_TCB_OK\nEXACT_HANDLE_CONSUMPTION_OK\nP162G6_G3_CCP02A_ATOMIC_REMEDIATION_TEST_OK")
if __name__=="__main__":main()
