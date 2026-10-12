from __future__ import annotations
import ast
from pathlib import Path
import pytest
import ontology.baseline_integrity as m
from ontology.governed_evidence_effect_policy import ALLOW,DENY,EvidenceEffectDecision
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedEffectHandle
class Broker:
 def __init__(self,hs): self.known={h.handle_id for h in hs}; self.used=set()
 def consume_once(self,h):
  if h not in self.known or h in self.used:return False
  self.used.add(h); return True
def H(i,op,t): return ScopedEffectHandle(i,"l","r","c","adapter","filesystem",op,t,"s","adapter","2999",True,False,False,False)
def D(i,op,rel,value=ALLOW): return EvidenceEffectDecision(i,value,"EVIDENCE_REPORT_EXPORT",op,"filesystem://r1/"+rel,"bounded","index7-test")
def C(root,parents=(),target="manifest.json"):
 ph=[H("p"+str(i),"FS_CREATE_DIR","filesystem://r1/"+r) for i,r in enumerate(parents)]; wh=H("w","FS_WRITE_REPLACE_BYTES","filesystem://r1/"+target); hs=ph+[wh]
 return GovernedFilesystemEffectContext(slots={"manifest_parent_create":ph,"manifest_write":[wh]},effector=GovernedFilesystemEffector(root_registry={"r1":str(root)},handle_broker=Broker(hs)),root_id="r1",root_path=root,adapter_id="adapter",effector_id="filesystem")
@pytest.fixture
def manifest(monkeypatch):
 v={"schema":"oce.p007.baseline.v2","functional_only":True,"phenomenology_undetermined":True,"marker":"index7"}; monkeypatch.setattr(m,"build_manifest",lambda:dict(v)); return v
def test_replace(tmp_path,manifest):
 t=tmp_path/"manifest.json"; t.write_text("OLD"); c=C(tmp_path); out=m.write_manifest(t,filesystem_context=c,evidence_decisions={"parent_create":[],"manifest_write":D("d","FS_WRITE_REPLACE_BYTES","manifest.json")}); assert out==manifest and "index7" in t.read_text() and not (tmp_path/"manifest.json.p162g.tmp").exists() and not any(c.remaining().values()) and c.authority_minting is False
def test_parent_chain(tmp_path,manifest):
 t=tmp_path/"a/b/manifest.json"; c=C(tmp_path,("a","a/b"),"a/b/manifest.json"); m.write_manifest(t,filesystem_context=c,evidence_decisions={"parent_create":[D("d1","FS_CREATE_DIR","a"),D("d2","FS_CREATE_DIR","a/b")],"manifest_write":D("d3","FS_WRITE_REPLACE_BYTES","a/b/manifest.json")}); assert t.is_file() and not any(c.remaining().values())
def test_no_context_before_build(tmp_path,monkeypatch):
 called=[]; monkeypatch.setattr(m,"build_manifest",lambda:called.append(1) or {});
 with pytest.raises(RuntimeError,match="governed_filesystem_context_required"): m.write_manifest(tmp_path/"x")
 assert called==[]
def test_cardinality(tmp_path,manifest):
 t=tmp_path/"a/b/m.json"; c=C(tmp_path,("a","a/b"),"a/b/m.json")
 with pytest.raises(RuntimeError,match="cardinality"): m.write_manifest(t,filesystem_context=c,evidence_decisions={"parent_create":[D("p","FS_CREATE_DIR","a")],"manifest_write":D("w","FS_WRITE_REPLACE_BYTES","a/b/m.json")})
 assert not (tmp_path/"a").exists()
def test_deny(tmp_path,manifest):
 t=tmp_path/"m.json"; c=C(tmp_path,target="m.json")
 with pytest.raises(RuntimeError,match="not_confirmed"): m.write_manifest(t,filesystem_context=c,evidence_decisions={"parent_create":[],"manifest_write":D("x","FS_WRITE_REPLACE_BYTES","m.json",DENY)})
 assert not t.exists()
def test_binding_mismatch(tmp_path,manifest):
 t=tmp_path/"m.json"; c=C(tmp_path,target="m.json")
 with pytest.raises(RuntimeError,match="target_mismatch"): m.write_manifest(t,filesystem_context=c,evidence_decisions={"parent_create":[],"manifest_write":D("x","FS_WRITE_REPLACE_BYTES","other.json")})
 assert not t.exists()
def test_missing_handle(tmp_path,manifest):
 t=tmp_path/"m.json"; c=C(tmp_path,target="m.json"); c._queues["manifest_write"].clear()
 with pytest.raises(RuntimeError,match="no remaining handle"): m.write_manifest(t,filesystem_context=c,evidence_decisions={"parent_create":[],"manifest_write":D("x","FS_WRITE_REPLACE_BYTES","m.json")})
 assert not t.exists()
def test_replay(tmp_path,manifest):
 t=tmp_path/"m.json"; c=C(tmp_path,target="m.json"); m.write_manifest(t,filesystem_context=c,evidence_decisions={"parent_create":[],"manifest_write":D("x","FS_WRITE_REPLACE_BYTES","m.json")})
 with pytest.raises(RuntimeError,match="context replay"): m.write_manifest(t,filesystem_context=c,evidence_decisions={"parent_create":[],"manifest_write":D("y","FS_WRITE_REPLACE_BYTES","m.json")})
def test_outside_root(tmp_path,manifest):
 root=tmp_path/"root"; root.mkdir(); t=tmp_path/"outside.json"; c=C(root,target="outside.json")
 with pytest.raises(RuntimeError,match="outside_root"): m.write_manifest(t,filesystem_context=c,evidence_decisions={"parent_create":[],"manifest_write":D("x","FS_WRITE_REPLACE_BYTES","outside.json")})
 assert not t.exists()
def test_no_direct_bypass():
 tr=ast.parse(Path(m.__file__).read_text()); fn=next(n for n in tr.body if isinstance(n,ast.FunctionDef) and n.name=="write_manifest"); bad=[]
 for n in ast.walk(fn):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in {"write_text","write_bytes","open","mkdir","replace","rename","unlink"}: bad.append((n.lineno,n.func.attr))
 assert bad==[]
