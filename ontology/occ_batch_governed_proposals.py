from __future__ import annotations
import hashlib,json,os,shutil,tempfile
from pathlib import Path
from ontology import occ_governed_numbered_proposal as unit
SCHEMA="oce.p159.occ1a.batch-proposals.v1"
TARGETS=tuple([f"DNA.H{i}" for i in range(4,10)]+[f"DNA.L0.{i}" for i in range(1,7)]+[f"DNA.L1.{i}" for i in range(1,9)])
def _load(p): return json.loads(p.read_text(encoding="utf-8"))
def _atomic(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);fd,t=tempfile.mkstemp(prefix="."+p.name+".",dir=str(p.parent))
 try:
  with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f:f.write(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n");f.flush();os.fsync(f.fileno())
  os.replace(t,p)
 finally:
  if os.path.exists(t):os.unlink(t)
def template(root):
 _,dm=unit.dossier_map(root.resolve());rows=[]
 for cid in TARGETS:
  a=[x["historical_id"] for x in dm[cid]["layer_compatible_historical_sources"]]
  rows.append({"canonical_id":cid,"allowed_evidence_ids":a,"evidence_ids":[],"candidate_definition":"","proposal_rationale":"","proposer_id":"","proposer_role":"principal_investigator","human_completion_required":True})
 return {"schema":SCHEMA,"status":"DRAFT_HUMAN_COMPLETION_REQUIRED","targets":list(TARGETS),"proposal_count_expected":20,"machine_mapping_performed":False,"machine_ranking_performed":False,"machine_adoption_performed":False,"proposals":rows}
def validate_document(root,d):
 if d.get("schema")!=SCHEMA or d.get("targets")!=list(TARGETS) or d.get("proposal_count_expected")!=20:raise ValueError("batch scope/schema drift")
 if any(d.get(k) is not False for k in ("machine_mapping_performed","machine_ranking_performed","machine_adoption_performed")):raise ValueError("machine authority forged")
 rows=d.get("proposals"); ids=[r.get("canonical_id") for r in rows or []]
 if len(rows or [])!=20 or ids!=list(TARGETS) or len(set(ids))!=20:raise ValueError("batch must contain exact 20 targets")
 _,dm=unit.dossier_map(root.resolve())
 for r in rows:
  cid=r["canonical_id"];allowed=[x["historical_id"] for x in dm[cid]["layer_compatible_historical_sources"]]
  if r.get("allowed_evidence_ids")!=allowed:raise ValueError(cid+": evidence vocabulary drift")
  chosen=r.get("evidence_ids") or []
  if not chosen or len(chosen)!=len(set(chosen)) or any(x not in allowed for x in chosen):raise ValueError(cid+": invalid evidence")
  if len(str(r.get("candidate_definition") or "").strip())<20 or len(str(r.get("proposal_rationale") or "").strip())<20:raise ValueError(cid+": incomplete human semantics")
  if not str(r.get("proposer_id") or "").strip():raise ValueError(cid+": proposer required")
  if r.get("proposer_role") not in ("principal_investigator","constitutional_authority"):raise ValueError(cid+": role")
  if r.get("human_completion_required") is not True:raise ValueError(cid+": human marker removed")
def apply_batch(root,batch_path):
 root=root.resolve();doc=_load(batch_path.resolve());validate_document(root,doc)
 rp=unit.proposal_path(root);reg=unit.load_registry(root);unit.validate_registry(root,reg)
 if any(cid not in reg["proposals"] for cid in ("DNA.H1","DNA.H2","DNA.H3")):raise ValueError("H1-H3 pilot proposals required")
 if any(cid in reg["proposals"] for cid in TARGETS):raise ValueError("refuse overwrite H4..L1.8")
 before=hashlib.sha256(rp.read_bytes()).hexdigest()
 with tempfile.TemporaryDirectory(prefix="oce_occ1a_batch_") as td:
  stage=Path(td)/"repo";rel=Path("oif_review/campaigns/P159-OCC1A/occ1a_candidate_materialization.json");rr=Path("oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json")
  (stage/rel.parent).mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,stage/rel);shutil.copy2(rp,stage/rr)
  for r in doc["proposals"]:unit.save_proposal(stage,r["canonical_id"],list(r["evidence_ids"]),str(r["candidate_definition"]),str(r["proposal_rationale"]),str(r["proposer_id"]),str(r["proposer_role"]))
  staged=unit.load_registry(stage);unit.validate_registry(stage,staged)
  if staged["proposal_count"]!=23:raise ValueError("staged count")
  if any(staged[k] is not False for k in ("binding_created","adoption_performed","activation_performed","execution_performed","occ1a_closed","occ1b_opened","p160_opened")):raise ValueError("protected boundary")
  if hashlib.sha256(rp.read_bytes()).hexdigest()!=before:raise RuntimeError("real registry changed during prevalidation")
  _atomic(rp,staged)
 after=unit.load_registry(root);unit.validate_registry(root,after)
 return {"status":"BATCH_PROPOSALS_COMMITTED_NOT_ADOPTED","before_sha256":before,"after_sha256":hashlib.sha256(rp.read_bytes()).hexdigest(),"proposal_count":after["proposal_count"],"binding_created":False,"adoption_performed":False,"activation_performed":False,"execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
def manifest():return {"primitive":"occ_batch_governed_proposals","reuses_unit_primitive":True,"direct_normative_authority":False,"transactional_prevalidation":True,"single_atomic_commit":True,"human_semantic_completion_required":True,"batch_target_count":20,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
