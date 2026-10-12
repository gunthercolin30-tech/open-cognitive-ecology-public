from pathlib import Path
from hashlib import sha256
import json
ROOT=Path.home()/"open-cognitive-ecology"
REG_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json")
ALLOWED=("ADOPT","REJECT","REQUEST_MORE_EVIDENCE","ABSTAIN")
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def h(v): return sha256(canon(v).encode()).hexdigest()
def load_registry(root=ROOT):
 p=Path(root)/REG_REL; raw=p.read_bytes(); d=json.loads(raw)
 if d.get("proposal_count")!=23: raise ValueError("INCOMPLETE_PROPOSAL_REGISTRY")
 return d,sha256(raw).hexdigest()
def prepare(root=ROOT):
 d,rh=load_registry(root); rows=[]
 for cid,p in sorted(d["proposals"].items()):
  layer="DNA_L0" if cid.startswith("DNA.L0.") else ("DNA_H" if cid.startswith("DNA.H") else "DNA_L1")
  rows.append({"canonical_id":cid,"layer":layer,"candidate_definition":p["candidate_definition"],"evidence_ids":p["evidence_ids"],"proposal_hash":p["proposal_hash"],"dossier_hash":p["dossier_hash"],"evidence_snapshot_hash":p["evidence_snapshot_hash"],"proposal_rationale":p["proposal_rationale"],"decision":None,"decision_rationale":None,"decider_id":None,"decider_role":None,"out_of_band_confirmation":False,"route":"REFOUNDING_OR_FORK_REVIEW_REQUIRED" if layer=="DNA_L0" else "GOVERNED_ADOPTION_DECISION","ordinary_adoption_permitted":layer!="DNA_L0"})
 return {"schema":"oce.p159.occ1a.human_adoption_decision.v1","registry_sha256":rh,"rows":rows,"decision_count":0,"adoption_performed":False,"activation_performed":False,"execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
def decide(workbook,cid,decision,rationale,decider_id,decider_role,out_of_band_confirmation=False):
 if decision not in ALLOWED:return {"accepted":False,"reason":"UNKNOWN_DECISION"}
 rows=[x for x in workbook["rows"] if x["canonical_id"]==cid]
 if len(rows)!=1:return {"accepted":False,"reason":"UNKNOWN_CANONICAL_ID"}
 row=rows[0]
 if row["decision"] is not None:return {"accepted":False,"reason":"DECISION_ALREADY_RECORDED"}
 if not rationale or not decider_id or decider_role not in ("principal_investigator","constitutional_authority"):return {"accepted":False,"reason":"HUMAN_DECISION_METADATA_REQUIRED"}
 if row["layer"]=="DNA_L0" and decision=="ADOPT":return {"accepted":False,"reason":"DNA_L0_REFOUNDING_OR_FORK_REQUIRED"}
 if decision=="ADOPT" and not out_of_band_confirmation:return {"accepted":False,"reason":"OUT_OF_BAND_CONFIRMATION_REQUIRED"}
 row.update({"decision":decision,"decision_rationale":rationale,"decider_id":decider_id,"decider_role":decider_role,"out_of_band_confirmation":bool(out_of_band_confirmation)})
 workbook["decision_count"]=sum(x["decision"] is not None for x in workbook["rows"])
 return {"accepted":True,"decision_hash":h(row),"adoption_performed":False,"activation_performed":False,"execution_performed":False}
def manifest():
 return {"human_decision_required":True,"decision_is_not_adoption":True,"dna_l0_ordinary_adoption_forbidden":True,"machine_decision_permitted":False,"adoption_performed":False,"activation_performed":False,"execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
DECISION_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_human_adoption_decisions.json")
def decision_path(root=ROOT): return Path(root)/DECISION_REL
def load_or_prepare(root=ROOT):
 p=decision_path(root)
 if not p.exists(): return prepare(root)
 w=json.loads(p.read_text(encoding="utf-8")); _,rh=load_registry(root)
 if w.get("registry_sha256")!=rh: raise ValueError("SOURCE_REGISTRY_DRIFT")
 if len(w.get("rows",[]))!=23: raise ValueError("DECISION_WORKBOOK_INCOMPLETE")
 return w
def save_human_decision(root,cid,decision,rationale,decider_id,decider_role,out_of_band_confirmation=False,filesystem_effect_context=None):
 p=decision_path(root); w=load_or_prepare(root)
 result=decide(w,cid,decision,rationale,decider_id,decider_role,out_of_band_confirmation)
 if not result.get("accepted"): return result
 payload=(json.dumps(w,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
 if filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
 filesystem_effect_context.begin()
 if not p.parent.exists(): filesystem_effect_context.execute_path("human_decision_parent_create","FS_CREATE_DIR",p.parent)
 filesystem_effect_context.execute_path("human_decision_write_replace","FS_WRITE_REPLACE_BYTES",p,payload)
 result.update(persisted_human_decision=True,normative_adoption_performed=False,workbook_sha256=sha256(payload).hexdigest())
 return result
def save_human_decisions_batch(root, decisions, decider_id, decider_role, out_of_band_confirmation=False, batch_confirmation="", filesystem_effect_context=None):
    root=Path(root); current=load_or_prepare(root)
    if not isinstance(decisions,list) or not decisions: return {"accepted":False,"reason":"EMPTY_BATCH"}
    if batch_confirmation != "CONFIRM HUMAN DECISIONS ONLY": return {"accepted":False,"reason":"BATCH_CONFIRMATION_REQUIRED"}
    staged=json.loads(json.dumps(current)); seen=set()
    for item in decisions:
        cid=str(item.get("canonical_id",""))
        if cid in seen: return {"accepted":False,"reason":"DUPLICATE_TARGET_IN_BATCH","canonical_id":cid}
        seen.add(cid)
        q=decide(staged,cid,str(item.get("decision","")),str(item.get("rationale","")),str(decider_id),str(decider_role),bool(out_of_band_confirmation))
        if not q.get("accepted"): return {"accepted":False,"reason":q.get("reason","DECISION_REJECTED"),"canonical_id":cid,"committed":False}
    _,rh=load_registry(root)
    if staged.get("registry_sha256") != rh: return {"accepted":False,"reason":"SOURCE_REGISTRY_DRIFT","committed":False}
    p=decision_path(root)
    payload=(json.dumps(staged,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode("utf-8")
    if filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
    filesystem_effect_context.begin()
    if not p.parent.exists(): filesystem_effect_context.execute_path("human_batch_parent_create","FS_CREATE_DIR",p.parent)
    filesystem_effect_context.execute_path("human_decision_write_replace","FS_WRITE_REPLACE_BYTES",p,payload)
    return {"accepted":True,"committed":True,"decision_count":len(decisions),"workbook_sha256":sha256(payload).hexdigest(),"human_decisions_only":True,"adoption_performed":False,"activation_performed":False,"execution_performed":False}
