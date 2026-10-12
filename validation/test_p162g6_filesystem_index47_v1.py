from pathlib import Path
from types import SimpleNamespace
import ast
import json
import tempfile

from ontology.governed_evidence_effect_policy import ALLOW, DENY, EvidenceEffectDecision, GovernedEvidenceEffectPolicy
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
import ontology.inter_individual_coordination_protocol as mod


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
        operation_id=op, target_binding=binding, ambient_authority=False,
        transferable=False, child_inheritance=False, single_use=True,
    )


def decision(did, role, op, binding, allow=True):
    return EvidenceEffectDecision(
        decision_id=did, decision=ALLOW if allow else DENY, evidence_role=role,
        operation_id=op, target_binding=binding,
        rationale="bounded coordination history persistence",
        provenance="P162-G6 index47 exact migration",
        authorization_inference=False, implementation_authorized=False,
    )


def governance(root, target, parent_count, include_trim=False, append_allow=True, trim_allow=True, wrong_append=False):
    root=Path(root).resolve(); target=Path(target)
    missing=mod._missing_parent_chain(target.parent)
    assert len(missing)==parent_count
    handles=[]; pdec=[]
    for i,p in enumerate(missing):
        rel=p.resolve().relative_to(root).as_posix(); binding="filesystem://testroot/"+rel; hid="p%d"%i
        handles.append(handle(hid,"FS_CREATE_DIR",binding))
        pdec.append(decision("pd%d"%i,"inter_individual_coordination_history_parent","FS_CREATE_DIR",binding))
    rel=target.resolve().relative_to(root).as_posix(); binding="filesystem://testroot/"+rel
    handles.append(handle("a","FS_APPEND_BYTES",binding))
    adec=decision("ad","inter_individual_coordination_history_append","FS_APPEND_BYTES",
                  "filesystem://testroot/wrong.jsonl" if wrong_append else binding,append_allow)
    tdec=None
    if include_trim:
        handles.append(handle("t","FS_WRITE_REPLACE_BYTES",binding))
        tdec=decision("td","inter_individual_coordination_history_trim","FS_WRITE_REPLACE_BYTES",binding,trim_allow)
    broker=Broker([h.handle_id for h in handles])
    eff=GovernedFilesystemEffector(root_registry={"testroot":str(root)},handle_broker=broker)
    ctx=GovernedFilesystemEffectContext(
        slots={
            "coordination_history_parent_create":[h for h in handles if h.operation_id=="FS_CREATE_DIR"],
            "coordination_history_append":[h for h in handles if h.operation_id=="FS_APPEND_BYTES"],
            "coordination_history_trim":[h for h in handles if h.operation_id=="FS_WRITE_REPLACE_BYTES"],
        },
        effector=eff,root_id="testroot",root_path=root,adapter_id="adapter",effector_id="effector",
    )
    ctx.begin()
    bridge=GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),ctx)
    return bridge,{"parent_create":pdec,"append":adec,"trim":tdec},ctx


def test_missing_governance_returns_false_without_mutation():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); target=root/"a"/"history.jsonl"
        assert mod._append_jsonl(target,{"x":1}) is False
        assert not (root/"a").exists()


def test_parent_chain_and_append_are_governed():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); target=root/"a"/"b"/"history.jsonl"
        bridge,decs,ctx=governance(root,target,2)
        assert mod._append_jsonl(target,{"x":1},evidence_bridge=bridge,evidence_decisions=decs) is True
        assert json.loads(target.read_text(encoding="utf-8"))=={"x":1}
        assert ctx.remaining()["coordination_history_parent_create"]==0
        assert ctx.remaining()["coordination_history_append"]==0


def test_existing_history_appends_without_replacing_prior_line():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); target=parent/"history.jsonl"
        target.write_text('{"old":true}\n',encoding="utf-8")
        bridge,decs,ctx=governance(root,target,0)
        assert mod._append_jsonl(target,{"new":True},evidence_bridge=bridge,evidence_decisions=decs) is True
        lines=target.read_text(encoding="utf-8").splitlines()
        assert len(lines)==2 and json.loads(lines[0])=={"old":True} and json.loads(lines[1])=={"new":True}


def test_rotation_is_governed_replace_and_keeps_last_max_lines():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); target=parent/"history.jsonl"
        target.write_text('{"n":1}\n{"n":2}\n',encoding="utf-8")
        bridge,decs,ctx=governance(root,target,0,include_trim=True)
        assert mod._append_jsonl(target,{"n":3},max_lines=2,evidence_bridge=bridge,evidence_decisions=decs) is True
        vals=[json.loads(x)["n"] for x in target.read_text(encoding="utf-8").splitlines()]
        assert vals==[2,3]
        assert ctx.remaining()["coordination_history_trim"]==0


def test_missing_trim_authority_preserves_confirmed_append_without_ambient_truncate():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); target=parent/"history.jsonl"
        target.write_text('{"n":1}\n{"n":2}\n',encoding="utf-8")
        bridge,decs,ctx=governance(root,target,0,include_trim=False)
        assert mod._append_jsonl(target,{"n":3},max_lines=2,evidence_bridge=bridge,evidence_decisions=decs) is True
        assert [json.loads(x)["n"] for x in target.read_text(encoding="utf-8").splitlines()]==[1,2,3]


def test_append_deny_preserves_existing_history():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); target=parent/"history.jsonl"
        target.write_text("OLD\n",encoding="utf-8")
        bridge,decs,ctx=governance(root,target,0,append_allow=False)
        assert mod._append_jsonl(target,{"x":1},evidence_bridge=bridge,evidence_decisions=decs) is False
        assert target.read_text(encoding="utf-8")=="OLD\n"
        assert ctx.remaining()["coordination_history_append"]==1


def test_target_binding_mismatch_preserves_existing_history():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); target=parent/"history.jsonl"
        target.write_text("OLD\n",encoding="utf-8")
        bridge,decs,ctx=governance(root,target,0,wrong_append=True)
        assert mod._append_jsonl(target,{"x":1},evidence_bridge=bridge,evidence_decisions=decs) is False
        assert target.read_text(encoding="utf-8")=="OLD\n"


def test_replay_fails_closed_without_second_append():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); target=parent/"history.jsonl"
        bridge,decs,ctx=governance(root,target,0)
        assert mod._append_jsonl(target,{"x":1},evidence_bridge=bridge,evidence_decisions=decs) is True
        first=target.read_bytes()
        assert mod._append_jsonl(target,{"x":2},evidence_bridge=bridge,evidence_decisions=decs) is False
        assert target.read_bytes()==first


def test_static_no_ambient_mutators_and_step_transport():
    source=Path(mod.__file__).read_text(encoding="utf-8"); tree=ast.parse(source)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_append_jsonl")
    attrs=[n.func.attr for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert "mkdir" not in attrs and "open" not in attrs and "write_text" not in attrs and "write_bytes" not in attrs
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="InterIndividualCoordinationProtocol")
    step=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="step")
    calls=[n for n in ast.walk(step) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="_append_jsonl"]
    assert len(calls)==1
    kws={k.arg:k.value for k in calls[0].keywords}
    assert isinstance(kws["evidence_bridge"],ast.Name) and kws["evidence_bridge"].id=="evidence_bridge"
    assert isinstance(kws["evidence_decisions"],ast.Name) and kws["evidence_decisions"].id=="history_evidence_decisions"
