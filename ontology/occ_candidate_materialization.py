from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any,Mapping
PRIMITIVE="occ_candidate_materialization";VERSION="P159-OCC1A-candidate-materialization-v1"
STATUS="EVIDENCE_DOSSIERS_MATERIALIZED_NO_NUMBERED_BINDING_PROPOSED"
DNA_TARGETS=tuple([f"DNA.H{i}" for i in range(1,10)]+[f"DNA.L0.{i}" for i in range(1,7)]+[f"DNA.L1.{i}" for i in range(1,9)])
LAYER_TOKEN={"DNA_H":"DNA_H","DNA_L0":"DNA_L0","DNA_L1":"DNA_L1"}
def _can(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _sha(v):return hashlib.sha256(_can(v).encode()).hexdigest()
def _shaf(p:Path):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1048576),b""):h.update(c)
 return h.hexdigest()
def _layer(cid):
 return "DNA_L0" if ".L0." in cid else ("DNA_L1" if ".L1." in cid else "DNA_H")
def load_historical(root:Path):
 p=root/"validation/evidence/p155_constitutional_architecture_v2/p155_historical_dna_semantic_binding_v2.json"
 raw=json.loads(p.read_text(encoding="utf-8"));b=raw.get("bindings") or {}
 if set(b)!=set(f"F{i}" for i in range(1,19)):raise ValueError("P155 F1-F18 binding set incomplete")
 return p,b
def build_dossiers(root:Path):
 root=root.resolve();p,b=load_historical(root)
 dossiers=[]
 for cid in DNA_TARGETS:
  layer=_layer(cid);token=LAYER_TOKEN[layer];alts=[]
  for fid in sorted(b,key=lambda x:int(x[1:])):
   rec=b[fid];targets=tuple(rec.get("canonical_targets") or ())
   if token in targets:
    alts.append({"historical_id":fid,"definition":rec.get("definition"),"justification":rec.get("justification"),
                 "canonical_targets":list(targets),"source":rec.get("source"),"source_sha256":rec.get("source_sha256"),
                 "semantic_coverage_reviewed":bool(rec.get("semantic_coverage_reviewed")),
                 "distinct_normative_object_preserved":rec.get("distinct_normative_object_preserved"),
                 "not_reduced_to_human_welfare":rec.get("not_reduced_to_human_welfare")})
  d={"canonical_id":cid,"layer":layer,"evidence_status":"LAYER_COMPATIBLE_ALTERNATIVES_ONLY",
     "numbered_semantic_binding_status":"UNRESOLVED",
     "machine_selected_historical_id":None,"machine_candidate_definition":None,"machine_ranking_performed":False,
     "human_governed_materialization_required":True,"layer_compatible_historical_sources":alts,
     "warning":"P155 proves broad-layer compatibility only; it does not define this numbered DNA target. No alternative is selected, ranked, merged or adopted by the machine."}
  d["dossier_hash"]=_sha({k:v for k,v in d.items() if k!="dossier_hash"});dossiers.append(d)
 return {"schema":"oce.p159.occ1a.candidate-materialization.v1","status":STATUS,"dossier_count":23,
         "dossiers":dossiers,"historical_source_sha256":_shaf(p),"automatic_numbered_binding":False,
         "automatic_ranking":False,"automatic_merging":False,"automatic_adoption":False,
         "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
         "functional_conclusion_only":True,"phenomenology_undetermined":True}
def validate(materialized:Mapping[str,Any]):
 if materialized.get("dossier_count")!=23 or len(materialized.get("dossiers") or [])!=23:raise ValueError("23 dossiers required")
 seen=set()
 for d in materialized["dossiers"]:
  cid=d.get("canonical_id")
  if cid not in DNA_TARGETS or cid in seen:raise ValueError("unknown/duplicate target")
  seen.add(cid)
  if d.get("numbered_semantic_binding_status")!="UNRESOLVED":raise ValueError("numbered binding manufactured")
  if d.get("machine_selected_historical_id") is not None or d.get("machine_candidate_definition") is not None:raise ValueError("machine selection forbidden")
  if d.get("machine_ranking_performed") is not False:raise ValueError("machine ranking forbidden")
  x={k:v for k,v in d.items() if k!="dossier_hash"}
  if d.get("dossier_hash")!=_sha(x):raise ValueError("dossier drift")
  token=LAYER_TOKEN[d["layer"]]
  for a in d["layer_compatible_historical_sources"]:
   if token not in a["canonical_targets"]:raise ValueError("cross-layer alternative")
 return True
def manifest():
 return {"primitive":PRIMITIVE,"version":VERSION,"status":STATUS,"dossier_count":23,
         "machine_numbered_binding_permitted":False,"machine_ranking_permitted":False,
         "machine_adoption_permitted":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
         "functional_conclusion_only":True,"phenomenology_undetermined":True}
