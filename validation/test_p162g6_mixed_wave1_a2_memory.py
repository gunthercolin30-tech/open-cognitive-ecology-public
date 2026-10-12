from pathlib import Path
import json
import pytest
from ontology.general_semantic_memory_unified import GeneralSemanticMemoryUnified
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.scoped_handle_broker import ScopedEffectHandle

ROOT_ID="a2root"; ADAPTER="a2adapter"; EFFECTOR="filesystem"
class Broker:
    def __init__(self,ids): self.ids=set(ids); self.used=set()
    def consume_once(self,hid):
        if hid not in self.ids or hid in self.used:return False
        self.used.add(hid);return True
def h(hid,op,target):
    return ScopedEffectHandle(hid,"l","r","c",ADAPTER,EFFECTOR,op,target,"s",ADAPTER,"9999",True,False,False,False)
def ctx(root,parent,file_name,wrong=False):
    hs=[h("c","FS_CREATE_DIR",f"filesystem://{ROOT_ID}/{parent}" if not wrong else f"filesystem://{ROOT_ID}/wrong"),
        h("w","FS_WRITE_REPLACE_BYTES",f"filesystem://{ROOT_ID}/{parent}/{file_name}")]
    b=Broker(["c","w"]); e=GovernedFilesystemEffector(root_registry={ROOT_ID:str(root)},handle_broker=b)
    return GovernedFilesystemEffectContext({"knowledge_parent_create":[hs[0]],"knowledge_write_replace":[hs[1]]},
      effector=e,root_id=ROOT_ID,root_path=root,adapter_id=ADAPTER,effector_id=EFFECTOR)
def obj():
    x=GeneralSemanticMemoryUnified(); x.triples=[{"subject":"a","predicate":"b","object":"c"}]; return x

def test_save_without_context_fails_closed(tmp_path):
    p=tmp_path/"memory"/"semantic.json"
    with pytest.raises(RuntimeError,match="governed_filesystem_effect_context_required"): obj().save_knowledge(p)
    assert not p.exists() and not p.parent.exists()
def test_governed_create_and_replace(tmp_path):
    p=tmp_path/"memory"/"semantic.json"; c=ctx(tmp_path,"memory","semantic.json")
    r=obj().save_knowledge(p,filesystem_effect_context=c)
    assert r["saved"] is True and json.loads(p.read_text(encoding="utf-8"))[0]["subject"]=="a"
    assert c.remaining()=={"knowledge_parent_create":0,"knowledge_write_replace":0}
def test_existing_parent_needs_only_write_handle(tmp_path):
    d=tmp_path/"memory"; d.mkdir(); p=d/"semantic.json"
    wh=h("w","FS_WRITE_REPLACE_BYTES",f"filesystem://{ROOT_ID}/memory/semantic.json")
    b=Broker(["w"]); e=GovernedFilesystemEffector(root_registry={ROOT_ID:str(tmp_path)},handle_broker=b)
    c=GovernedFilesystemEffectContext({"knowledge_write_replace":[wh]},effector=e,root_id=ROOT_ID,root_path=tmp_path,adapter_id=ADAPTER,effector_id=EFFECTOR)
    assert obj().save_knowledge(p,filesystem_effect_context=c)["saved"] is True
def test_wrong_create_target_blocks_before_effect(tmp_path):
    p=tmp_path/"memory"/"semantic.json"; c=ctx(tmp_path,"memory","semantic.json",wrong=True)
    with pytest.raises(RuntimeError,match="target_mismatch"): obj().save_knowledge(p,filesystem_effect_context=c)
    assert not p.parent.exists()
def test_context_replay_rejected(tmp_path):
    p=tmp_path/"memory"/"semantic.json"; c=ctx(tmp_path,"memory","semantic.json")
    obj().save_knowledge(p,filesystem_effect_context=c)
    with pytest.raises(RuntimeError,match="context replay"): obj().save_knowledge(p,filesystem_effect_context=c)
def test_quota_rejection_precedes_authority_requirement(tmp_path,monkeypatch):
    x=obj(); p=tmp_path/"memory"/"semantic.json"; monkeypatch.setattr(x,"_storage_quota_status",lambda _:{"quota_exceeded":True})
    r=x.save_knowledge(p); assert r["saved"] is False and r["reason"]=="quota_exceeded" and not p.exists()
def test_long_term_wrapper_propagates_context(tmp_path):
    p=tmp_path/"memory"/"semantic.json"; c=ctx(tmp_path,"memory","semantic.json")
    r=obj().long_term_knowledge_persistence_step({"action":"save","file_path":str(p),"filesystem_effect_context":c})
    assert r["saved"] is True and r["primitive"]=="LONG_TERM_KNOWLEDGE_PERSISTENCE_ENGINE" and p.exists()
def test_load_remains_read_only_compatible(tmp_path):
    p=tmp_path/"semantic.json"; p.write_text('[{"subject":"x","predicate":"y","object":"z"}]',encoding="utf-8")
    x=GeneralSemanticMemoryUnified(); r=x.load_knowledge(p)
    assert r["loaded"] is True and x.triples[0]["subject"]=="x"
