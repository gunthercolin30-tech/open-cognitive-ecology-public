from __future__ import annotations
import hashlib,json,os,tempfile
from pathlib import Path
SCHEMA_ELIG="oce.p159.occ1k.final_lock_eligibility.v1"; SCHEMA_LOCK="oce.p159.occ1k.final_lock.v1"
ART_ROOT=Path("validation_artifacts/p159/occ1k"); ELIG_REL=ART_ROOT/"p159_final_lock_eligibility_v1.json"; LOCK_REL=ART_ROOT/"p159_final_lock_v1.json"
EVIDENCE={
"occ1a_closure":"validation/evidence/p159_occ1a_closure/occ1a_closing_transaction_v1.json",
"occ1b_closure":"validation_artifacts/p159/occ1b/occ1b_closure_transaction.json","occ1b_postclose":"validation_artifacts/p159/occ1b/occ1b_postclose_verification.json",
"occ1c_closure":"validation_artifacts/p159/occ1c/occ1c_closure_transaction_v1.json","occ1c_postclose":"validation_artifacts/p159/occ1c/occ1c_postclose_verification_v1.json",
"occ1d_closure":"validation_artifacts/p159/occ1d/occ1d_closure_transaction_v1.json","occ1d_postclose":"validation_artifacts/p159/occ1d/occ1d_postclose_verification_v1.json",
"occ1e_closure":"validation_artifacts/p159/occ1e/occ1e_closing_transaction_v1.json","occ1e_postclose":"validation_artifacts/p159/occ1e/occ1e_postclose_verification_v1.json",
"occ1f_closure":"validation_artifacts/p159/occ1f/occ1f_closure_transaction_v1.json","occ1f_postclose":"validation_artifacts/p159/occ1f/occ1f_postclose_verification_v1.json",
"occ1g_closure":"validation_artifacts/p159/occ1g/occ1g_closure_transaction_v1.json","occ1g_postclose":"validation_artifacts/p159/occ1g/occ1g_postclose_verification_v1.json",
"occ1h_closure":"validation_artifacts/p159/occ1h/governed_closure_v1.json","occ1h_postclose":"validation_artifacts/p159/occ1h/postclose_verification_v1.json",
"occ1i_lock":"validation_artifacts/p159/occ1i/f12a_final_lock_v1.json","occ1i_postclose":"validation_artifacts/p159/occ1i/f12b_post_close_verification_v1.json",
"occ1j_matrix":"validation_artifacts/p159/occ1j/rpi_evidence_matrix_final_v1.json","occ1j_closure":"validation_artifacts/p159/occ1j/occ1j_closure_report_v1.json"}
PROTECTED_MODULES=["ontology/occ_canonical_normative_sources.py","ontology/occ_normative_ir.py","ontology/occ_constitutional_compiler.py","ontology/occ_static_constitutional_checker.py","ontology/occ_compiled_normative_profile.py","ontology/occ_independent_constitutional_verifier.py","ontology/occ_golden_constitutional_vectors.py","ontology/occ_reproducibility_persistence.py","ontology/occ_p159_final_lock.py","ontology/occ_p159_final_lock_postlock_verifier.py"]
def root(r=None): return Path(r) if r else Path.home()/"open-cognitive-ecology"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def objhash(v): return hashlib.sha256(canon(v).encode()).hexdigest()
def atomic_json(path,obj,filesystem_effect_context=None):
 path=Path(path)
 if filesystem_effect_context is None: raise RuntimeError("occ_p159_final_lock_filesystem_effect_context_required")
 payload=(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode("utf-8")
 filesystem_effect_context.begin()
 if not path.parent.exists():
  filesystem_effect_context.execute_path("p159_final_lock_create_dirs","FS_CREATE_DIRS",path.parent)
 filesystem_effect_context.execute_path("p159_final_lock_write_replace","FS_WRITE_REPLACE_BYTES",path,payload)
def _boundary_false(p):
 for k in ("p160_opened","authorization_created","execution_performed","authority_activated"):
  if k in p and p[k] is not False:return False
 return True
def evaluate_eligibility(r=None):
 r=root(r); checks={}; hashes={}
 for name,rel in EVIDENCE.items():
  p=r/rel; checks["exists_"+name]=p.is_file()
  if p.is_file():
   hashes[name]=sha(p)
   try:d=load(p)
   except Exception:checks["parse_"+name]=False;continue
   checks["parse_"+name]=True;checks["boundary_"+name]=_boundary_false(d)
   if "p160_opened" in d:checks["p160_closed_"+name]=d["p160_opened"] is False
 from ontology import occ_occ1a_independent_postclose_verification as avm
 av=avm.audit(r); checks["occ1a_postclose_live"]=av.get("decision")==avm.PASS and av.get("occ1a_closed") is True
 a=load(r/EVIDENCE["occ1a_closure"]);checks["occ1a_closed"]=a.get("occ1a_closed") is True and a.get("final_lock_performed") is False
 b=load(r/EVIDENCE["occ1b_postclose"]);checks["occ1b_postclose"]=b.get("occ1b_closed") is True and b.get("post_close_verified") is True
 for x in ("occ1c","occ1d"):
  checks[x+"_closure_pass"]=load(r/EVIDENCE[x+"_closure"]).get("status")=="PASS";checks[x+"_postclose_pass"]=load(r/EVIDENCE[x+"_postclose"]).get("status")=="PASS"
 e=load(r/EVIDENCE["occ1e_postclose"]);checks["occ1e_postclose"]=e.get("occ1e_closed") is True and e.get("postclose_verified") is True
 f=load(r/EVIDENCE["occ1f_postclose"]);checks["occ1f_postclose"]=f.get("occ1f_closed") is True and f.get("status")=="POSTCLOSE_VERIFIED"
 g=load(r/EVIDENCE["occ1g_postclose"]);checks["occ1g_postclose"]=g.get("occ1g_closed") is True and g.get("status")=="POSTCLOSE_VERIFIED"
 h=load(r/EVIDENCE["occ1h_postclose"]);checks["occ1h_postclose"]=h.get("occ1h_closed") is True and h.get("post_close_verified") is True and h.get("status")=="POST_CLOSE_VERIFIED"
 i=load(r/EVIDENCE["occ1i_postclose"]);checks["occ1i_postclose"]=i.get("post_close_verified") is True and i.get("verification")=="POST_CLOSE_VERIFIED"
 j=load(r/EVIDENCE["occ1j_matrix"]);jc=load(r/EVIDENCE["occ1j_closure"])
 checks["occ1j_rpi_18"]=j.get("counts")=={"PASS":18,"PARTIAL":0,"UNRESOLVED":0} and j.get("occ1j_closure_ready") is True
 checks["occ1j_closure_ready"]=jc.get("status")=="CLOSURE_READY" and jc.get("transverse_debt")==0
 modules={}
 for rel in PROTECTED_MODULES:
  p=r/rel;checks["module_exists_"+Path(rel).stem]=p.is_file()
  if p.is_file():modules[rel]=sha(p)
 ok=all(v is True for v in checks.values())
 out={"schema":SCHEMA_ELIG,"milestone":"P159/OCC-1K","status":"ELIGIBLE" if ok else "BLOCKED","checks":checks,"evidence_hashes":hashes,"protected_module_hashes":modules,"occ1a_live_postclose":av,"functional_conclusion_only":True,"phenomenology_undetermined":True,"p159_final_lock":False,"p160_opened":False,"authorization_created":False,"execution_performed":False}
 out["eligibility_identity_sha256"]=objhash({k:v for k,v in out.items() if k!="eligibility_identity_sha256"});return out
def build_lock(elig,receipt):
 if elig.get("status")!="ELIGIBLE":raise ValueError("P159_NOT_ELIGIBLE")
 if not isinstance(receipt,str) or len(receipt)!=64:raise ValueError("GLOBAL_VALIDATION_RECEIPT_INVALID")
 out={"schema":SCHEMA_LOCK,"milestone":"P159/OCC-1K","status":"LOCKED","locked_scope":"P159_OCC1A_TO_OCC1J","eligibility_identity_sha256":elig["eligibility_identity_sha256"],"eligibility_evidence_hashes":elig["evidence_hashes"],"protected_module_hashes":elig["protected_module_hashes"],"global_validation_receipt_sha256":receipt,"source_compiler_verifier_authority_execution_separated":True,"compilation_is_not_authorization":True,"historical_results_preserved":True,"functional_conclusion_only":True,"phenomenology_undetermined":True,"authorization_created":False,"execution_performed":False,"p159_final_lock":True,"p160_opened":False}
 out["final_lock_identity_sha256"]=objhash({k:v for k,v in out.items() if k!="final_lock_identity_sha256"});return out
