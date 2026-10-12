from pathlib import Path
from types import SimpleNamespace
import ast
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.preventive_growth_producer_routing import PreventiveGrowthProducerRouting
from ontology.residual_local_producer_router import ResidualLocalProducerRouter
import ontology.preventive_growth_producer_routing as pm, ontology.residual_local_producer_router as rm
class Broker:
 def __init__(self,ids):self.ids=set(ids);self.used=set()
 def consume_once(self,x):
  if x not in self.ids or x in self.used:return False
  self.used.add(x);return True
def H(i,op,b):return SimpleNamespace(handle_id=i,adapter_id="a",effector_id="e",operation_id=op,target_binding=b,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
def B(r,p):return "filesystem://"+r+"/"+p
def report_ctx(root,rid,base,state,hist):
 br=Broker({"d","s","h"});ef=GovernedFilesystemEffector(root_registry={rid:str(root)},handle_broker=br)
 return GovernedFilesystemEffectContext(slots={"producer_report_dir_create":[H("d","FS_CREATE_DIRS",B(rid,base.relative_to(root).as_posix()))],"producer_report_state_replace":[H("s","FS_WRITE_REPLACE_BYTES",B(rid,state.relative_to(root).as_posix()))],"producer_report_history_append":[H("h","FS_APPEND_BYTES",B(rid,hist.relative_to(root).as_posix()))]},effector=ef,root_id=rid,root_path=root,adapter_id="a",effector_id="e")
def test_verify_probe_governed(tmp_path):
 root=tmp_path/"repo";ssd=tmp_path/"ssd";root.mkdir();ssd.mkdir();dest=ssd/"OCE_MEMORY/preventive_growth/data";dest.mkdir(parents=True);(root/"data").symlink_to(dest,target_is_directory=True);probe=dest/"f17_8_verify_data.json"
 class Provider:
  def __call__(self,op,target,source=None):
   br=Broker({"p"});ef=GovernedFilesystemEffector(root_registry={"ssd":str(ssd)},handle_broker=br);return GovernedFilesystemEffectContext(slots={"p162g6_postv3_verify_probe_replace":[H("p","FS_WRITE_REPLACE_BYTES",B("ssd",probe.relative_to(ssd).as_posix()))]},effector=ef,root_id="ssd",root_path=ssd,adapter_id="a",effector_id="e")
 out=PreventiveGrowthProducerRouting(root=root,ssd_root=ssd,filesystem_effect_context_provider=Provider())._verify_only("data",True);assert out["verified"] and probe.is_file()
def test_verify_missing_authority_no_probe(tmp_path):
 root=tmp_path/"repo";ssd=tmp_path/"ssd";root.mkdir();ssd.mkdir();dest=ssd/"OCE_MEMORY/preventive_growth/data";dest.mkdir(parents=True);(root/"data").symlink_to(dest,target_is_directory=True)
 out=PreventiveGrowthProducerRouting(root=root,ssd_root=ssd)._verify_only("data",True);assert not out["verified"] and "governed_filesystem_effect_context_provider_required" in out["error"];assert not (dest/"f17_8_verify_data.json").exists()
def test_residual_step_missing_report_authority_before_mutation(tmp_path):
 root=tmp_path/"repo";ssd=tmp_path/"ssd";root.mkdir();ssd.mkdir();src=root/"metrics";src.mkdir();r=ResidualLocalProducerRouter(root=root,ssd_root=ssd)
 try:r.step({"dry_run":False,"producer_dirs":["metrics"],"backup_paths":{"metrics":str(root/"metrics.pre_f17_4_local_backup_X")}})
 except PermissionError:pass
 else:raise AssertionError
 assert src.is_dir() and not src.is_symlink() and not r._route_target("metrics").exists()
def test_residual_dryrun_report_governed(tmp_path):
 root=tmp_path/"repo";ssd=tmp_path/"ssd";root.mkdir();ssd.mkdir();(root/"metrics").mkdir();r=ResidualLocalProducerRouter(root=root,ssd_root=ssd);p=r._report_paths();ctx=report_ctx(ssd,"ssd",p["base"],p["state"],p["history"]);out=r.step({"dry_run":True,"producer_dirs":["metrics"]},report_fs_context=ctx);assert out["dry_run"] and p["state"].is_file() and p["history"].is_file()
def test_no_direct_ambient_writes_targeted():
 for m,cname,names in ((pm,"PreventiveGrowthProducerRouting",("_verify_only","step")),(rm,"ResidualLocalProducerRouter",("step",))):
  t=ast.parse(Path(m.__file__).read_text());c=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name==cname)
  for name in names:
   f=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name==name);a=[n.func.attr for n in ast.walk(f) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)];assert not any(x in a for x in ("write_text","write_bytes","mkdir","open"))
