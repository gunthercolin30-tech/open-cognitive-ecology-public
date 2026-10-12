from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import ast
import json
import tempfile

from ontology.governed_evidence_effect_policy import ALLOW, DENY, EvidenceEffectDecision, GovernedEvidenceEffectPolicy
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
import ontology.occ_compiled_normative_profile_closing_transaction as mod


class Broker:
    def __init__(self, ids):
        self.ids=set(ids); self.used=set()
    def consume_once(self, handle_id):
        if handle_id not in self.ids or handle_id in self.used:
            return False
        self.used.add(handle_id); return True


def handle(hid,op,binding):
    return SimpleNamespace(handle_id=hid,adapter_id="adapter",effector_id="effector",
        operation_id=op,target_binding=binding,ambient_authority=False,transferable=False,
        child_inheritance=False,single_use=True)


def decision(did,role,op,binding,allow=True):
    return EvidenceEffectDecision(decision_id=did,decision=ALLOW if allow else DENY,
        evidence_role=role,operation_id=op,target_binding=binding,
        rationale="bounded OCC1E closing artifact persistence",
        provenance="P162-G6 index71 exact migration",
        authorization_inference=False,implementation_authorized=False)


def governance(root,out,parent_count,write_allow=True,wrong_write=False):
    root=Path(root).resolve(); out=Path(out)
    missing=mod._missing_parent_chain(out.parent); assert len(missing)==parent_count
    handles=[]; pdec=[]
    for i,p in enumerate(missing):
        rel=p.resolve().relative_to(root).as_posix(); binding="filesystem://testroot/"+rel
        handles.append(handle("p%d"%i,"FS_CREATE_DIR",binding))
        pdec.append(decision("pd%d"%i,"occ1e_closing_artifact_parent","FS_CREATE_DIR",binding))
    rel=out.resolve().relative_to(root).as_posix(); binding="filesystem://testroot/"+rel
    handles.append(handle("w","FS_WRITE_REPLACE_BYTES",binding))
    wdec=decision("wd","occ1e_closing_artifact","FS_WRITE_REPLACE_BYTES",
                  "filesystem://testroot/wrong.json" if wrong_write else binding,write_allow)
    broker=Broker([h.handle_id for h in handles])
    eff=GovernedFilesystemEffector(root_registry={"testroot":str(root)},handle_broker=broker)
    ctx=GovernedFilesystemEffectContext(
        slots={"occ1e_closing_parent_create":[h for h in handles if h.operation_id=="FS_CREATE_DIR"],
               "occ1e_closing_write":[h for h in handles if h.operation_id=="FS_WRITE_REPLACE_BYTES"]},
        effector=eff,root_id="testroot",root_path=root,adapter_id="adapter",effector_id="effector")
    ctx.begin()
    return GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),ctx),{"parent_create":pdec,"write":wdec},ctx


def closed_result():
    return {"occ1e_closed":True,"checks":{"x":True},"transaction_id":"tx-test"}


def test_missing_governance_fails_before_mutation():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); out=root/"a"/"b"/"close.json"
        with patch.object(mod,"evaluate",return_value=closed_result()), patch.object(mod,"_paths",return_value={"output":out}):
            try: mod.commit(root)
            except PermissionError: pass
            else: raise AssertionError("missing governance accepted")
        assert not (root/"a").exists()


def test_parent_chain_and_write_are_governed():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); out=root/"a"/"b"/"close.json"
        bridge,decs,ctx=governance(root,out,2)
        with patch.object(mod,"evaluate",return_value=closed_result()), patch.object(mod,"_paths",return_value={"output":out}):
            result=mod.commit(root,bridge,decs)
        assert result["transaction_id"]=="tx-test"
        assert json.loads(out.read_text(encoding="utf-8"))["transaction_id"]=="tx-test"
        assert ctx.remaining()["occ1e_closing_parent_create"]==0 and ctx.remaining()["occ1e_closing_write"]==0


def test_identical_existing_artifact_is_replaced_governedly():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); out=parent/"close.json"
        content=json.dumps(closed_result(),indent=2,sort_keys=True)+"\n"; out.write_text(content,encoding="utf-8")
        bridge,decs,ctx=governance(root,out,0)
        with patch.object(mod,"evaluate",return_value=closed_result()), patch.object(mod,"_paths",return_value={"output":out}):
            mod.commit(root,bridge,decs)
        assert out.read_text(encoding="utf-8")==content
        assert ctx.remaining()["occ1e_closing_write"]==0


def test_divergent_existing_artifact_rejected_before_authority_consumption():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); out=parent/"close.json"; out.write_text("DIVERGENT",encoding="utf-8")
        bridge,decs,ctx=governance(root,out,0)
        with patch.object(mod,"evaluate",return_value=closed_result()), patch.object(mod,"_paths",return_value={"output":out}):
            try: mod.commit(root,bridge,decs)
            except RuntimeError as e: assert "EXISTING_CLOSURE_ARTIFACT_DIVERGES" in str(e)
            else: raise AssertionError("divergent artifact accepted")
        assert out.read_text(encoding="utf-8")=="DIVERGENT"
        assert ctx.remaining()["occ1e_closing_write"]==1


def test_parent_decision_cardinality_fails_before_mutation():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); out=root/"a"/"b"/"close.json"; bridge,decs,ctx=governance(root,out,2)
        decs["parent_create"]=decs["parent_create"][:1]
        with patch.object(mod,"evaluate",return_value=closed_result()), patch.object(mod,"_paths",return_value={"output":out}):
            try: mod.commit(root,bridge,decs)
            except RuntimeError as e: assert "CARDINALITY_MISMATCH" in str(e)
            else: raise AssertionError("bad cardinality accepted")
        assert not (root/"a").exists()


def test_write_deny_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); out=parent/"close.json"
        bridge,decs,ctx=governance(root,out,0,write_allow=False)
        with patch.object(mod,"evaluate",return_value=closed_result()), patch.object(mod,"_paths",return_value={"output":out}):
            try: mod.commit(root,bridge,decs)
            except PermissionError: pass
            else: raise AssertionError("DENY accepted")
        assert not out.exists() and ctx.remaining()["occ1e_closing_write"]==1


def test_target_binding_mismatch_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); out=parent/"close.json"
        bridge,decs,ctx=governance(root,out,0,wrong_write=True)
        with patch.object(mod,"evaluate",return_value=closed_result()), patch.object(mod,"_paths",return_value={"output":out}):
            try: mod.commit(root,bridge,decs)
            except RuntimeError as e: assert "target_mismatch" in str(e)
            else: raise AssertionError("target mismatch accepted")
        assert not out.exists()


def test_replay_fails_closed_without_second_write():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); parent=root/"a"; parent.mkdir(); out=parent/"close.json"
        bridge,decs,ctx=governance(root,out,0)
        with patch.object(mod,"evaluate",return_value=closed_result()), patch.object(mod,"_paths",return_value={"output":out}):
            mod.commit(root,bridge,decs); first=out.read_bytes()
            try: mod.commit(root,bridge,decs)
            except RuntimeError: pass
            else: raise AssertionError("replay accepted")
        assert out.read_bytes()==first


def test_static_no_ambient_mutators_in_commit():
    source=Path(mod.__file__).read_text(encoding="utf-8"); tree=ast.parse(source)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="commit")
    attrs=[n.func.attr for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert "mkdir" not in attrs and "write_text" not in attrs and "write_bytes" not in attrs and "open" not in attrs
