from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
ALLOWED_DECISIONS={"approve","reject","request_revision","abstain"}
ALLOWED_ROLES={"human_reviewer","scientific_reviewer","theory_governance_reviewer","principal_investigator"}

def canon(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def sha(v:Any)->str:return hashlib.sha256(canon(v).encode()).hexdigest()
def readj(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))
def atomic_json(p:Path,v:Any)->None:
 p.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix="."+p.name+".",dir=str(p.parent))
 try:
  with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as h:json.dump(v,h,ensure_ascii=False,sort_keys=True,indent=2);h.write("\n");h.flush();os.fsync(h.fileno())
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def atomic_text(p:Path,t:str)->None:
 p.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix="."+p.name+".",dir=str(p.parent))
 try:
  with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as h:h.write(t);h.flush();os.fsync(h.fileno())
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def latest_with(base:Path,name:str)->Path:
 for d in sorted((x for x in base.iterdir() if x.is_dir()),reverse=True):
  if (d/name).is_file():return d
 raise FileNotFoundError(f"No campaign containing {name} under {base}")
def locate(root:Path=ROOT,campaign:Path|None=None)->dict[str,Path]:
 d1b=latest_with(root/"theory_evolution/ay1_d1b/campaigns","relation_candidates.json")
 d1a=latest_with(root/"theory_evolution/ay1_d1/campaigns","documentary_evidence.json")
 ay1=latest_with(root/"theory_evolution/ay1/campaigns","theory_dependency_graph.json")
 d1c=campaign.resolve() if campaign else latest_with(root/"theory_evolution/ay1_d1c/campaigns","human_review_packet.json")
 return {"d1b":d1b,"d1a":d1a,"ay1":ay1,"d1c":d1c}
