from pathlib import Path
from hashlib import sha256
from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.scoped_handle_broker import ScopedEffectHandle
from ontology import occ_constitutional_adversarial_crown_h7 as h7
from ontology import occ_independent_constitutional_verifier as verifier
from ontology import occ_independent_constitutional_verification_report as verifier_report
class _Broker:
 def __init__(self): self.issued=set(); self.used=set()
 def add(self,h): self.issued.add(h.handle_id); return h
 def consume_once(self,hid):
  if hid not in self.issued or hid in self.used:return False
  self.used.add(hid);return True
def _handle(broker,operation,target,seq):
 hid=sha256((operation+repr(target)+str(seq)).encode()).hexdigest()
 return broker.add(ScopedEffectHandle(hid,"lease","reservation","claim","h7-adapter","filesystem-effector",operation,target,"scope","h7-adapter","2999-01-01T00:00:00Z"))
def _dest_binding(rid,parent,path):
 rel=Path(path).resolve().relative_to(Path(parent).resolve()).as_posix(); return GovernedFilesystemEffector.canonical_target(rid,rel)
def _copy_binding(rid,parent,dst,root,src):
 return {"source":GovernedFilesystemEffector.canonical_target("repo",Path(src).resolve().relative_to(Path(root).resolve()).as_posix()),"destination":_dest_binding(rid,parent,dst)}
def _make_lease(root,i):
 root=Path(root).resolve(); coverage_rel=verifier.paths(root)["occ1d_coverage"].resolve().relative_to(root)
 ctx=BoundedFilesystemValidationContext(prefix="oce-p162g6-h7-"); parent=ctx.root.parent.resolve(); rid="h7sb"+str(i); broker=_Broker()
 slots={"sandbox_cleanup":[]}
 eff=GovernedFilesystemEffector(root_registry={rid:str(parent),"repo":str(root)},handle_broker=broker)
 slots["sandbox_cleanup"].append(_handle(broker,"FS_REMOVE_TREE",_dest_binding(rid,parent,ctx.root),0))
 if i==4:
  dst=ctx.root/"repo"/coverage_rel; slots["a072_remove"]=[_handle(broker,"FS_REMOVE_FILE",_dest_binding(rid,parent,dst),1)]
 if i==6:
  sb=ctx.root/"repo"; vp=sb/"ontology/occ_independent_constitutional_verifier.py"; incumbent=Path(verifier.__file__).resolve()
  if incumbent.suffix==".pyc" and incumbent.with_suffix(".py").is_file(): incumbent=incumbent.with_suffix(".py")
  parent_rels=set()
  for rel in list(h7.A075_V1_BINDING_INPUTS)+list(h7.A075_IMPORT_CLOSURE)+["ontology/occ_independent_constitutional_verifier.py"]:
   par=Path(rel).parent
   while str(par) not in ("","."):
    parent_rels.add(par.as_posix()); par=par.parent
  parent_slots={}
  for n,rel in enumerate(sorted(parent_rels,key=lambda x:(len(Path(x).parts),x))):
   slot="a075_parent_"+sha256(rel.encode()).hexdigest()[:16]
   parent_slots[rel]=slot
   slots[slot]=[_handle(broker,"FS_CREATE_DIR",_dest_binding(rid,parent,sb/rel),100+n)]
  slots["a075_verifier_copy"]=[_handle(broker,"FS_COPY2",_copy_binding(rid,parent,vp,root,incumbent),3)]
  slots["a075_binding_copy"]=[]
  for j,rel in enumerate(h7.A075_V1_BINDING_INPUTS):
   src=root/rel; dst=sb/rel; slots["a075_binding_copy"].append(_handle(broker,"FS_COPY2",_copy_binding(rid,parent,dst,root,src),20+j))
  slots["a075_verifier_write"]=[_handle(broker,"FS_WRITE_REPLACE_BYTES",_dest_binding(rid,parent,vp),40)]
  slots["a075_closure_copy"]=[]
  k=0
  for rel in h7.A075_IMPORT_CLOSURE:
   if rel=="ontology/occ_independent_constitutional_verifier.py": continue
   src=root/rel; dst=sb/rel; slots["a075_closure_copy"].append(_handle(broker,"FS_COPY2",_copy_binding(rid,parent,dst,root,src),50+k)); k+=1
  child=sb/"a075_loaded_v2_probe.py"; slots["a075_child_write"]=[_handle(broker,"FS_WRITE_REPLACE_BYTES",_dest_binding(rid,parent,child),90)]
 fctx=GovernedFilesystemEffectContext(slots=slots,effector=eff,root_id=rid,root_path=parent,adapter_id="h7-adapter",effector_id="filesystem-effector")
 return {"context":ctx,"filesystem_context":fctx,"parent_slots":parent_slots if i==6 else {},"cleaned":False}
def make_h7_leases(root): return [_make_lease(root,i) for i in range(7)]
def run_h7(root):
 leases=make_h7_leases(root)
 try: return h7.run(Path(root).resolve(),sandbox_leases=leases)
 finally:
  for lease in leases:
   if lease.get("cleaned") is True: continue
   fctx=lease["filesystem_context"]
   if not fctx._begun: fctx.begin()
   h7._cleanup(lease)
