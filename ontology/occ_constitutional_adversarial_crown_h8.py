from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
from ontology.governed_evidence_effect_policy import EvidenceEffectDecision
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from pathlib import Path
import json,hashlib,tempfile
from ontology import occ_compiled_normative_profile_postclose_verifier as pcv
VERDICTS=("RESISTED","DETECTED","CONTAINED","DEGRADED_SAFELY","RECOVERED","NEAR_FAILURE","VIOLATED","INCONCLUSIVE")
ATTACKS=(("A076","post-verification mutation"),("A077","post-seal mutation"),("A078","stale report"),("A079","stale CNP"),("A080","revoked activation"),("A081","registry substitution"),("A082","cache substitution"),("A083","token/CNP mismatch"),("A084","clock rollback"),("A085","emergency replay"))
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _row(a,l,v,r,e=None): return {"attack_id":a,"canonical_attack_id":"A"+str(int(a[1:])),"family_id":"H8","label":l,"success_criteria_fixed_before_execution":True,"verdict":v,"reason":r,"evidence":e or {},"authorization_created":False,"execution_performed":False}
def _sandbox(root, lease):
 if not isinstance(lease,dict): raise TypeError("H8_SANDBOX_LEASE_REQUIRED")
 ctx=lease.get("context"); bridge=lease.get("cleanup_bridge"); decision=lease.get("cleanup_decision")
 if not isinstance(ctx,BoundedFilesystemValidationContext): raise TypeError("H8_BOUNDED_CONTEXT_REQUIRED")
 if not isinstance(bridge,GovernedEvidenceFilesystemBridge): raise TypeError("H8_CLEANUP_BRIDGE_REQUIRED")
 if not isinstance(decision,EvidenceEffectDecision): raise TypeError("H8_CLEANUP_DECISION_REQUIRED")
 if lease.get("cleaned") is True: raise RuntimeError("H8_SANDBOX_LEASE_REPLAY")
 d=ctx.root/"repo"
 try:
  for src in pcv.paths(root).values():
   if not src.exists(): continue
   rel=Path("repo")/src.relative_to(root)
   ctx.copytree_from(src,rel) if src.is_dir() else ctx.copy2_from(src,rel)
 except Exception:
  _cleanup(lease)
  raise
 return ctx,d
def _cleanup(lease):
 ctx=lease["context"]; bridge=lease["cleanup_bridge"]; decision=lease["cleanup_decision"]
 fsctx=bridge.filesystem_context; parent=ctx.root.parent.resolve()
 if getattr(fsctx,"root_path",None) is None or Path(fsctx.root_path).resolve()!=parent:
  raise RuntimeError("H8_CLEANUP_ROOT_BINDING_MISMATCH")
 result=bridge.execute_path(decision=decision,evidence_role="occ1h_h8_validation_sandbox_cleanup",
  slot="h8_sandbox_cleanup",operation_id="FS_REMOVE_TREE",path=ctx.root.name)
 if not isinstance(result,dict) or result.get("status")!="EVIDENCE_EFFECT_CONFIRMED":
  raise PermissionError("H8_SANDBOX_CLEANUP_DENIED")
 lease["cleaned"]=True; ctx._closed=True
 if ctx.root.exists() or ctx.root.is_symlink(): raise RuntimeError("H8_SANDBOX_CLEANUP_POSTCONDITION_FAILED")
def _mut_json(p,fn):
 x=json.loads(p.read_text(encoding="utf-8")); fn(x); p.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n",encoding="utf-8")
