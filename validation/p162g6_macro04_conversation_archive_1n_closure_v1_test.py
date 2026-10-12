from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json

from ontology.conversation_memory_archive import ConversationMemoryArchive
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker

RID="R"; A="A"; E="E"; STAMP="2026-10-07T00:00:00+00:00"
SLOT="p162g6_macro04_conversation_archive_write_replace"

def provider_for(root):
    issued_contexts=[]
    def provider(operation_id,target):
        assert operation_id=="FS_WRITE_REPLACE_BYTES"
        target=Path(target)
        broker=ScopedHandleBroker()
        effector=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=broker)
        rel=target.resolve().relative_to(root.resolve()).as_posix()
        binding=effector.canonical_target(RID,rel)
        lease={"lease_id":"lease-"+target.name,"reservation_id":"res-"+target.name,
               "operation_id":operation_id,"expires_at":"2099-01-01T00:00:00+00:00"}
        claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],
                              adapter_id=A,claim_hash="claim-"+target.name)
        scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
        issued=broker.issue(claim=claim,lease=lease,
            registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,
            authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP)
        assert issued["status"]=="HANDLE_ISSUED"
        ctx=GovernedFilesystemEffectContext(slots={SLOT:[issued["handle"]]},effector=effector,
            root_id=RID,root_path=root,adapter_id=A,effector_id=E)
        issued_contexts.append(ctx)
        return ctx
    return provider,issued_contexts

def main():
    # Degradation: no ambient authority and no write on missing provider.
    with TemporaryDirectory() as td:
        root=Path(td); archive=root/"archive"; archive.mkdir()
        obj=ConversationMemoryArchive(str(archive))
        before=list(archive.iterdir())
        try:
            obj.save_exchange("q","r")
            raise AssertionError("ambient write accepted")
        except RuntimeError as exc:
            assert "filesystem_effect_context_provider_required" in str(exc)
        assert list(archive.iterdir())==before
    print("DEGRADATION_TEST_OK")

    # Functional: real governed effector + exact preissued handle writes valid payload.
    with TemporaryDirectory() as td:
        root=Path(td); archive=root/"archive"; archive.mkdir()
        provider,contexts=provider_for(root)
        obj=ConversationMemoryArchive(str(archive),filesystem_effect_context_provider=provider)
        path=obj.save_exchange("question","réponse")
        payload=json.loads(path.read_text(encoding="utf-8"))
        assert payload["question"]=="question" and payload["response"]=="réponse"
        assert len(contexts)==1 and contexts[0].remaining()=={SLOT:0}
        assert obj.list_archives()==[path.name]
    print("FUNCTIONAL_TEST_OK")
    print("REAL_TCB_OK")
    print("EXACT_HANDLE_CONSUMPTION_OK")

    # Non-regression: step/list behavior remains coherent after governed persistence.
    with TemporaryDirectory() as td:
        root=Path(td); archive=root/"archive"; archive.mkdir()
        provider,_=provider_for(root)
        obj=ConversationMemoryArchive(str(archive),filesystem_effect_context_provider=provider)
        obj.save_exchange("a","b")
        state=obj.step()
        assert state["primitive"]=="conversation_memory_archive"
        assert state["archive_count"]==1
        assert state["persistent_memory_enabled"] is True
    print("NON_REGRESSION_TEST_OK")
    print("P162G6_MACRO04_CONVERSATION_ARCHIVE_1N_TEST_OK")

if __name__=="__main__":
    main()
