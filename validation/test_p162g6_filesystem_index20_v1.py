from pathlib import Path
from types import SimpleNamespace
import ast
import tempfile

from ontology.governed_evidence_effect_policy import ALLOW, DENY, EvidenceEffectDecision, GovernedEvidenceEffectPolicy
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
import ontology.consciousness_explanation_engine as mod


class Broker:
    def __init__(self, ids):
        self.ids=set(ids); self.used=set()
    def consume_once(self, handle_id):
        if handle_id not in self.ids or handle_id in self.used:
            return False
        self.used.add(handle_id); return True


def handle(hid, op, binding):
    return SimpleNamespace(
        handle_id=hid, adapter_id="adapter", effector_id="effector",
        operation_id=op, target_binding=binding,
        ambient_authority=False, transferable=False, child_inheritance=False,
        single_use=True,
    )


def decision(did, role, op, binding, allow=True):
    return EvidenceEffectDecision(
        decision_id=did, decision=ALLOW if allow else DENY,
        evidence_role=role, operation_id=op, target_binding=binding,
        rationale="bounded AS16 markdown persistence",
        provenance="P162-G6 index20 exact migration",
        authorization_inference=False, implementation_authorized=False,
    )


def governance(root, target, parent_count, write_allow=True, wrong_write=False):
    root=Path(root).resolve(); target=Path(target)
    missing=mod._missing_parent_chain(target.parent)
    assert len(missing)==parent_count
    handles=[]; pdec=[]
    for i,p in enumerate(missing):
        rel=p.resolve().relative_to(root).as_posix()
        binding="filesystem://testroot/"+rel
        hid="p%d"%i
        handles.append(handle(hid,"FS_CREATE_DIR",binding))
        pdec.append(decision("pd%d"%i,"consciousness_explanation_markdown_parent","FS_CREATE_DIR",binding))
    rel=target.resolve().relative_to(root).as_posix()
    actual_binding="filesystem://testroot/"+rel
    decision_binding="filesystem://testroot/wrong.md" if wrong_write else actual_binding
    handles.append(handle("w","FS_WRITE_REPLACE_BYTES",actual_binding))
    wdec=decision("wd","consciousness_explanation_markdown","FS_WRITE_REPLACE_BYTES",decision_binding,write_allow)
    broker=Broker([h.handle_id for h in handles])
    eff=GovernedFilesystemEffector(root_registry={"testroot":str(root)},handle_broker=broker)
    ctx=GovernedFilesystemEffectContext(
        slots={
            "markdown_parent_create":[h for h in handles if h.operation_id=="FS_CREATE_DIR"],
            "markdown_write":[h for h in handles if h.operation_id=="FS_WRITE_REPLACE_BYTES"],
        },
        effector=eff, root_id="testroot", root_path=root,
        adapter_id="adapter", effector_id="effector",
    )
    ctx.begin()
    bridge=GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),ctx)
    return bridge,{"parent_create":pdec,"write":wdec},ctx


PAYLOAD={
    "timestamp_utc":"2026-10-05T00:00:00Z",
    "current_state":"FUNCTIONAL_ONLY",
    "explanation_status":"READY",
    "explanation_text":"Functional explanation.",
    "modules":[],"missing_conditions":[],"countermodels":[],
}


def test_missing_governance_fails_before_mutation():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); target=root/"a"/"b"/"report.md"
        try: mod._write_markdown(target,PAYLOAD)
        except PermissionError: pass
        else: raise AssertionError("missing governance accepted")
        assert not (root/"a").exists()


def test_missing_parent_chain_and_write_are_governed():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); target=root/"a"/"b"/"report.md"
        bridge,decs,ctx=governance(root,target,2)
        mod._write_markdown(target,PAYLOAD,bridge,decs)
        assert target.is_file()
        assert "Functional conclusion only" in target.read_text(encoding="utf-8")
        assert ctx.remaining()["markdown_parent_create"]==0
        assert ctx.remaining()["markdown_write"]==0
        assert bridge.authority_minting is False


def test_existing_parent_requires_no_parent_authority_and_replaces():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); target=parent/"report.md"
        target.write_text("OLD",encoding="utf-8")
        bridge,decs,ctx=governance(root,target,0)
        mod._write_markdown(target,PAYLOAD,bridge,decs)
        assert target.read_text(encoding="utf-8")!="OLD"
        assert ctx.remaining()["markdown_write"]==0


def test_parent_decision_cardinality_fails_before_effect():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); target=root/"a"/"b"/"report.md"
        bridge,decs,ctx=governance(root,target,2)
        decs["parent_create"]=decs["parent_create"][:1]
        try: mod._write_markdown(target,PAYLOAD,bridge,decs)
        except RuntimeError as e: assert "cardinality_mismatch" in str(e)
        else: raise AssertionError("bad cardinality accepted")
        assert not (root/"a").exists()
        assert ctx.remaining()["markdown_parent_create"]==2
        assert ctx.remaining()["markdown_write"]==1


def test_write_deny_preserves_existing_target():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); target=parent/"report.md"
        target.write_text("OLD",encoding="utf-8")
        bridge,decs,ctx=governance(root,target,0,write_allow=False)
        try: mod._write_markdown(target,PAYLOAD,bridge,decs)
        except PermissionError: pass
        else: raise AssertionError("DENY accepted")
        assert target.read_text(encoding="utf-8")=="OLD"
        assert ctx.remaining()["markdown_write"]==1


def test_target_binding_mismatch_preserves_existing_target():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); target=parent/"report.md"
        target.write_text("OLD",encoding="utf-8")
        bridge,decs,ctx=governance(root,target,0,wrong_write=True)
        try: mod._write_markdown(target,PAYLOAD,bridge,decs)
        except RuntimeError as e: assert "target_mismatch" in str(e)
        else: raise AssertionError("target mismatch accepted")
        assert target.read_text(encoding="utf-8")=="OLD"
        assert ctx.remaining()["markdown_write"]==1


def test_replay_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); target=parent/"report.md"
        bridge,decs,ctx=governance(root,target,0)
        mod._write_markdown(target,PAYLOAD,bridge,decs)
        first=target.read_bytes()
        try: mod._write_markdown(target,PAYLOAD,bridge,decs)
        except RuntimeError: pass
        else: raise AssertionError("replay accepted")
        assert target.read_bytes()==first


def test_outside_root_fails_closed():
    with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as out:
        root=Path(td); outside=Path(out); target=outside/"report.md"
        # Build a valid bridge rooted inside root; target is outside and must fail before dispatch.
        inside=root/"inside.md"; bridge,decs,ctx=governance(root,inside,0)
        try: mod._write_markdown(target,PAYLOAD,bridge,decs)
        except RuntimeError as e: assert "outside governed root" in str(e)
        else: raise AssertionError("outside-root target accepted")
        assert not target.exists()


def test_static_no_ambient_markdown_mutators_and_step_transport():
    source=Path(mod.__file__).read_text(encoding="utf-8")
    tree=ast.parse(source)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_write_markdown")
    attrs=[n.func.attr for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert "mkdir" not in attrs and "write_text" not in attrs and "write_bytes" not in attrs and "open" not in attrs
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="ConsciousnessExplanationEngine")
    step=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="step")
    calls=[n for n in ast.walk(step) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="_write_markdown"]
    assert len(calls)==2
    for call in calls:
        assert len(call.args)==4
        assert isinstance(call.args[2],ast.Name) and call.args[2].id=="evidence_bridge"
