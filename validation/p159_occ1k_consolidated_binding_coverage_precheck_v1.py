from pathlib import Path
import json, hashlib
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1k_r9p/governed_proven_rule_consumer_binding_layer_v1.json"
W=ROOT/"validation_artifacts/p159/occ1k_r9w/governed_direct_rule_consumer_binding_layer_v1.json"
Z=ROOT/"validation_artifacts/p159/occ1k_r9z/governed_contextual_rule_consumer_binding_layer_v1.json"
AB=ROOT/"validation_artifacts/p159/occ1k_r9ab/governed_genesis_g0_ccad_binding_layer_v1.json"
CNP=ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ac/consolidated_binding_coverage_precheck_v1.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ids_from_cnp(x):
 candidates=[]
 def walk(v):
  if isinstance(v,dict):
   for k,val in v.items():
    if k in ("rule_id","canonical_id") and isinstance(val,str) and (val.startswith("GENESIS.") or val.startswith("DNA.") or val.startswith("CCAD.")):
     candidates.append(val)
    walk(val)
  elif isinstance(v,list):
   for q in v: walk(q)
 walk(x)
 return set(candidates)
def bindings(layer):
 out=[]
 if isinstance(layer.get("bindings"),list): out+=layer["bindings"]
 if isinstance(layer.get("binding"),dict): out+=[layer["binding"]]
 return out
def build():
 layers={"R9P":load(P),"R9W":load(W),"R9Z":load(Z),"R9AB":load(AB)}
 cnp=load(CNP); expected=ids_from_cnp(cnp)
 if len(expected)!=48: raise RuntimeError("CNP_RULE_UNIVERSE_NOT_48:"+str(len(expected)))
 by_rule={}
 for lname,layer in layers.items():
  for b in bindings(layer):
   rid=b["rule_id"]; cs=b.get("consumers") or b.get("consumer_bindings") or b.get("consumer")
   if isinstance(cs,str): cs=[cs]
   if not isinstance(cs,list) or not cs: raise RuntimeError("EMPTY_CONSUMER_BINDING:"+lname+":"+rid)
   e=by_rule.setdefault(rid,{"layers":[],"consumers":[]})
   e["layers"].append(lname);e["consumers"].extend(cs)
 for rid,e in by_rule.items(): e["layers"]=sorted(set(e["layers"]));e["consumers"]=sorted(set(e["consumers"]))
 covered=set(by_rule); missing=sorted(expected-covered); unexpected=sorted(covered-expected)
 duplicate=sorted(r for r,e in by_rule.items() if len(e["layers"])>1)
 multi=sorted(r for r,e in by_rule.items() if len(e["consumers"])>1)
 complete=(not missing and not unexpected and len(covered)==48)
 return {"schema":"oce.p159.occ1k.r9ac.consolidated.binding.coverage.precheck.v1","milestone":"P159/OCC-1K-R9AC",
 "status":"CONSOLIDATED_BINDING_COVERAGE_COMPLETE_S10_REPLAY_READY" if complete else "CONSOLIDATED_BINDING_COVERAGE_INCOMPLETE",
 "inputs":{k.lower()+"_sha256":sha(v) for k,v in {"R9P":P,"R9W":W,"R9Z":Z,"R9AB":AB,"CNP":CNP}.items()},
 "counts":{"expected_rules":len(expected),"covered_rules":len(covered),"missing_rules":len(missing),"unexpected_rules":len(unexpected),
 "duplicate_rule_layers":len(duplicate),"multi_consumer_rules":len(multi)},
 "expected_rule_ids":sorted(expected),"covered_rule_ids":sorted(covered),"missing_rule_ids":missing,"unexpected_rule_ids":unexpected,
 "duplicate_rule_layer_ids":duplicate,"multi_consumer_rule_ids":multi,"consolidated_bindings":dict(sorted(by_rule.items())),
 "coverage_complete":complete,"s10_replay_authorized":complete,
 "boundaries":{"source_modified":False,"cnp_modified":False,"rule_bindings_modified":False,"runtime_binding_created":False,
 "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
 "fl_b3":"BLOCKED_PENDING_INDEPENDENT_S10_REPLAY","lock_ready":False,"p160b_opened":False},
 "next_required_step":"R9AD_INDEPENDENT_S10_REPLAY" if complete else "R9AC_GAP_RESOLUTION",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();c=d["counts"]
 print("P159_OCC1K_R9AC_CONSOLIDATED_BINDING_COVERAGE_PRECHECK_COMPLETE");print("STATUS="+d["status"])
 for k in ("expected_rules","covered_rules","missing_rules","unexpected_rules","duplicate_rule_layers","multi_consumer_rules"):print(k.upper()+"="+str(c[k]))
 print("COVERAGE_COMPLETE="+str(d["coverage_complete"]).lower());print("S10_REPLAY_AUTHORIZED="+str(d["s10_replay_authorized"]).lower())
 print("RULE_BINDINGS_MODIFIED=false");print("RUNTIME_BINDING_CREATED=false");print("FL_B3=BLOCKED_PENDING_INDEPENDENT_S10_REPLAY")
 print("P160B_OPENED=false");print("NEXT="+d["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
