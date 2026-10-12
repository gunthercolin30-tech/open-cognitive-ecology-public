from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
LAYER=ROOT/"validation_artifacts/p159/occ1k_r9p/governed_proven_rule_consumer_binding_layer_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9q/residual_rule_consumer_semantic_resolution_v1.json"
def load():return json.loads(LAYER.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def family(rule_id):
 if rule_id=="GENESIS.G0": return "GENESIS_HUMAN_JUDGMENT"
 if rule_id.startswith("DNA.H"): return "DNA_H"
 if rule_id.startswith("DNA.L0."): return "DNA_L0"
 if rule_id.startswith("DNA.L1."): return "DNA_L1"
 return "OTHER"
def build():
 d=load(); residual=[]
 for r in d["rules"]:
  if r["unresolved_reasons_preserved"]:
   residual.append({"rule_id":r["rule_id"],"family":family(r["rule_id"]),
    "adopted_consumers":r["adopted_consumers"],
    "candidate_not_adopted_consumers":r["candidate_not_adopted_consumers"],
    "unresolved_reasons":r["unresolved_reasons_preserved"]})
 fam={}
 for r in residual:
  fam.setdefault(r["family"],{"rules":[],"candidate_sets":[]})
  fam[r["family"]]["rules"].append(r["rule_id"])
  fam[r["family"]]["candidate_sets"].append(r["candidate_not_adopted_consumers"])
 families=[]
 for k,v in sorted(fam.items()):
  sets={tuple(x) for x in v["candidate_sets"]}
  families.append({"family":k,"rule_count":len(v["rules"]),"rule_ids":v["rules"],
   "uniform_candidate_set":len(sets)==1,"candidate_set":list(next(iter(sets))) if len(sets)==1 else [],
   "resolution_state":"GOVERNED_FAMILY_SEMANTIC_DECISION_REQUIRED"})
 return {"schema":"oce.p159.occ1k.r9q.residual.rule.consumer.semantic.resolution.v1",
  "milestone":"P159/OCC-1K-R9Q","status":"RESIDUALS_GROUPED_GOVERNED_FAMILY_DECISION_REQUIRED",
  "input_layer_sha256":sha(LAYER),"residual_rule_count":len(residual),"residual_rules":residual,
  "families":families,
  "policy":{"family_grouping_is_not_binding":True,"candidate_is_not_binding":True,
   "no_automatic_promotion":True,"unknown_preserved":True},
  "boundaries":{"binding_layer_modified":False,"cnp_modified":False,"runtime_binding_created":False,
   "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
   "fl_b3":"BLOCKED","lock_ready":False,"p160b_opened":False},
  "next_required_step":"R9R_GOVERNED_RESIDUAL_FAMILY_BINDING_DOSSIER",
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write()
 print("P159_OCC1K_R9Q_RESIDUAL_RULE_CONSUMER_SEMANTIC_RESOLUTION_COMPLETE")
 print("STATUS="+d["status"]);print("RESIDUAL_RULES=%d"%d["residual_rule_count"]);print("FAMILIES=%d"%len(d["families"]))
 for f in d["families"]:print("FAMILY_%s=%d"% (f["family"],f["rule_count"]))
 print("AUTOMATIC_PROMOTION=false");print("BINDING_LAYER_MODIFIED=false");print("RUNTIME_BINDING_CREATED=false")
 print("FL_B3=BLOCKED");print("P160B_OPENED=false");print("NEXT="+d["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