def run(root, sandbox_leases=None):
 root=Path(root); labels=dict(ATTACKS); rows=[]
 if not isinstance(sandbox_leases,(list,tuple)) or len(sandbox_leases)!=3:
  raise PermissionError("H8_THREE_PREASSEMBLED_GOVERNED_SANDBOX_LEASES_REQUIRED")
 leases=iter(sandbox_leases); baseline=pcv.verify(root)
 # A76: verify, mutate profile, verify again. Re-verification must reject drift.
 lease=next(leases); sb_ctx,sb=_sandbox(root,lease)
 try:
  before=pcv.verify(sb); pp=pcv.paths(sb)["profile"]; _mut_json(pp,lambda x:x.update({"h8_post_verification_mutation":True})); after=pcv.verify(sb)
  ok=before.get("postclose_verified") is True and after.get("postclose_verified") is False and after.get("source_drift_detected") is True
  rows.append(_row("A076",labels["A076"],"DETECTED" if ok else "VIOLATED","POST_VERIFICATION_DRIFT_REJECTED" if ok else "POST_VERIFICATION_MUTATION_NOT_REJECTED",{"before":before.get("decision"),"after":after.get("decision")}))
 finally: _cleanup(lease)
 # A77: mutate a closure-bound manifest after seal.
 lease=next(leases); sb_ctx,sb=_sandbox(root,lease)
 try:
  mp=pcv.paths(sb)["manifest"]; _mut_json(mp,lambda x:x.update({"h8_post_seal_mutation":True})); r=pcv.verify(sb); ok=r.get("postclose_verified") is False and r.get("source_drift_detected") is True
  rows.append(_row("A077",labels["A077"],"DETECTED" if ok else "VIOLATED","POST_SEAL_INPUT_DRIFT_REJECTED" if ok else "POST_SEAL_MUTATION_NOT_REJECTED",{"decision":r.get("decision")}))
 finally: _cleanup(lease)
 # A78: a previously written report can physically remain stale; no P159 consumer freshness gate is proven.
 rows.append(_row("A078",labels["A078"],"INCONCLUSIVE","STALE_REPORT_CAN_EXIST_BUT_NO_P159_REPORT_CONSUMER_FRESHNESS_GATE_IS_PROVEN"))
 # A79: stale/substituted CNP is closure-bound and rejected on fresh verification.
 lease=next(leases); sb_ctx,sb=_sandbox(root,lease)
 try:
  pth=pcv.paths(sb); sb_ctx.copy2_from(pth["source"],pth["profile"].relative_to(sb_ctx.root)); r=pcv.verify(sb); ok=r.get("postclose_verified") is False
  rows.append(_row("A079",labels["A079"],"DETECTED" if ok else "VIOLATED","STALE_OR_SUBSTITUTED_CNP_REJECTED_BY_POSTCLOSE_BINDING" if ok else "STALE_CNP_ACCEPTED",{"decision":r.get("decision")}))
 finally: _cleanup(lease)
 # Remaining attacks require runtime/lifecycle consumers that P159 explicitly does not claim.
 boundaries={
 "A080":"REVOCATION_ACTIVATION_PATH_NOT_PROVEN_AT_P159",
 "A081":"RUNTIME_REGISTRY_CONSUMER_BINDING_NOT_PROVEN_AT_P159",
 "A082":"RUNTIME_CACHE_CONSUMER_BINDING_NOT_PROVEN_AT_P159",
 "A083":"TOKEN_TO_CNP_RUNTIME_BINDING_NOT_PROVEN_AT_P159",
 "A084":"CLOCK_DEPENDENT_CONSTITUTIONAL_ENFORCEMENT_NOT_PROVEN_AT_P159",
 "A085":"EMERGENCY_REPLAY_ENFORCEMENT_PATH_NOT_PROVEN_AT_P159"}
 for aid,reason in boundaries.items(): rows.append(_row(aid,labels[aid],"INCONCLUSIVE",reason))
 rows.sort(key=lambda x:int(x["attack_id"][1:]))
 counts={v:sum(x["verdict"]==v for x in rows) for v in VERDICTS}
 return {"schema":"oce.p159.occ1h.h8.execution.v1","family_id":"H8","scenario_count":10,"postclose_verifier_sha256":_sha(Path(pcv.__file__)),"baseline_decision":baseline.get("decision"),"rows":rows,"verdict_counts":counts,"success_criteria_fixed_before_execution":True,"inconclusive_not_resisted":True,"runtime_absence_not_resistance":True,"historical_evidence_rewritten":False,"normative_auto_rewrite":False,"authorization_created":False,"execution_performed":False,"functional_only":True,"phenomenology_undetermined":True,"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
