from pathlib import Path
import json,pytest
import ontology.metrics_statistical_significance_engine as m
from ontology.governed_evidence_effect_policy import ALLOW,DENY,EvidenceEffectDecision
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedEffectHandle
class B:
 def __init__(self,hs):self.k={h.handle_id for h in hs};self.u=set()
 def consume_once(self,x):
  if x not in self.k or x in self.u:return False
  self.u.add(x);return True
def H(i,o,t):return ScopedEffectHandle(i,"l","r","c","a","filesystem",o,t,"s","a","2999-01-01T00:00:00Z")
def D(i,o,r,v=ALLOW):return EvidenceEffectDecision(i,v,m.P162G6_EVIDENCE_ROLE,o,"filesystem://r1/"+r,"index57 bounded evidence effect",__file__)
def C(root,parents=()):
 hs=[];ph=[]
 for i,r in enumerate(parents):h=H("p"+str(i),"FS_CREATE_DIR","filesystem://r1/"+r);hs.append(h);ph.append(h)
 oh=H("out","FS_WRITE_REPLACE_BYTES","filesystem://r1/metrics/metrics_statistical_significance_summary.json");sh=H("state","FS_WRITE_REPLACE_BYTES","filesystem://r1/metrics/metrics_statistical_significance_engine_state.json");hs += [oh,sh]
 return GovernedFilesystemEffectContext(slots={"metrics_parent_create":ph,"significance_summary_write":[oh],"significance_state_write":[sh]},effector=GovernedFilesystemEffector(root_registry={"r1":str(root)},handle_broker=B(hs)),root_id="r1",root_path=root,adapter_id="a",effector_id="filesystem")
def DS(parents=(),out=ALLOW,state=ALLOW):return {"parent_create":[D("pD"+str(i),"FS_CREATE_DIR",r) for i,r in enumerate(parents)],"output_write":D("oD","FS_WRITE_REPLACE_BYTES","metrics/metrics_statistical_significance_summary.json",out),"state_write":D("sD","FS_WRITE_REPLACE_BYTES","metrics/metrics_statistical_significance_engine_state.json",state)}
def E(root,mp):
 e=m.MetricsStatisticalSignificanceEngine(root=root);mp.setattr(e,"_load_json",lambda p:{"aggregations":{}});mp.setattr(e,"_load_records",lambda:[]);mp.setattr(e,"_utc_now",lambda:"2026-10-05T09:00:00Z");return e
def test_two_independent_writes(tmp_path,monkeypatch):
 (tmp_path/"metrics").mkdir();e=E(tmp_path,monkeypatch);c=C(tmp_path);r=e.step(filesystem_context=c,evidence_decisions=DS());assert r["error_count"]==0;assert e.output_path.is_file() and e.state_path.is_file();assert not any(c.remaining().values());assert c.authority_minting is False
def test_replace_existing(tmp_path,monkeypatch):
 (tmp_path/"metrics").mkdir();e=E(tmp_path,monkeypatch);e.output_path.write_text("old");e.state_path.write_text("old");e.step(filesystem_context=C(tmp_path),evidence_decisions=DS());assert e.output_path.read_text()!="old" and e.state_path.read_text()!="old"
def test_missing_parent_governed(tmp_path,monkeypatch):
 e=E(tmp_path,monkeypatch);e.step(filesystem_context=C(tmp_path,("metrics",)),evidence_decisions=DS(("metrics",)));assert e.output_path.is_file() and e.state_path.is_file()
def test_missing_context_fails_closed(tmp_path,monkeypatch):
 e=E(tmp_path,monkeypatch)
 with pytest.raises(RuntimeError,match="governed_filesystem_context_required"):e.step()
 assert not (tmp_path/"metrics").exists()
def test_cardinality_fails_before_effect(tmp_path,monkeypatch):
 e=E(tmp_path,monkeypatch)
 with pytest.raises(RuntimeError,match="cardinality"):e.step(filesystem_context=C(tmp_path,("metrics",)),evidence_decisions=DS())
 assert not (tmp_path/"metrics").exists()
def test_first_deny_blocks_both(tmp_path,monkeypatch):
 (tmp_path/"metrics").mkdir();e=E(tmp_path,monkeypatch)
 with pytest.raises(RuntimeError,match="not_confirmed"):e.step(filesystem_context=C(tmp_path),evidence_decisions=DS(out=DENY))
 assert not e.output_path.exists() and not e.state_path.exists()
def test_second_deny_blocks_second_only(tmp_path,monkeypatch):
 (tmp_path/"metrics").mkdir();e=E(tmp_path,monkeypatch)
 with pytest.raises(RuntimeError,match="not_confirmed"):e.step(filesystem_context=C(tmp_path),evidence_decisions=DS(state=DENY))
 assert e.output_path.is_file() and not e.state_path.exists()
def test_target_binding_fails_closed(tmp_path,monkeypatch):
 (tmp_path/"metrics").mkdir();e=E(tmp_path,monkeypatch);d=DS();d["output_write"]=D("bad","FS_WRITE_REPLACE_BYTES","metrics/wrong.json")
 with pytest.raises(RuntimeError,match="target_mismatch"):e.step(filesystem_context=C(tmp_path),evidence_decisions=d)
 assert not e.output_path.exists()
def test_replay_fails_closed(tmp_path,monkeypatch):
 (tmp_path/"metrics").mkdir();e=E(tmp_path,monkeypatch);c=C(tmp_path);e.step(filesystem_context=c,evidence_decisions=DS())
 with pytest.raises(RuntimeError,match="context replay"):e.step(filesystem_context=c,evidence_decisions=DS())
def test_outside_root_fails_closed(tmp_path,monkeypatch):
 root=tmp_path/"root";root.mkdir();(root/"metrics").mkdir();e=E(root,monkeypatch);e.output_path=tmp_path/"outside.json"
 with pytest.raises(RuntimeError,match="outside_root"):e.step(filesystem_context=C(root),evidence_decisions=DS())
 assert not e.output_path.exists()
