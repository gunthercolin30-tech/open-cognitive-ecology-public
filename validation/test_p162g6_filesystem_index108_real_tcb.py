from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
from ontology.reflexive_threshold_final_scientific_synthesis import ReflexiveThresholdFinalScientificSynthesis
RID="root";AD="adapter";EF="effector"
def ctx(root,target):
    b=ScopedHandleBroker();binding=GovernedFilesystemEffector.canonical_target(RID,target.relative_to(root).as_posix())
    c=SimpleNamespace(lease_id="lease",reservation_id="reservation",claim_hash="claim-"+target.name,adapter_id=AD)
    lease={"lease_id":"lease","reservation_id":"reservation","operation_id":"FS_WRITE_REPLACE_BYTES","expires_at":"2999-01-01T00:00:00+00:00"}
    reg={"adapter_id":AD,"effector_id":EF};scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
    issued=b.issue(claim=c,lease=lease,registry_entry=reg,requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=AD,now_iso="2026-10-05T00:00:00+00:00")
    assert issued["status"]=="HANDLE_ISSUED",issued
    e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b)
    x=GovernedFilesystemEffectContext(slots={"final_synthesis_html_write":[issued["handle"]]},effector=e,root_id=RID,root_path=root,adapter_id=AD,effector_id=EF);x.begin();return x
def syn():return {"final_reflexive_threshold_status":"REFLEXIVE_THRESHOLD_PARTIAL","final_scientific_confidence":.5,"certification":{"certification_status":"TEST"},"replication_evaluation":{"replication_decision":"TEST"},"functional_scientific_conclusion":"functional conclusion only; phenomenology undetermined."}
with TemporaryDirectory() as td:
    root=Path(td);target=root/"final.html";obj=ReflexiveThresholdFinalScientificSynthesis(root=root)
    try:obj._write_html(target,syn(),fs_context=None);raise AssertionError("missing_context")
    except PermissionError:pass
    assert not target.exists();target.write_text("OLD-CONTENT",encoding="utf-8")
    c=ctx(root,target);obj._write_html(target,syn(),fs_context=c);data=target.read_text(encoding="utf-8")
    assert "OLD-CONTENT" not in data and "phenomenology undetermined" in data and c.remaining()["final_synthesis_html_write"]==0
    try:obj._write_html(target,syn(),fs_context=c);raise AssertionError("replay")
    except RuntimeError:pass
    wrong=root/"wrong.html";cw=ctx(root,wrong)
    try:obj._write_html(target,syn(),fs_context=cw);raise AssertionError("wrong_binding")
    except RuntimeError:pass
    assert not wrong.exists()
print("P162G6_INDEX108_REAL_TCB_OK")
print("EXISTING_TARGET_REPLACE_SEMANTICS_OK")
print("MISSING_CONTEXT_FAIL_CLOSED_OK")
print("REPLAY_FAIL_CLOSED_OK")
print("TARGET_BINDING_FAIL_CLOSED_OK")
print("AUTHORITY_MINTING=false")
print("AMBIENT_FALLBACK=false")
