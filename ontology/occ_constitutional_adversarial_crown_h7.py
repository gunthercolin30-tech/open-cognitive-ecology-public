from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
from pathlib import Path
from ontology.governed_isolated_probe_runner import run_isolated_generated_probe, as_completed_process
import json,hashlib,sys
from ontology import occ_independent_constitutional_verifier as verifier
from ontology import occ_independent_constitutional_verification_report as verifier_report
VERDICTS=("RESISTED","DETECTED","CONTAINED","DEGRADED_SAFELY","RECOVERED","NEAR_FAILURE","VIOLATED","INCONCLUSIVE")
A075_V1_BINDING_INPUTS=(Path("ontology/occ_normative_ir.py"),Path("ontology/occ_normative_ir_real_builder.py"),verifier_report.COMMON_TCB_REL,verifier_report.CHECK_REGISTRY_REL)
A075_IMPORT_CLOSURE=("ontology/dna_adversarial_regression.py","ontology/dna_fitness_suite.py","ontology/dna_fundamental.py","ontology/dna_inheritance.py","ontology/dna_mutation_protocol.py","ontology/dna_registry.py","ontology/dna_rule_contract.py","ontology/dna_severity_model.py","ontology/dna_stack.py","ontology/dna_versioning_lineage.py","ontology/minimal_dna.py","ontology/normative_hierarchy.py","ontology/occ_independent_constitutional_verification_report.py","ontology/occ_independent_constitutional_verifier.py","ontology/occ_normative_ir.py","ontology/occ_normative_ir_real_builder.py")
ATTACKS=(("A065","trust compiler PASS"),("A066","trust declared/compiler hash"),("A067","missing rule"),("A068","extra rule"),("A069","post-compile mutation"),("A070","parser differential"),("A071","shared bug"),("A072","INDETERMINATE to VERIFIED"),("A073","partial to VERIFIED"),("A074","verifier repair"),("A075","verifier self-upgrade"))
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _row(a,l,v,r,e=None): return {"attack_id":a,"canonical_attack_id":"A"+str(int(a[1:])),"family_id":"H7","label":l,"success_criteria_fixed_before_execution":True,"verdict":v,"reason":r,"evidence":e or {},"authorization_created":False,"execution_performed":False}
def _sandbox(root,lease=None):
 if not isinstance(lease,dict): raise PermissionError("H7_PREASSEMBLED_SANDBOX_LEASE_REQUIRED")
 ctx=lease.get("context"); fctx=lease.get("filesystem_context")
 if not isinstance(ctx,BoundedFilesystemValidationContext): raise PermissionError("H7_BOUNDED_CONTEXT_REQUIRED")
 if fctx is None or getattr(fctx,"authority_minting",True) is not False: raise PermissionError("H7_GOVERNED_FILESYSTEM_CONTEXT_REQUIRED")
 if Path(getattr(fctx,"root_path","")).resolve()!=ctx.root.parent.resolve(): raise PermissionError("H7_SANDBOX_ROOT_BINDING_MISMATCH")
 if lease.get("cleaned") is True: raise RuntimeError("H7_SANDBOX_LEASE_REPLAY")
 fctx.begin()
 d=ctx.root/"repo"
 try:
  for src in verifier.paths(root).values():
   if not src.exists(): continue
   rel=Path("repo")/src.relative_to(root)
   ctx.copytree_from(src,rel) if src.is_dir() else ctx.copy2_from(src,rel)
 except Exception:
  _cleanup(lease); raise
 return ctx,d
def _ensure_parent_governed(lease,sb,path):
 parent=Path(path).parent
 if parent.is_dir(): return
 try: rel=parent.resolve(strict=False).relative_to(Path(sb).resolve()).as_posix()
 except Exception as exc: raise PermissionError("H7_PARENT_OUTSIDE_SANDBOX") from exc
 slot=lease.get("parent_slots",{}).get(rel)
 if not isinstance(slot,str) or not slot: raise PermissionError("H7_PREISSUED_PARENT_SLOT_REQUIRED:"+rel)
 chain=[]; cur=parent
 while not cur.exists():
  chain.append(cur); cur=cur.parent
 if not cur.is_dir(): raise PermissionError("H7_PARENT_ANCESTOR_NOT_DIRECTORY:"+rel)
 for item in reversed(chain):
  item_rel=item.resolve(strict=False).relative_to(Path(sb).resolve()).as_posix()
  item_slot=lease.get("parent_slots",{}).get(item_rel)
  if not isinstance(item_slot,str) or not item_slot: raise PermissionError("H7_PREISSUED_PARENT_SLOT_REQUIRED:"+item_rel)
  lease["filesystem_context"].execute_path(item_slot,"FS_CREATE_DIR",item)
 if not parent.is_dir(): raise RuntimeError("H7_GOVERNED_PARENT_CREATE_FAILED:"+rel)

