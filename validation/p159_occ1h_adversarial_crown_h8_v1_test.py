from pathlib import Path
from types import SimpleNamespace
from ontology import occ_constitutional_adversarial_crown_h8 as h8
from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
from ontology.governed_evidence_effect_policy import ALLOW, EvidenceEffectDecision, GovernedEvidenceEffectPolicy
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
ROOT=Path(__file__).resolve().parents[1]
class _Broker:
 def __init__(self,handle_id): self.handle_id=handle_id; self.used=False
 def consume_once(self,handle_id):
  if self.used or handle_id!=self.handle_id:return False
  self.used=True;return True
def _leases():
 out=[]
 for i in range(3):
  ctx=BoundedFilesystemValidationContext(prefix="oce-occ1h-h8-"); parent=ctx.root.parent.resolve(); root_id="h8-parent-%d"%i
  binding="filesystem://%s/%s"%(root_id,ctx.root.name); hid="h8-cleanup-%d"%i
  handle=SimpleNamespace(handle_id=hid,adapter_id="h8-validation",effector_id="filesystem",operation_id="FS_REMOVE_TREE",
   target_binding=binding,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
  eff=GovernedFilesystemEffector(root_registry={root_id:str(parent)},handle_broker=_Broker(hid))
  fsctx=GovernedFilesystemEffectContext(slots={"h8_sandbox_cleanup":[handle]},effector=eff,root_id=root_id,
   root_path=parent,adapter_id="h8-validation",effector_id="filesystem"); fsctx.begin()
  bridge=GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(),fsctx)
  decision=EvidenceEffectDecision(decision_id="h8-cleanup-decision-%d"%i,decision=ALLOW,
   evidence_role="occ1h_h8_validation_sandbox_cleanup",operation_id="FS_REMOVE_TREE",target_binding=binding,
   rationale="bounded H8 validation sandbox cleanup",provenance="P162-G6 index77 exact migration",
   authorization_inference=False,implementation_authorized=False)
  out.append({"context":ctx,"cleanup_bridge":bridge,"cleanup_decision":decision,"cleaned":False})
 return out
def _run(): return h8.run(ROOT,sandbox_leases=_leases())
def test_h8_exact_range():
 r=_run(); assert r["scenario_count"]==10
 assert [x["attack_id"] for x in r["rows"]]==["A%03d"%i for i in range(76,86)]
 assert [x["canonical_attack_id"] for x in r["rows"]]==["A%d"%i for i in range(76,86)]
def test_h8_executable_lifecycle_attacks_detected():
 d={x["attack_id"]:x for x in _run()["rows"]}
 for a in ("A076","A077","A079"): assert d[a]["verdict"]=="DETECTED",(a,d[a])
def test_h8_runtime_boundaries_not_laundered():
 r=_run(); d={x["attack_id"]:x for x in r["rows"]}
 for a in ("A078","A080","A081","A082","A083","A084","A085"): assert d[a]["verdict"]=="INCONCLUSIVE"
 assert r["runtime_absence_not_resistance"] and r["inconclusive_not_resisted"]
def test_h8_no_authority_execution_or_closure():
 r=_run(); assert not r["authorization_created"] and not r["execution_performed"]
 assert not r["occ1h_closed"] and not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]
def test_h8_deterministic_summary():
 a=_run(); b=_run()
 assert [(x["attack_id"],x["verdict"],x["reason"]) for x in a["rows"]]==[(x["attack_id"],x["verdict"],x["reason"]) for x in b["rows"]]
 assert a["postclose_verifier_sha256"]==b["postclose_verifier_sha256"]
