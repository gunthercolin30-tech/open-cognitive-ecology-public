from pathlib import Path
import ast, hashlib, inspect, textwrap
from ontology.acee_rollback_engine import AceeRollbackEngine, STATUS_FAILED

def _request(root, destination, backup):
    return {
        "rollback_request": {
            "reason": "explicit_governed_request",
            "transaction_id": "e2-degradation",
            "targets": [{
                "destination": str(destination.relative_to(root)),
                "backup": str(backup.relative_to(root)),
                "expected_backup_sha256": hashlib.sha256(backup.read_bytes()).hexdigest(),
            }],
        },
        "governance_authorization": True,
        "constitutional_authorization": True,
        "dry_run": False,
        "execute": True,
        "timestamp_utc": "2026-10-06T00:00:00Z",
    }

def test_execute_without_provider_fails_closed_without_mutation(tmp_path):
    root=tmp_path.resolve()
    destination=root/"ontology"/"candidate.py"
    backup=root/"ontology"/"candidate.py.bak"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"mutated\n")
    backup.write_bytes(b"original\n")
    before_destination=destination.read_bytes()
    before_backup=backup.read_bytes()
    result=AceeRollbackEngine(root=root).step(_request(root,destination,backup),persist=False)
    assert result["rollback_status"]==STATUS_FAILED
    assert result["rollback_performed"] is False
    assert result["restored_count"]==0
    assert result["failure"]=="governed_filesystem_effect_context_provider_required"
    assert destination.read_bytes()==before_destination
    assert backup.read_bytes()==before_backup
    assert not list(destination.parent.glob("*.acee11.*"))

def test_dry_run_without_provider_remains_non_mutating_and_ready(tmp_path):
    root=tmp_path.resolve()
    destination=root/"ontology"/"candidate.py"
    backup=root/"ontology"/"candidate.py.bak"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"mutated\n")
    backup.write_bytes(b"original\n")
    request=_request(root,destination,backup)
    request["execute"]=False
    request["dry_run"]=True
    before=destination.read_bytes()
    result=AceeRollbackEngine(root=root).step(request,persist=False)
    assert result["rollback_ready"] is True
    assert result["rollback_performed"] is False
    assert destination.read_bytes()==before

def test_restore_contains_no_direct_filesystem_mutator_fallback():
    source=textwrap.dedent(inspect.getsource(AceeRollbackEngine._restore))
    tree=ast.parse(source)
    calls=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            try: calls.append(ast.unparse(node.func))
            except Exception: pass
    forbidden={
        "destination.parent.mkdir","tempfile.mkstemp","shutil.copy2",
        "os.replace","tmp.unlink","candidate.unlink",
    }
    assert not (forbidden & set(calls))
    assert "governed_filesystem_effect_context_provider_required" in source
    assert "execute_copy2" in source
