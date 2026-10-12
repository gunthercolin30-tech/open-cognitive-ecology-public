from __future__ import annotations
import hashlib,json,os,tempfile
from pathlib import Path
from typing import Any,Mapping
PRIMITIVE="occ_human_semantic_review";VERSION="P159-OCC1A-human-semantic-review-v1";STATUS="HUMAN_REVIEW_PREPARED_NOT_ADOPTED"
DECISIONS=("ACCEPT_CANDIDATE","REJECT_CANDIDATE","REQUEST_MORE_EVIDENCE","UNRESOLVED")
AUTHORIZED_ROLES=("principal_investigator","constitutional_authority")
DNA_TARGETS=tuple([f"DNA.H{i}" for i in range(1,10)]+[f"DNA.L0.{i}" for i in range(1,7)]+[f"DNA.L1.{i}" for i in range(1,9)])
def _can(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _sha(v):return hashlib.sha256(_can(v).encode()).hexdigest()
def _shaf(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1048576),b""):h.update(c)
 return h.hexdigest()
def _write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);fd,t=tempfile.mkstemp(prefix="."+p.name+".",dir=str(p.parent))
 try:
  with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f:json.dump(v,f,ensure_ascii=False,sort_keys=True,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
  os.replace(t,p)
 finally:
  if os.path.exists(t):os.unlink(t)
def build_workbook(root:Path):
 root=root.resolve();u=root/"validation/evidence/p159_occ1a/occ1a_governed_semantic_adoption_workbook_v1.json";p=root/"validation/evidence/p155_constitutional_architecture_v2/p155_historical_dna_semantic_binding_v2.json"
 raw=json.loads(u.read_text(encoding="utf-8")); rows=raw.get("rows") or raw.get("dna_rows") or raw.get("bindings") or []
 if not isinstance(rows,list) or len(rows)!=23:raise ValueError("upstream workbook must expose 23 DNA rows")
 by={str(x.get("canonical_id")):x for x in rows if isinstance(x,Mapping)}
 if set(by)!=set(DNA_TARGETS):raise ValueError("DNA target mismatch")
 entries=[]
 for n,cid in enumerate(DNA_TARGETS,1):
  r=by[cid];cand={"canonical_id":cid,"historical_id":r.get("historical_id"),"candidate_definition":r.get("candidate_definition"),"source_state":r.get("state"),"human_governance_required":r.get("human_governance_required"),"machine_assignment_normative":r.get("machine_assignment_normative")}
  e={"position":n,"candidate_id":"OCC1A-"+cid.replace(".","-"),"canonical_id":cid,"layer":"DNA_L0" if ".L0." in cid else ("DNA_L1" if ".L1." in cid else "DNA_H"),"candidate":cand,"candidate_hash":_sha(cand),"human_decision":{"decision":"","reviewer_id":"","reviewer_role":"principal_investigator","rationale":""},"normative_binding_created":False,"adoption_performed":False,"activation_performed":False,"execution_performed":False}
  e["entry_hash"]=_sha({k:v for k,v in e.items() if k not in ("human_decision","entry_hash")});entries.append(e)
 wb={"schema":"oce.p159.occ1a.human-semantic-review.v1","campaign_id":"P159-OCC1A-"+_sha({"u":_shaf(u),"p":_shaf(p)})[:20],"status":STATUS,"candidate_count":23,"entries":entries,"genesis_review":{"canonical_id":"GENESIS.G0","state":"SEPARATE_GOVERNED_REVIEW_REQUIRED","pdf_extraction_must_not_define_machine_semantics":True,"adoption_performed":False},"automatic_assignment":False,"automatic_adoption":False,"automatic_activation":False,"registry_write_on_edit":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True,"source_hashes":{"upstream":_shaf(u),"p155":_shaf(p)}}
 return wb
def validate_integrity(root,wb):
 u=root/"validation/evidence/p159_occ1a/occ1a_governed_semantic_adoption_workbook_v1.json";p=root/"validation/evidence/p155_constitutional_architecture_v2/p155_historical_dna_semantic_binding_v2.json"
 if wb.get("source_hashes")!={"upstream":_shaf(u),"p155":_shaf(p)}:raise ValueError("source drift detected")
 if wb.get("candidate_count")!=23 or len(wb.get("entries") or [])!=23:raise ValueError("count mismatch")
 seen=set()
 for e in wb["entries"]:
  cid=e.get("canonical_id")
  if cid in seen or cid not in DNA_TARGETS:raise ValueError("duplicate/unknown id")
  seen.add(cid)
  if any(e.get(k) is not False for k in ("normative_binding_created","adoption_performed","activation_performed")):raise ValueError("review cannot adopt/activate")
  if e.get("entry_hash")!=_sha({k:v for k,v in e.items() if k not in ("human_decision","entry_hash")}):raise ValueError("immutable candidate drift")
def save_decision(root,path,candidate_id,decision,reviewer_id,reviewer_role,rationale):
 wb=json.loads(path.read_text(encoding="utf-8"));validate_integrity(root,wb);decision=decision.strip().upper()
 if decision not in DECISIONS:raise ValueError("unsupported decision")
 if reviewer_role not in AUTHORIZED_ROLES:raise PermissionError("unauthorized role")
 if not reviewer_id.strip():raise ValueError("reviewer_id required")
 if len(rationale.strip())<20:raise ValueError("rationale too short")
 e=next((x for x in wb["entries"] if x["candidate_id"]==candidate_id),None)
 if e is None:raise KeyError(candidate_id)
 if decision=="ACCEPT_CANDIDATE" and (not e["candidate"].get("historical_id") or not e["candidate"].get("candidate_definition")):raise ValueError("cannot accept empty candidate")
 e["human_decision"]={"decision":decision,"reviewer_id":reviewer_id.strip(),"reviewer_role":reviewer_role,"rationale":rationale.strip()}
 validate_integrity(root,wb);_write(path,wb)
 return {"saved":True,"adoption_performed":False,"registry_write_performed":False}
def manifest():
 return {"primitive":PRIMITIVE,"version":VERSION,"status":STATUS,"reuse":["OIF governed review patterns","NiceGUI renderer"],"dna_target_count":23,"genesis_separate":True,"machine_assignment_permitted":False,"machine_adoption_permitted":False,"machine_activation_permitted":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
