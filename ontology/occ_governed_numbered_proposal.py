from __future__ import annotations
import hashlib,json,os,tempfile
from pathlib import Path
from typing import Any,Mapping
PRIMITIVE="occ_governed_numbered_proposal";VERSION="P159-OCC1A-governed-numbered-proposal-v1"
STATUS="NUMBERED_PROPOSAL_PREPARED_NOT_ADOPTED"
PROPOSAL_STATUS="PROPOSED_NOT_ADOPTED"
def _can(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _sha(v):return hashlib.sha256(_can(v).encode()).hexdigest()
def _load(p):return json.loads(p.read_text(encoding="utf-8"))
def _atomic(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);fd,t=tempfile.mkstemp(prefix="."+p.name+".",dir=str(p.parent))
 try:
  with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f:f.write(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n");f.flush();os.fsync(f.fileno())
  os.replace(t,p)
 finally:
  if os.path.exists(t):os.unlink(t)
def dossier_map(root:Path):
 from ontology import occ_candidate_materialization as cm
 p=root/"oif_review/campaigns/P159-OCC1A/occ1a_candidate_materialization.json";x=_load(p);cm.validate(x)
 return p,{d["canonical_id"]:d for d in x["dossiers"]}
def proposal_path(root:Path):return root/"oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json"
def empty_registry(root:Path):
 p,dm=dossier_map(root)
 return {"schema":"oce.p159.occ1a.numbered-proposals.v1","status":STATUS,"source_dossier_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
 "proposals":{},"proposal_count":0,"binding_created":False,"adoption_performed":False,"activation_performed":False,"execution_performed":False,
 "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def load_registry(root:Path):
 p=proposal_path(root)
 return _load(p) if p.exists() else empty_registry(root)
def validate_registry(root:Path,reg:Mapping[str,Any]):
 p,dm=dossier_map(root)
 if reg.get("source_dossier_sha256")!=hashlib.sha256(p.read_bytes()).hexdigest():raise ValueError("source dossier drift")
 if any(reg.get(k) is not False for k in ("binding_created","adoption_performed","activation_performed","execution_performed","occ1a_closed","occ1b_opened","p160_opened")):raise ValueError("protected state forged")
 props=reg.get("proposals") or {}
 if reg.get("proposal_count")!=len(props):raise ValueError("proposal count mismatch")
 for cid,q in props.items():
  if cid not in dm or q.get("canonical_id")!=cid:raise ValueError("unknown proposal target")
  d=dm[cid];allowed={a["historical_id"]:a for a in d["layer_compatible_historical_sources"]}
  ids=q.get("evidence_ids") or []
  if not ids or len(ids)!=len(set(ids)) or any(i not in allowed for i in ids):raise ValueError("invalid evidence selection")
  if len((q.get("candidate_definition") or "").strip())<20:raise ValueError("candidate definition too short")
  if len((q.get("proposal_rationale") or "").strip())<20:raise ValueError("proposal rationale too short")
  if not (q.get("proposer_id") or "").strip():raise ValueError("proposer required")
  if q.get("proposer_role") not in ("principal_investigator","constitutional_authority"):raise ValueError("unauthorized proposer role")
  if q.get("status")!=PROPOSAL_STATUS:raise ValueError("proposal status")
  if q.get("binding_created") is not False or q.get("adoption_performed") is not False:raise ValueError("proposal became normative")
  if q.get("dossier_hash")!=d["dossier_hash"]:raise ValueError("dossier binding drift")
  snap=[allowed[i] for i in ids]
  if q.get("evidence_snapshot_hash")!=_sha(snap):raise ValueError("evidence snapshot drift")
  base={k:v for k,v in q.items() if k!="proposal_hash"}
  if q.get("proposal_hash")!=_sha(base):raise ValueError("proposal drift")
 return True
def save_proposal(root:Path,canonical_id:str,evidence_ids:list[str],candidate_definition:str,proposal_rationale:str,proposer_id:str,proposer_role:str):
 root=root.resolve();reg=load_registry(root);validate_registry(root,reg);_,dm=dossier_map(root)
 if canonical_id not in dm:raise ValueError("unknown canonical target")
 d=dm[canonical_id];allowed={a["historical_id"]:a for a in d["layer_compatible_historical_sources"]}
 ids=list(evidence_ids)
 if not ids or len(ids)!=len(set(ids)) or any(i not in allowed for i in ids):raise ValueError("evidence must be unique and layer-compatible")
 if len(candidate_definition.strip())<20 or len(proposal_rationale.strip())<20:raise ValueError("definition/rationale minimum 20 chars")
 if not proposer_id.strip():raise ValueError("proposer required")
 if proposer_role not in ("principal_investigator","constitutional_authority"):raise ValueError("unauthorized proposer role")
 if ".L0." in canonical_id:
  governance_route="REFOUNDING_OR_FORK_REVIEW_REQUIRED"
 else: governance_route="GOVERNED_REVIEW_REQUIRED"
 q={"canonical_id":canonical_id,"evidence_ids":ids,"candidate_definition":candidate_definition.strip(),"proposal_rationale":proposal_rationale.strip(),
 "proposer_id":proposer_id.strip(),"proposer_role":proposer_role,"status":PROPOSAL_STATUS,"governance_route":governance_route,
 "dossier_hash":d["dossier_hash"],"evidence_snapshot_hash":_sha([allowed[i] for i in ids]),"binding_created":False,"adoption_performed":False,
 "activation_performed":False,"execution_performed":False}
 q["proposal_hash"]=_sha(q);reg["proposals"][canonical_id]=q;reg["proposal_count"]=len(reg["proposals"]);_atomic(proposal_path(root),reg)
 return q
def manifest():
 return {"primitive":PRIMITIVE,"version":VERSION,"status":STATUS,"proposal_is_binding":False,"machine_proposal_permitted":False,
 "adoption_performed":False,"activation_performed":False,"execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