def build(root:Path=ROOT,campaign:Path|None=None)->dict[str,Any]:
 from ontology.governed_relation_review_gate import candidate_payload_hash,evidence_payload_hash
 p=locate(root,campaign);cs=readj(p["d1b"]/"relation_candidates.json");ev=readj(p["d1a"]/"documentary_evidence.json");g=readj(p["ay1"]/"theory_dependency_graph.json");packet=readj(p["d1c"]/"human_review_packet.json")
 if packet.get("auto_promotion_performed") is not False or packet.get("validated_count")!=0:raise RuntimeError("campaign is not untouched and pending")
 titles={str(n.get("id") or n.get("document_id")):str(n.get("title") or n.get("name") or n.get("id")) for n in g.get("nodes",[]) if isinstance(n,dict)};idx={x["evidence_id"]:x for x in ev}
 entries=[]
 for i,c in enumerate(sorted(cs,key=lambda x:x["candidate_id"]),1):
  records=[idx[e] for e in c.get("evidence",[]) if e in idx]
  if len(records)!=len(c.get("evidence",[])):raise RuntimeError(f"missing evidence for {c['candidate_id']}")
  entries.append({"position":i,"candidate":c,"source_title":titles.get(c["source"],c["source"]),"target_title":titles.get(c["target"],c["target"]),"evidence_records":records,"candidate_payload_hash":candidate_payload_hash(c),"evidence_payload_hash":evidence_payload_hash(records),"human_decision":{"decision":"","reviewer_id":"","reviewer_role":"principal_investigator","rationale":"","confirmed_source":c["source"],"confirmed_target":c["target"],"confirmed_relation":c["relation"]}})
 w={"schema_version":"1.0.0","campaign_id":packet.get("campaign_id",p["d1c"].name),"status":"GOVERNED_HUMAN_REVIEW_PREPARED","candidate_count":len(entries),"decision_count":0,"auto_promotion_performed":False,"registry_write_performed":False,"source_campaigns":{k:str(v) for k,v in p.items()},"entries":entries,"functional_conclusion_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
 w["workbook_hash"]=sha({k:v for k,v in w.items() if k!="workbook_hash"});return w
def markdown(w:Mapping[str,Any])->str:
 lines=["# AY1-D1c — Campagne humaine gouvernée réelle","",f"- Campaign ID: `{w['campaign_id']}`",f"- Candidates: **{w['candidate_count']}**","- Auto-promotion: **false**","- Décisions autorisées: `approve`, `reject`, `request_revision`, `abstain`.",""]
 for e in w["entries"]:
  c=e["candidate"];lines += [f"## {e['position']}. {c['candidate_id']}","",f"- Source: **{e['source_title']}** (`{c['source']}`)",f"- Relation: **{c['relation']}**",f"- Cible: **{e['target_title']}** (`{c['target']}`)",f"- Confiance classificatoire non décisionnelle: `{c['confidence']}`","","### Preuve documentaire",""]
  for r in e["evidence_records"]:lines += [f"- `{r.get('evidence_id')}` — page `{r.get('page_number')}`","> "+str(r.get("excerpt") or "").replace("\n","\n> "),""]
  lines += ["Renseigner dans le JSON: `decision`, `reviewer_id`, `reviewer_role`, `rationale`.",""]
 return "\n".join(lines)
def prepare(root:Path=ROOT,campaign:Path|None=None)->Path:
 w=build(root,campaign);d=Path(w["source_campaigns"]["d1c"])/"human_review";d.mkdir(parents=True,exist_ok=True);atomic_json(d/"governed_review_workbook.json",w);atomic_text(d/"governed_review_workbook.md",markdown(w));atomic_json(d/"human_review_manifest.json",{"campaign_id":w["campaign_id"],"status":w["status"],"candidate_count":w["candidate_count"],"decision_count":0,"validated_count":0,"auto_promotion_performed":False,"registry_write_performed":False,"workbook_hash":w["workbook_hash"]});return d
def validate_entry(e:Mapping[str,Any])->dict[str,Any]:
 h=e.get("human_decision",{});d=str(h.get("decision") or "").strip().lower();rid=str(h.get("reviewer_id") or "").strip();role=str(h.get("reviewer_role") or "").strip();rat=str(h.get("rationale") or "").strip();c=e["candidate"]
 if d not in ALLOWED_DECISIONS:raise ValueError(f"missing/unsupported decision for {c['candidate_id']}")
 if not rid or not rat:raise ValueError("reviewer_id and rationale required")
 if role not in ALLOWED_ROLES:raise PermissionError("unauthorized reviewer role")
 cs=str(h.get("confirmed_source") or "");ct=str(h.get("confirmed_target") or "");cr=str(h.get("confirmed_relation") or "").lower()
 if d=="approve" and (cs!=c["source"] or ct!=c["target"] or cr!=c["relation"]):raise ValueError("approval confirmation mismatch")
 core={"candidate_id":c["candidate_id"],"decision":d,"reviewer_id":rid,"reviewer_role":role,"rationale":rat,"confirmed_source":cs,"confirmed_target":ct,"confirmed_relation":cr,"candidate_payload_hash":e["candidate_payload_hash"],"evidence_payload_hash":e["evidence_payload_hash"]};core["decision_id"]="decision:"+sha(core)[:24];return core
def apply(path:Path,root:Path=ROOT)->dict[str,Any]:
 from ontology.governed_relation_review_gate import GovernedRelationReviewGate
 from ontology.validated_relation_registry import ValidatedRelationRegistry
 w=readj(path.resolve());base=build(root,Path(w["source_campaigns"]["d1c"]));
 if w.get("workbook_hash")!=base.get("workbook_hash"):raise RuntimeError("workbook baseline hash mismatch")
 byid={x["candidate"]["candidate_id"]:x for x in base["entries"]};results=[];gate=GovernedRelationReviewGate();registry=ValidatedRelationRegistry(root)
 for e in w["entries"]:
  cid=e["candidate"]["candidate_id"];b=byid.get(cid)
  if not b:raise RuntimeError("unknown candidate")
  for f in ("candidate","source_title","target_title","evidence_records","candidate_payload_hash","evidence_payload_hash"):
   if e.get(f)!=b.get(f):raise RuntimeError(f"immutable field changed: {f}")
  dec=validate_entry(e);gr=gate.step(inputs={"candidate":e["candidate"],"decision":dec,"evidence_records":e["evidence_records"]},persist=False);rr=registry.step(inputs={"gate_result":gr},persist=True);results.append({"candidate_id":cid,"decision":dec["decision"],"decision_id":dec["decision_id"],"approved":gr["approval_authorized"],"registry_result":rr})
 out={"campaign_id":w["campaign_id"],"status":"GOVERNED_HUMAN_REVIEW_APPLIED","decision_count":len(results),"approved_count":sum(x["approved"] for x in results),"non_approved_count":sum(not x["approved"] for x in results),"auto_promotion_performed":False,"registry_write_performed":True,"decisions":results};out["result_hash"]=sha(out);atomic_json(path.parent/"human_review_result.json",out);return out
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("action",choices=("prepare","apply","status"));p.add_argument("--campaign-dir",type=Path);p.add_argument("--workbook",type=Path);a=p.parse_args()
 if a.action=="prepare":
  d=prepare(ROOT,a.campaign_dir);print("AY1_D1C_GOVERNED_HUMAN_REVIEW_PREPARED");print(f"review_dir={d}");print(f"workbook_json={d/'governed_review_workbook.json'}");print(f"workbook_markdown={d/'governed_review_workbook.md'}");print("auto_promotion_performed=false");print("registry_write_performed=false");return 0
 if a.action=="apply":
  if not a.workbook:p.error("--workbook required")
  r=apply(a.workbook,ROOT);print("AY1_D1C_GOVERNED_HUMAN_REVIEW_APPLIED");print(f"decision_count={r['decision_count']}");print(f"approved_count={r['approved_count']}");print(f"non_approved_count={r['non_approved_count']}");return 0
 d=locate(ROOT,a.campaign_dir)["d1c"]/"human_review/human_review_manifest.json";print(d.read_text() if d.is_file() else json.dumps({"status":"NOT_PREPARED"}));return 0
if __name__=="__main__":raise SystemExit(main())
