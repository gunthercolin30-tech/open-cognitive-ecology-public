from pathlib import Path
from types import SimpleNamespace
import ast,tempfile
from ontology.governed_filesystem_effector import GovernedFilesystemEffector,FilesystemEffectRequest
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_evidence_effect_policy import ALLOW,DENY,EvidenceEffectDecision,GovernedEvidenceEffectPolicy
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
from ontology import occ_constitutional_adversarial_crown_h8 as h8

class Broker:
 def __init__(self,hid): self.hid=hid; self.used=False
 def consume_once(self,hid):
  if self.used or hid!=self.hid:return False
  self.used=True;return True

def setup(root,target,allow=True,wrong=False):
 root=Path(root).resolve(); target=Path(target).resolve(); rid="r"; binding="filesystem://r/"+target.relative_to(root).as_posix(); hid="h"
 handle=SimpleNamespace(handle_id=hid,adapter_id="a",effector_id="e",operation_id="FS_REMOVE_TREE",
  target_binding=binding,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
 broker=Broker(hid); eff=GovernedFilesystemEffector(root_registry={rid:str(root)},handle_broker=broker)
 ctx=GovernedFilesystemEffectContext(slots={"h8_sandbox_cleanup":[handle]},effector=eff,root_id=rid,root_path=root,adapter_id="a",effector_id="e");ctx.begin()
 bridge=GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),ctx)
 dec=EvidenceEffectDecision(decision_id="d",decision=ALLOW if allow else DENY,evidence_role="occ1h_h8_validation_sandbox_cleanup",
  operation_id="FS_REMOVE_TREE",target_binding=("filesystem://r/wrong" if wrong else binding),rationale="test",provenance="test",
  authorization_inference=False,implementation_authorized=False)
 return bridge,dec,ctx

def test_remove_tree_nominal_real_tcb():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td); target=root/"s"; (target/"a").mkdir(parents=True); (target/"a"/"x").write_text("x")
  bridge,dec,ctx=setup(root,target)
  r=bridge.execute_path(decision=dec,evidence_role="occ1h_h8_validation_sandbox_cleanup",slot="h8_sandbox_cleanup",operation_id="FS_REMOVE_TREE",path="s")
  assert r["status"]=="EVIDENCE_EFFECT_CONFIRMED" and not target.exists() and ctx.remaining()["h8_sandbox_cleanup"]==0

def test_remove_tree_deny_no_effect_handle_unconsumed():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td); target=root/"s"; target.mkdir(); bridge,dec,ctx=setup(root,target,allow=False)
  r=bridge.execute_path(decision=dec,evidence_role="occ1h_h8_validation_sandbox_cleanup",slot="h8_sandbox_cleanup",operation_id="FS_REMOVE_TREE",path="s")
  assert r["status"]=="DENIED" and target.exists() and ctx.remaining()["h8_sandbox_cleanup"]==1

def test_remove_tree_target_mismatch_no_effect():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td); target=root/"s"; target.mkdir(); bridge,dec,ctx=setup(root,target,wrong=True)
  try: bridge.execute_path(decision=dec,evidence_role="occ1h_h8_validation_sandbox_cleanup",slot="h8_sandbox_cleanup",operation_id="FS_REMOVE_TREE",path="s")
  except RuntimeError: pass
  else: raise AssertionError("mismatch accepted")
  assert target.exists() and ctx.remaining()["h8_sandbox_cleanup"]==1

def test_remove_tree_symlink_blocked():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td); outside=root/"outside"; outside.mkdir(); link=root/"s"; link.symlink_to(outside,target_is_directory=True)
  bridge,dec,ctx=setup(root,link)
  try: bridge.execute_path(decision=dec,evidence_role="occ1h_h8_validation_sandbox_cleanup",slot="h8_sandbox_cleanup",operation_id="FS_REMOVE_TREE",path="s")
  except RuntimeError as e: assert ("target_symlink_forbidden" in str(e) or "target_mismatch" in str(e))
  else: raise AssertionError("symlink accepted")
  assert link.is_symlink() and outside.exists()

def test_remove_tree_replay_fails_closed():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td); target=root/"s"; target.mkdir(); bridge,dec,ctx=setup(root,target)
  bridge.execute_path(decision=dec,evidence_role="occ1h_h8_validation_sandbox_cleanup",slot="h8_sandbox_cleanup",operation_id="FS_REMOVE_TREE",path="s")
  target.mkdir()
  try: bridge.execute_path(decision=dec,evidence_role="occ1h_h8_validation_sandbox_cleanup",slot="h8_sandbox_cleanup",operation_id="FS_REMOVE_TREE",path="s")
  except RuntimeError: pass
  else: raise AssertionError("replay accepted")
  assert target.exists()

def test_h8_missing_governance_fails_before_sandbox():
 try: h8.run(Path("."),sandbox_leases=None)
 except PermissionError as e: assert "THREE_PREASSEMBLED" in str(e)
 else: raise AssertionError("missing governance accepted")

def test_h8_cleanup_real_tcb_marks_context_closed():
 c=BoundedFilesystemValidationContext(prefix="oce-index77-test-"); parent=c.root.parent; bridge,dec,ctx=setup(parent,c.root)
 lease={"context":c,"cleanup_bridge":bridge,"cleanup_decision":dec,"cleaned":False}
 h8._cleanup(lease)
 assert lease["cleaned"] is True and c._closed is True and not c.root.exists()

def test_h8_no_direct_remove_tree_and_effector_has_operation():
 hs=Path(h8.__file__).read_text(encoding="utf-8"); tree=ast.parse(hs)
 run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="run")
 attrs=[n.func.attr for n in ast.walk(run) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
 assert "remove_tree" not in attrs
 from ontology.governed_filesystem_effector import ALLOWED_OPERATIONS
 assert "FS_REMOVE_TREE" in ALLOWED_OPERATIONS
