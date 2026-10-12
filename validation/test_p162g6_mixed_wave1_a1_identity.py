from __future__ import annotations
from pathlib import Path
import builtins, types
import pytest
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.scoped_handle_broker import ScopedEffectHandle
from ontology.civilizational_identity_preservation import CivilizationalIdentityPreservation
from ontology.continuity_metrics_engine import ContinuityMetricsEngine
from ontology.identity_continuity_index import IdentityContinuityIndex
ADAPTER="a1-adapter"; EFFECTOR="filesystem"; ROOT_ID="test-root"
class Broker:
    def __init__(self, ids): self.ids=set(ids); self.used=set()
    def consume_once(self,hid):
        if hid not in self.ids or hid in self.used: return False
        self.used.add(hid); return True
def handle(hid,op,target): return ScopedEffectHandle(hid,"l","r","c",ADAPTER,EFFECTOR,op,target,"s",ADAPTER,"9999",True,False,False,False)
def context(root,state_dir,state_name,hist_name,wrong=False):
    hs=[handle("h1","FS_CREATE_DIR",f"filesystem://{ROOT_ID}/{state_dir.name}" if not wrong else f"filesystem://{ROOT_ID}/wrong"),handle("h2","FS_WRITE_REPLACE_BYTES",f"filesystem://{ROOT_ID}/{state_dir.name}/{state_name}"),handle("h3","FS_APPEND_BYTES",f"filesystem://{ROOT_ID}/{state_dir.name}/{hist_name}")]
    broker=Broker([h.handle_id for h in hs]); eff=GovernedFilesystemEffector(root_registry={ROOT_ID:str(root)},handle_broker=broker)
    return GovernedFilesystemEffectContext({"state_dir_create":[hs[0]],"state_write_replace":[hs[1]],"history_append":[hs[2]]},effector=eff,root_id=ROOT_ID,root_path=root,adapter_id=ADAPTER,effector_id=EFFECTOR)
@pytest.mark.parametrize("cls,state_name,hist_name",[(CivilizationalIdentityPreservation,"civilizational_identity_preservation.json","civilizational_identity_preservation_history.jsonl"),(ContinuityMetricsEngine,"continuity_metrics_engine.json","continuity_metrics_engine_history.jsonl")])
def test_constructor_pure_and_dry_run(tmp_path,cls,state_name,hist_name):
    d=tmp_path/"state"; obj=cls(state_dir=d); assert not d.exists(); out=obj.step(dry_run=True); assert out["dry_run"] is True; assert not d.exists()
@pytest.mark.parametrize("cls",[CivilizationalIdentityPreservation,ContinuityMetricsEngine])
def test_persistence_without_context_fails_closed(tmp_path,cls):
    d=tmp_path/"state"; obj=cls(state_dir=d)
    with pytest.raises(RuntimeError,match="governed_filesystem_effect_context_required"): obj.step()
    assert not d.exists()
@pytest.mark.parametrize("cls,state_name,hist_name",[(CivilizationalIdentityPreservation,"civilizational_identity_preservation.json","civilizational_identity_preservation_history.jsonl"),(ContinuityMetricsEngine,"continuity_metrics_engine.json","continuity_metrics_engine_history.jsonl")])
def test_governed_create_replace_append(tmp_path,cls,state_name,hist_name):
    d=tmp_path/"state"; ctx=context(tmp_path,d,state_name,hist_name); out=cls(state_dir=d).step(filesystem_effect_context=ctx); assert out["dry_run"] is False; assert (d/state_name).is_file(); assert (d/hist_name).is_file(); assert ctx.remaining()=={"state_dir_create":0,"state_write_replace":0,"history_append":0}
def test_wrong_target_fails_before_effect(tmp_path):
    d=tmp_path/"state"; ctx=context(tmp_path,d,"civilizational_identity_preservation.json","civilizational_identity_preservation_history.jsonl",wrong=True)
    with pytest.raises(RuntimeError,match="target_mismatch"): CivilizationalIdentityPreservation(state_dir=d).step(filesystem_effect_context=ctx)
    assert not d.exists()
def test_context_replay_rejected(tmp_path):
    d=tmp_path/"state"; ctx=context(tmp_path,d,"civilizational_identity_preservation.json","civilizational_identity_preservation_history.jsonl"); CivilizationalIdentityPreservation(state_dir=d).step(filesystem_effect_context=ctx)
    with pytest.raises(RuntimeError,match="context replay"): CivilizationalIdentityPreservation(state_dir=d).step(filesystem_effect_context=ctx)
def test_identity_discovery_for_a1_is_dry_run(monkeypatch):
    seen=[]; real_import=builtins.__import__; targets={"civilizational_identity_preservation":"CivilizationalIdentityPreservation","continuity_metrics_engine":"ContinuityMetricsEngine"}
    class Fake:
        def step(self,*a,**kw): seen.append(dict(kw)); return {"functional":True}
    def imp(name,globals=None,locals=None,fromlist=(),level=0):
        leaf=name.rsplit(".",1)[-1]
        if leaf in targets: return types.SimpleNamespace(**{targets[leaf]:Fake})
        if name.startswith("ontology."): raise ImportError(name)
        return real_import(name,globals,locals,fromlist,level)
    monkeypatch.setattr(builtins,"__import__",imp); out=IdentityContinuityIndex()._collect_identity_modules({}); assert set(out)==set(targets); assert seen==[{"dry_run":True},{"dry_run":True}]