def _cleanup(lease):
 ctx=lease["context"]; fctx=lease["filesystem_context"]
 fctx.execute_path("sandbox_cleanup","FS_REMOVE_TREE",ctx.root)
 lease["cleaned"]=True; ctx._closed=True
 if ctx.root.exists() or ctx.root.is_symlink(): raise RuntimeError("H7_GOVERNED_SANDBOX_CLEANUP_FAILED")
def _mut(ctx,root,fn,rehash=False):
 p=verifier.paths(root)["profile"]; x=json.loads(p.read_text(encoding="utf-8")); fn(x)
 if rehash:
  y=dict(x); y.pop("artifact_hash",None); x["artifact_hash"]=verifier._canonical_hash(y)
 rel=p.resolve().relative_to(ctx.root)
 ctx.write_text(rel,json.dumps(x,sort_keys=True,indent=2)+"\n",encoding="utf-8")
def _det(r,c=None): return r.get("verdict")==verifier.REJECTED and (c is None or c in r.get("failed_check_ids",[]))
def run(root,sandbox_leases=None):
 root=Path(root).resolve(); labels=dict(ATTACKS); rows=[]
 if not isinstance(sandbox_leases,(list,tuple)) or len(sandbox_leases)!=7: raise PermissionError("H7_EXACT_SEVEN_PREASSEMBLED_SANDBOX_LEASES_REQUIRED")
 lease_iter=iter(sandbox_leases)
 baseline=verifier.verify(root)
 ok=baseline.get("legacy_upstream_states_used_as_verdict_oracle") is False and baseline.get("compiler_hash_trusted_without_recalculation") is False
 rows.append(_row("A065",labels["A065"],"RESISTED" if ok else "VIOLATED","VERIFIER_DOES_NOT_USE_COMPILER_PASS_AS_ORACLE" if ok else "COMPILER_ORACLE_TRUST_OBSERVED"))
 cases=[
 ("A066","IVI-1",lambda x:x.update({"artifact_hash":"0"*64}),False,"IVI1_HASH_RECALCULATION"),
 ("A067","IVI-3",lambda x:x["rules"].pop(),True,"IVI3_MISSING_RULE"),
 ("A069","IVI-5",lambda x:x["rules"][0]["normative_effect"]["result_domain"].append("ALLOW_EXECUTION"),True,"IVI5_REHASHED_SEMANTIC_MUTATION")]
 for aid,cid,fn,rh,reason in cases:
  current_lease=next(lease_iter); sb_ctx,sb=_sandbox(root,current_lease)
  try:
   _mut(sb_ctx,sb,fn,rh); r=verifier.verify(sb); ok=_det(r,cid)
   rows.append(_row(aid,labels[aid],"DETECTED" if ok else "VIOLATED",reason if ok else aid+"_ATTACK_ACCEPTED",{"verdict":r.get("verdict"),"failed":r.get("failed_check_ids",[])}))
  finally: _cleanup(current_lease)
 current_lease=next(lease_iter); sb_ctx,sb=_sandbox(root,current_lease)
 try:
  def extra(x):
   z=dict(x["rules"][0]); z["rule_id"]="H7.FAKE.EXTRA"; z["source_norm_ids"]=[]; z["nir_node_ids"]=[]; x["rules"].append(z)
  _mut(sb_ctx,sb,extra,True); r=verifier.verify(sb); ok=_det(r,"IVI-4")
  rows.append(_row("A068",labels["A068"],"DETECTED" if ok else "VIOLATED","IVI4_EXTRA_RULE" if ok else "EXTRA_RULE_ACCEPTED",{"verdict":r.get("verdict"),"failed":r.get("failed_check_ids",[])}))
 finally: _cleanup(current_lease)
 rows.append(_row("A070",labels["A070"],"INCONCLUSIVE","NO_INDEPENDENT_PARSER_DIFFERENTIAL_ORACLE_IN_OCC1F_SCOPE"))
 rows.append(_row("A071",labels["A071"],"INCONCLUSIVE","COMMON_TCB_DISCLOSED_BUT_SHARED_BUG_RESISTANCE_NOT_EMPIRICALLY_PROVEN",{"common_tcb":list(verifier.COMMON_TCB)}))
 current_lease=next(lease_iter); sb_ctx,sb=_sandbox(root,current_lease)
 try:
  current_lease["filesystem_context"].execute_path("a072_remove","FS_REMOVE_FILE",verifier.paths(sb)["occ1d_coverage"]); r=verifier.verify(sb); ok=r.get("verdict")==verifier.INDETERMINATE
  rows.append(_row("A072",labels["A072"],"DETECTED" if ok else "VIOLATED","INDETERMINATE_PRESERVED" if ok else "INDETERMINATE_PROMOTED",{"verdict":r.get("verdict")}))
 finally: _cleanup(current_lease)
 current_lease=next(lease_iter); sb_ctx,sb=_sandbox(root,current_lease)
 try:
  def partial(x):
   b=next(iter(x["enforcement_map"]["rule_bindings"].values())); b["runtime_reachability_proven"]=True; b["consumers"]=[]
  _mut(sb_ctx,sb,partial,True); r=verifier.verify(sb); ok=_det(r,"IVI-10")
  rows.append(_row("A073",labels["A073"],"DETECTED" if ok else "VIOLATED","IVI10_PARTIAL_REPORTING" if ok else "PARTIAL_PROMOTED_TO_VERIFIED",{"verdict":r.get("verdict"),"failed":r.get("failed_check_ids",[])}))
 finally: _cleanup(current_lease)
 pp=verifier.paths(root)["profile"]; before=_sha(pp); r=verifier.verify(root); after=_sha(pp); ok=before==after and r.get("repair_performed") is False
 rows.append(_row("A074",labels["A074"],"RESISTED" if ok else "VIOLATED","READ_ONLY_NO_REPAIR" if ok else "VERIFIER_REPAIR_OBSERVED",{"before":before,"after":after}))
 current_lease=next(lease_iter); sb_ctx,sb=_sandbox(root,current_lease)
 try:
  vp=sb/"ontology"/"occ_independent_constitutional_verifier.py"
  incumbent=Path(verifier.__file__).resolve()
  if incumbent.suffix==".pyc" and incumbent.with_suffix(".py").is_file(): incumbent=incumbent.with_suffix(".py")
  if not incumbent.is_file(): raise FileNotFoundError("A075 incumbent verifier source unavailable: "+str(incumbent))
  _ensure_parent_governed(current_lease,sb,vp)
  current_lease["filesystem_context"].execute_copy2("a075_verifier_copy","repo",root,incumbent,vp)
  # A075_V1_PRECLOSE_BINDING_INPUTS
  for rel in A075_V1_BINDING_INPUTS:
   srcp=root/rel
   if not srcp.is_file(): raise FileNotFoundError("A075 required V1 binding input missing: "+str(srcp))
   dstp=sb/rel
   _ensure_parent_governed(current_lease,sb,dstp)
   current_lease["filesystem_context"].execute_copy2("a075_binding_copy","repo",root,srcp,dstp)
  v1_sha=_sha(vp); src=vp.read_text(encoding="utf-8")
  marker='lm.get("self_activation") is False'
  if marker not in src:
   replacement={"status":"INDETERMINATE","reason":"A075_WEAKENING_ANCHOR_MISSING"}
  else:
   weakened=src.replace(marker,"True",1)
   current_lease["filesystem_context"].execute_path("a075_verifier_write","FS_WRITE_REPLACE_BYTES",vp,weakened.encode("utf-8")); v2_sha=_sha(vp)
   try:
    compile(weakened,str(vp),"exec"); syntax_ok=True
   except SyntaxError:
    syntax_ok=False
   binding=verifier_report.verify_preclose_evidence(sb) if syntax_ok else {"status":"REJECTED","reason":"A075_V2_SYNTAX_INVALID"}
   replacement={"status":binding.get("status"),"reason":binding.get("reason"),"v1_sha256":v1_sha,"v2_sha256":v2_sha,"v1_v2_distinct":v1_sha!=v2_sha,"v2_syntax_valid":syntax_ok,"weakening":"IVI11_SELF_ACTIVATION_GUARD_REMOVED","external_binding_rejected":binding.get("status")=="REJECTED"}
  ok=(replacement.get("external_binding_rejected") is True and replacement.get("v1_v2_distinct") is True and replacement.get("v2_syntax_valid") is True)
  # A075_LOADED_V2_SELF_CERTIFICATION_V1
  # A075_LOADED_V2_SELF_CERTIFICATION_V2
  for _rel in A075_IMPORT_CLOSURE:
   _src=root/_rel; _dst=sb/_rel
   if not _src.is_file(): raise RuntimeError("A075_IMPORT_CLOSURE_SOURCE_MISSING:"+_rel)
   _ensure_parent_governed(current_lease,sb,_dst)
   if _rel!="ontology/occ_independent_constitutional_verifier.py": current_lease["filesystem_context"].execute_copy2("a075_closure_copy","repo",root,_src,_dst)
  _closure_missing=[_rel for _rel in A075_IMPORT_CLOSURE if not (sb/_rel).is_file()]
  if _closure_missing: raise RuntimeError("A075_IMPORT_CLOSURE_MATERIALIZATION_FAILED:"+",".join(_closure_missing))
  tcbp=sb/verifier_report.COMMON_TCB_REL; regp=sb/verifier_report.CHECK_REGISTRY_REL
  v1_tcb_sha=_sha(tcbp); v1_reg_sha=_sha(regp)
  child=sb/"a075_loaded_v2_probe.py"
  child_source="""import json,sys,hashlib
from pathlib import Path
root=Path(sys.argv[1]).resolve(); sys.path.insert(0,str(root))
from ontology import occ_independent_constitutional_verifier as v
from ontology import occ_independent_constitutional_verification_report as r
def sh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
vp=root/'ontology'/'occ_independent_constitutional_verifier.py'
out={'loaded_verifier_path':str(Path(v.__file__).resolve()),'loaded_verifier_sha256':sh(Path(v.__file__).resolve()),'sandbox_verifier_sha256':sh(vp)}
out['loaded_from_sandbox']=Path(v.__file__).resolve()==vp.resolve()
out['pre_materialize']=r.verify_preclose_evidence(root)
try:
 r.materialize_preclose_evidence(root); out['materialize']='SUCCEEDED'
except Exception as e:
 out['materialize']='REJECTED'; out['materialize_error']=type(e).__name__+':'+str(e)
out['post_materialize']=r.verify_preclose_evidence(root)
out['tcb_sha256']=sh(root/r.COMMON_TCB_REL) if (root/r.COMMON_TCB_REL).is_file() else None
out['registry_sha256']=sh(root/r.CHECK_REGISTRY_REL) if (root/r.CHECK_REGISTRY_REL).is_file() else None
print(json.dumps(out,sort_keys=True))
"""
  current_lease["filesystem_context"].execute_path("a075_child_write","FS_WRITE_REPLACE_BYTES",child,child_source.encode("utf-8"))
  cp=as_completed_process(run_isolated_generated_probe(script=child, sandbox=sb, timeout_seconds=30))
  if cp.returncode==0:
   try: loaded=json.loads(cp.stdout.strip().splitlines()[-1])
   except Exception: loaded={"parse_error":True,"stdout":cp.stdout[-2000:]}
  else: loaded={"child_returncode":cp.returncode,"stderr":cp.stderr[-2000:],"stdout":cp.stdout[-2000:]}
  loaded["external_v1_tcb_sha256"]=v1_tcb_sha; loaded["external_v1_registry_sha256"]=v1_reg_sha
  loaded["preclose_artifacts_rewritten"]=(loaded.get("tcb_sha256") not in (None,v1_tcb_sha) or loaded.get("registry_sha256") not in (None,v1_reg_sha))
  loaded["self_certified_after_rewrite"]=(loaded.get("post_materialize",{}).get("status")=="VERIFIED_PRECLOSE_BINDING")
  loaded["self_certification_attempt_reached"]=(loaded.get("materialize") in ("SUCCEEDED","REJECTED"))
  loaded["loaded_v2_identity_proven"]=(loaded.get("loaded_from_sandbox") is True and loaded.get("loaded_verifier_sha256")==v2_sha)
  loaded["loaded_v2_self_certification_materialized"]=(loaded.get("loaded_v2_identity_proven") is True and loaded.get("self_certification_attempt_reached") is True)
  if loaded.get("loaded_v2_identity_proven") and loaded.get("self_certified_after_rewrite") and loaded.get("preclose_artifacts_rewritten"): loaded_result="COUNTEREXAMPLE_CANDIDATE"
  elif loaded.get("loaded_v2_identity_proven") and not loaded.get("self_certified_after_rewrite"): loaded_result="REJECTED"
  else: loaded_result="INDETERMINATE"
  rows.append(_row("A075",labels["A075"],"INCONCLUSIVE","LOADED_V2_SELF_CERTIFICATION_EXPERIMENT_EXECUTED_PENDING_COUNTEREXAMPLE_CLASSIFICATION",{"replacement_probe_result":"DETECTED" if ok else "VIOLATED","replacement":replacement,"loaded_v2_self_certification_materialized":bool(loaded.get("loaded_v2_self_certification_materialized")),"loaded_v2_probe_result":loaded_result,"loaded_v2":loaded,"full_verifier_replacement_path_materialized":bool(loaded.get("loaded_v2_identity_proven"))}))
 finally: _cleanup(current_lease)
 rows.sort(key=lambda x:int(x["attack_id"][1:]))
 counts={v:sum(x["verdict"]==v for x in rows) for v in VERDICTS}
 return {"schema":"oce.p159.occ1h.h7.execution.v1","family_id":"H7","scenario_count":11,"verifier_file_sha256":_sha(Path(verifier.__file__)),"baseline_verdict":baseline.get("verdict"),"rows":rows,"verdict_counts":counts,"success_criteria_fixed_before_execution":True,"inconclusive_not_resisted":True,"historical_evidence_rewritten":False,"normative_auto_rewrite":False,"authorization_created":False,"execution_performed":False,"functional_only":True,"phenomenology_undetermined":True,"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
