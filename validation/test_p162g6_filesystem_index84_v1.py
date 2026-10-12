from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import ast
import json
import tempfile

from ontology.governed_evidence_effect_policy import (
    ALLOW, DENY, EvidenceEffectDecision, GovernedEvidenceEffectPolicy,
)
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
import ontology.occ_normative_ir_closing_transaction as mod


class Broker:
    def __init__(self, allowed):
        self.allowed=set(allowed); self.used=set()
    def consume_once(self, handle_id):
        if handle_id not in self.allowed or handle_id in self.used:
            return False
        self.used.add(handle_id); return True


def handle(hid,target):
    return SimpleNamespace(
        handle_id=hid, adapter_id="adapter", effector_id="effector",
        operation_id="FS_REMOVE_FILE", target_binding=target,
        ambient_authority=False, transferable=False, child_inheritance=False,
        single_use=True,
    )


def bridge_and_decision(root, rel="artifact.json", allow=True):
    binding="filesystem://testroot/"+rel
    broker=Broker({"h1"})
    eff=GovernedFilesystemEffector(root_registry={"testroot":str(root)},handle_broker=broker)
    ctx=GovernedFilesystemEffectContext(
        slots={"normative_ir_rollback_remove":[handle("h1",binding)]},
        effector=eff, root_id="testroot", root_path=root,
        adapter_id="adapter", effector_id="effector",
    )
    ctx.begin()
    bridge=GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),ctx)
    decision=EvidenceEffectDecision(
        decision_id="d1",
        decision=ALLOW if allow else DENY,
        evidence_role="normative_ir_closing_artifact_rollback",
        operation_id="FS_REMOVE_FILE",
        target_binding=binding,
        rationale="bounded rollback of invalid closing artifact",
        provenance="P162-G6 index84 exact migration",
        authorization_inference=False,
        implementation_authorized=False,
    )
    return bridge,decision,ctx


def test_governed_rollback_remove_success():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); p=root/"artifact.json"; p.write_text("x",encoding="utf-8")
        bridge,decision,ctx=bridge_and_decision(root)
        assert mod._rollback_remove(p,bridge,decision) is True
        assert not p.exists()
        assert ctx.remaining()["normative_ir_rollback_remove"]==0
        assert bridge.authority_minting is False


def test_missing_governance_fails_closed_without_removal():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); p=root/"artifact.json"; p.write_text("x",encoding="utf-8")
        assert mod._rollback_remove(p,None,None) is False
        assert p.read_text(encoding="utf-8")=="x"


def test_deny_fails_closed_without_removal():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); p=root/"artifact.json"; p.write_text("x",encoding="utf-8")
        bridge,decision,ctx=bridge_and_decision(root,allow=False)
        assert mod._rollback_remove(p,bridge,decision) is False
        assert p.exists()
        assert ctx.remaining()["normative_ir_rollback_remove"]==1


def test_target_binding_mismatch_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); p=root/"artifact.json"; p.write_text("x",encoding="utf-8")
        bridge,decision,ctx=bridge_and_decision(root,rel="wrong.json")
        assert mod._rollback_remove(p,bridge,decision) is False
        assert p.exists()
        assert ctx.remaining()["normative_ir_rollback_remove"]==1


def test_outside_root_fails_closed():
    with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as out:
        root=Path(td); p=Path(out)/"artifact.json"; p.write_text("x",encoding="utf-8")
        bridge,decision,ctx=bridge_and_decision(root)
        assert mod._rollback_remove(p,bridge,decision) is False
        assert p.exists()
        assert ctx.remaining()["normative_ir_rollback_remove"]==1


def test_replay_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); p=root/"artifact.json"; p.write_text("x",encoding="utf-8")
        bridge,decision,ctx=bridge_and_decision(root)
        assert mod._rollback_remove(p,bridge,decision) is True
        p.write_text("new",encoding="utf-8")
        assert mod._rollback_remove(p,bridge,decision) is False
        assert p.read_text(encoding="utf-8")=="new"


def test_close_unreadable_persisted_artifact_uses_governed_rollback():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); target=root/"artifact.json"
        bridge,decision,ctx=bridge_and_decision(root)
        audit_result={"status":mod.PASS,"decision":"READY_TO_CLOSE","report":{
            "requirements_total":27,"satisfied_count":25,"bounded_count":2,
            "missing_count":0,"bounded_requirements":["C08","C09"]},
            "report_sha256":"a"*64}
        def bad_write(path,obj,filesystem_effect_context=None):
            path.write_bytes(b"{not-json")
        with patch.object(mod.auditmod,"audit",return_value=audit_result), \
             patch.object(mod,"_source_identity",return_value={"x":"y"}), \
             patch.object(mod,"_atomic_write",side_effect=bad_write):
            result=mod.close(root,target,filesystem_effect_context=object(),
                             filesystem_effect_bridge=bridge,
                             rollback_evidence_decision=decision)
        assert result["reason"]=="PERSISTED_ARTIFACT_UNREADABLE_ROLLBACK"
        assert not target.exists()
        assert ctx.remaining()["normative_ir_rollback_remove"]==0


def test_close_without_rollback_authority_never_ambiently_deletes():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); target=root/"artifact.json"
        audit_result={"status":mod.PASS,"decision":"READY_TO_CLOSE","report":{
            "requirements_total":27,"satisfied_count":25,"bounded_count":2,
            "missing_count":0,"bounded_requirements":["C08","C09"]},
            "report_sha256":"a"*64}
        def bad_write(path,obj,filesystem_effect_context=None):
            path.write_bytes(b"{not-json")
        with patch.object(mod.auditmod,"audit",return_value=audit_result), \
             patch.object(mod,"_source_identity",return_value={"x":"y"}), \
             patch.object(mod,"_atomic_write",side_effect=bad_write):
            result=mod.close(root,target,filesystem_effect_context=object())
        assert result["reason"]=="PERSISTED_ARTIFACT_UNREADABLE_ROLLBACK"
        assert target.exists(), "missing governance must not trigger ambient deletion"


def test_close_contains_no_direct_unlink_and_exact_three_governed_calls():
    source=Path(mod.__file__).read_text(encoding="utf-8")
    tree=ast.parse(source)
    close_fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="close")
    attrs=[n.func.attr for n in ast.walk(close_fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert "unlink" not in attrs
    rollback_calls=[n for n in ast.walk(close_fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="_rollback_remove"]
    assert len(rollback_calls)==3
