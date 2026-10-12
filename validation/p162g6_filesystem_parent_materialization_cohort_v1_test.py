from pathlib import Path
from types import SimpleNamespace
import ast,pytest,inspect,textwrap
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
import ontology.dna_versioning_lineage as lineage
import ontology.documentary_relation_classifier as doc
import ontology.interaction_graph as ig
import ontology.occ_constitutional_compilation_transaction as cct
import ontology.occ_initial_development_authority_materialization as ida
import ontology.occ_institutional_authority_amendment_dossier as iad
import ontology.occ_normative_ir_closing_transaction as nir
class Broker:
 def __init__(self,ids):self.ids=set(ids);self.used=set()
 def consume_once(self,x):
  if x not in self.ids or x in self.used:return False
  self.used.add(x);return True
def H(i,op,b):return SimpleNamespace(handle_id=i,adapter_id="a",effector_id="e",operation_id=op,target_binding=b,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
def C(root,target,ps,ws,parent=True):
 slots={ws:[H("w","FS_WRITE_REPLACE_BYTES","filesystem://r/"+target.relative_to(root).as_posix())]};ids={"w"}
 if parent:slots[ps]=[H("p","FS_CREATE_DIRS","filesystem://r/"+target.parent.relative_to(root).as_posix())];ids.add("p")
 c=GovernedFilesystemEffectContext(slots=slots,effector=GovernedFilesystemEffector(root_registry={"r":str(root)},handle_broker=Broker(ids)),root_id="r",root_path=root,adapter_id="a",effector_id="e");c.begin();return c
CASES=[("lineage","lineage_parent_create","lineage_write_replace"),("doc","relation_candidates_parent_create","relation_candidates_write_replace"),("ig","interaction_graph_parent_create","interaction_graph_write_replace"),("cct","constitutional_profile_parent_create","constitutional_profile_write_replace"),("ida","human_inputs_parent_create","human_inputs_write_replace"),("iad","human_inputs_parent_create","human_inputs_write_replace"),("nir","normative_ir_parent_create","normative_ir_write_replace")]
def invoke(k,t,c):
 if k=="lineage":lineage.save_lineage(t,lineage.create_lineage("e",lineage.INDIVIDUAL,"D",provenance="t"),c)
 elif k=="doc":doc._atomic(t,{"x":1},c,"relation_candidates_write_replace")
 elif k=="ig":ig.InteractionGraph._atomic(t,{"x":1},c)
 elif k=="cct":cct._atomic_json(t,{"x":1},c,"constitutional_profile_write_replace")
 elif k in ("ida","iad"):
  m=ida if k=="ida" else iad;ov,op=m.validate,m.path
  try:m.validate=lambda x:{"status":"READY"};m.path=lambda root=None:t;m.save_human_inputs({},t.parents[1],c)
  finally:m.validate,m.path=ov,op
 else:nir._atomic_write(t,{"x":1},c)
@pytest.mark.parametrize("k,ps,ws",CASES)
def test_governed_parent_and_write(tmp_path,k,ps,ws):
 root=tmp_path/"r";root.mkdir();t=root/"new"/"a.json";c=C(root,t,ps,ws);invoke(k,t,c);assert t.is_file();assert c.remaining()=={ws:0,ps:0}
@pytest.mark.parametrize("k,ps,ws",CASES)
def test_missing_parent_authority_fails_before_mutation(tmp_path,k,ps,ws):
 root=tmp_path/"r";root.mkdir();t=root/"new"/"a.json";c=C(root,t,ps,ws,False)
 with pytest.raises(KeyError):invoke(k,t,c)
 assert not t.parent.exists();assert c.remaining()=={ws:1}
def test_no_ambient_parent_mkdir():
 for obj,name in [(lineage,"save_lineage"),(doc,"_atomic"),(ig.InteractionGraph,"_atomic"),(cct,"_atomic_json"),(ida,"save_human_inputs"),(iad,"save_human_inputs"),(nir,"_atomic_write")]:
  tr=ast.parse(textwrap.dedent(inspect.getsource(getattr(obj,name))));attrs=[n.func.attr for n in ast.walk(tr) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)];assert "mkdir" not in attrs
