from __future__ import annotations
import json, shutil, tempfile
from pathlib import Path
from ontology.occ_human_adoption_decision import save_human_decision,save_human_decisions_batch
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.scoped_handle_broker import ScopedEffectHandle
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json"
ORACLE=ROOT/"validation_artifacts/p162/p162g/g6_filesystem_governed_create_temp/cohort8f5a_premigration_oracle_harness_v1.json"
REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_human_adoption_decisions.json")
ADAPTER="8f5a-adapter"; EFFECTOR="filesystem"; RID="8f5a-root"
class Broker:
    def __init__(self,ids): self.ids=set(ids); self.used=set()
    def consume_once(self,hid):
        if hid not in self.ids or hid in self.used:return False
        self.used.add(hid);return True
def handle(hid,op,target):
    return ScopedEffectHandle(hid,"lease","reservation","claim",ADAPTER,EFFECTOR,op,target,"scope",ADAPTER,"9999",True,False,False,False)
def ctx(root,hid):
    target=f"filesystem://{RID}/{REL.as_posix()}"
    h=handle(hid,"FS_WRITE_REPLACE_BYTES",target)
    b=Broker([hid]); e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b)
    return GovernedFilesystemEffectContext({"human_decision_write_replace":[h]},effector=e,root_id=RID,root_path=root,adapter_id=ADAPTER,effector_id=EFFECTOR)
def setup(root):
    p=root/"oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json"
    p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(REG,p)
def ids():
    r=json.loads(REG.read_text());q=sorted(k for k in r["proposals"] if not k.startswith("DNA.L0."))
    assert len(q)>=3;return q[:3]
def oracle(name):
    x=json.loads(ORACLE.read_text());return next(c for c in x["cases"] if c["name"]==name)
with tempfile.TemporaryDirectory(prefix="oce-8f5a-post-") as td:
    r=Path(td).resolve();setup(r);i=ids()
    try:
        save_human_decision(r,i[0],"REJECT","8F5A oracle rejection rationale","oracle-human","principal_investigator",False)
        raise AssertionError("missing context did not fail closed")
    except RuntimeError as e: assert "governed_filesystem_effect_context_required" in str(e)
    assert not (r/REL).exists()
with tempfile.TemporaryDirectory(prefix="oce-8f5a-post-") as td:
    r=Path(td).resolve();setup(r);i=ids()
    q=save_human_decision(r,i[0],"REJECT","8F5A oracle rejection rationale","oracle-human","principal_investigator",False,filesystem_effect_context=ctx(r,"s1"))
    assert q["accepted"] is True and (r/REL).read_bytes().hex()==oracle("valid_single_reject")["decision_file_hex"]
with tempfile.TemporaryDirectory(prefix="oce-8f5a-post-") as td:
    r=Path(td).resolve();setup(r);i=ids()
    ds=[{"canonical_id":i[0],"decision":"REJECT","rationale":"8F5A batch oracle rationale A"},{"canonical_id":i[1],"decision":"REJECT","rationale":"8F5A batch oracle rationale B"}]
    q=save_human_decisions_batch(r,ds,"oracle-human","principal_investigator",False,"CONFIRM HUMAN DECISIONS ONLY",filesystem_effect_context=ctx(r,"b1"))
    assert q["accepted"] is True and (r/REL).read_bytes().hex()==oracle("valid_batch_reject")["decision_file_hex"]
with tempfile.TemporaryDirectory(prefix="oce-8f5a-post-") as td:
    r=Path(td).resolve();setup(r);i=ids()
    ds=[{"canonical_id":i[0],"decision":"REJECT","rationale":"8F5A degradation rationale"}]
    q=save_human_decisions_batch(r,ds,"oracle-human","principal_investigator",False,"")
    assert q=={"accepted":False,"reason":"BATCH_CONFIRMATION_REQUIRED"} and not (r/REL).exists()
with tempfile.TemporaryDirectory(prefix="oce-8f5a-post-") as td:
    r=Path(td).resolve();setup(r);i=ids()
    assert save_human_decision(r,i[0],"REJECT","8F5A seed rationale","oracle-human","principal_investigator",False,filesystem_effect_context=ctx(r,"p1"))["accepted"]
    assert save_human_decision(r,i[1],"REJECT","8F5A replacement rationale","oracle-human","principal_investigator",False,filesystem_effect_context=ctx(r,"p2"))["accepted"]
    assert (r/REL).read_bytes().hex()==oracle("preexisting_workbook_replacement")["decision_file_hex"]
print("P162G6_FILESYSTEM_8F5A_HUMAN_ADOPTION_MIGRATION_V7_TEST=PASSED")
print("ORDINALS=79,80")
print("MISSING_CONTEXT_FAIL_CLOSED=true")
print("BYTE_EXACT_SINGLE=true")
print("BYTE_EXACT_BATCH=true")
print("DEGRADATION_NO_EFFECT=true")
print("BYTE_EXACT_PREEXISTING_REPLACE=true")
print("AUTHORITY_MINTING=0")
print("AMBIENT_AUTHORITY=false")
