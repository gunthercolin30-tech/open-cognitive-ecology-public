from pathlib import Path
import ast

def test_index2_consumer_has_no_direct_mutator_in_rollback_boundary():
    p=Path("ontology/acee_installation_executor.py"); tree=ast.parse(p.read_text())
    fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=="_rollback_after_local_validation_failure")
    calls=[]
    for n in ast.walk(fn):
        if isinstance(n,ast.Call):
            try: calls.append(ast.unparse(n.func))
            except Exception: pass
    forbidden={"path.unlink","path.write_bytes","path.parent.mkdir","self._fsync_directory","self._append_journal_record"}
    assert not (forbidden & set(calls))
    text=ast.get_source_segment(p.read_text(),fn)
    for token in ("FS_REMOVE_FILE","FS_WRITE_REPLACE_BYTES","_append_journal_record_governed","filesystem_effect_context_provider=self.filesystem_effect_context_provider"):
        assert token in text

def test_index2_delegated_acee11_has_governed_single_target_restore_and_persistence():
    text=Path("ontology/acee_rollback_engine.py").read_text()
    for token in ("filesystem_effect_context_provider", "p162g6_index2_acee11_restore_copy2", "p162g6_index2_acee11_history_append", "p162g6_index2_acee11_latest_replace"):
        assert token in text


def test_index2_functional_existing_target_full_governed_path():
    import hashlib
    from datetime import datetime, timezone
    from tempfile import TemporaryDirectory
    from types import SimpleNamespace
    from ontology.acee_installation_executor import AceeInstallationExecutor
    from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
    from ontology.governed_filesystem_effector import GovernedFilesystemEffector
    from ontology.scoped_handle_broker import ScopedHandleBroker
    with TemporaryDirectory() as td:
        root=Path(td).resolve(); (root/"ontology").mkdir()
        tx=root/"acee6_transactions"/"tx1"; tx.mkdir(parents=True)
        inventory=root/"ontology_inventory.txt"; inventory.write_bytes(b"changed\n")
        target=root/"ontology"/"candidate.py"; backup=root/"ontology"/"candidate.py.bak"
        target.write_bytes(b"mutated\n"); backup.write_bytes(b"original\n")
        before_hash=hashlib.sha256(b"original\n").hexdigest()
        (tx/"inventory_snapshot_manifest.json").write_text(
            __import__("json").dumps({"files":[{"path":"ontology_inventory.txt","existed_before":True,"before_hex":b"before\n".hex()}]}),
            encoding="utf-8",
        )
        (tx/"backup_manifest.json").write_text(
            __import__("json").dumps({"target_path":"ontology/candidate.py","target_existed_before":True,"backup_path":"ontology/candidate.py.bak","backup_sha256":before_hash,"target_sha256_before":before_hash}),
            encoding="utf-8",
        )
        (tx/"latest_state.json").write_text("{}",encoding="utf-8")
        broker=ScopedHandleBroker(); adapter="p162g6-index2-test"; effector_id="p162g6-filesystem-effector"; root_id="repo"
        eff=GovernedFilesystemEffector(root_registry={root_id:str(root)},handle_broker=broker); counter=[0]
        slots={
          "FS_CREATE_DIR":["p162g6_index2_acee11_parent_create","p162g6_index2_inventory_parent_create","p162g6_index2_journal_parent_create","p162g6_c02_parent_create"],
          "FS_WRITE_BYTES":["p162g6_index2_acee11_lock_create"],
          "FS_WRITE_REPLACE_BYTES":["p162g6_index2_inventory_restore","p162g6_index2_acee11_latest_replace","p162g6_c02_write_replace"],
          "FS_REMOVE_FILE":["p162g6_index2_inventory_remove","p162g6_index2_target_remove"],
          "FS_APPEND_BYTES":["p162g6_index2_acee11_history_append","p162g6_index2_journal_append"],
          "FS_COPY2":["p162g6_index2_acee11_restore_copy2"],
        }
        def provider(operation_id,destination):
            counter[0]+=1; destination=Path(destination).resolve()
            dr=destination.relative_to(root).as_posix()
            if operation_id=="FS_COPY2":
                source=backup.resolve(); sr=source.relative_to(root).as_posix()
                binding={"source":f"filesystem://{root_id}/{sr}","destination":f"filesystem://{root_id}/{dr}"}
            else:
                binding=f"filesystem://{root_id}/{dr}"
            claim=SimpleNamespace(lease_id=f"lease-{counter[0]}",reservation_id=f"res-{counter[0]}",claim_hash=f"claim-{counter[0]}",adapter_id=adapter)
            lease={"lease_id":claim.lease_id,"reservation_id":claim.reservation_id,"operation_id":operation_id,"expires_at":"2999-01-01T00:00:00Z"}
            scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
            issued=broker.issue(claim=claim,lease=lease,registry_entry={"adapter_id":adapter,"effector_id":effector_id},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=adapter,now_iso="2026-10-05T00:00:00Z")
            assert issued["status"]=="HANDLE_ISSUED"
            return GovernedFilesystemEffectContext(slots={name:[issued["handle"]] for name in slots[operation_id]},effector=eff,root_id=root_id,root_path=root,adapter_id=adapter,effector_id=effector_id)
        engine=AceeInstallationExecutor(filesystem_effect_context_provider=provider,root=root,now_utc=datetime(2026,10,5,tzinfo=timezone.utc))
        result=engine._rollback_after_local_validation_failure(
            tx,{"transaction_id":"tx1","proposal_id":"p1","normalized_plan":{"target_path":"ontology/candidate.py"}},"functional_test_failure"
        )
        assert result["transaction_state"]=="ROLLED_BACK"
        assert result["inventory_rollback_succeeded"] is True and inventory.read_bytes()==b"before\n"
        assert result["target_rollback_succeeded"] is True and target.read_bytes()==b"original\n"
        assert result["rollback_result"]["persisted"] is True
        assert (root/"acee_runtime"/"ACEE11_acee_rollback_engine"/"rollback_history.jsonl").is_file()
        assert (tx/"journal.jsonl").is_file()
