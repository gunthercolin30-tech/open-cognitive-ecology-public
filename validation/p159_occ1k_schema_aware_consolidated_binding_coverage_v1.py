from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1k_r9p/governed_proven_rule_consumer_binding_layer_v1.json"
W=ROOT/"validation_artifacts/p159/occ1k_r9w/governed_direct_rule_consumer_binding_layer_v1.json"
Z=ROOT/"validation_artifacts/p159/occ1k_r9z/governed_contextual_rule_consumer_binding_layer_v1.json"
AB=ROOT/"validation_artifacts/p159/occ1k_r9ab/governed_genesis_g0_ccad_binding_layer_v1.json"
CNP=ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
OLD=ROOT/"validation_artifacts/p159/occ1k_r9ac/consolidated_binding_coverage_precheck_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ac2/schema_aware_consolidated_binding_coverage_v1.json"
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rule_ids(v):
 out=set()
 def w(x):
  if isinstance(x,dict):
   for k,y in x.items():
    if k in ("rule_id","canonical_id") and isinstance(y,str) and y.startswith(("GENESIS.","DNA.","CCAD.")):out.add(y)
    w(y)
  elif isinstance(x,list):
   for y in x:w(y)
 w(v);return out
def consumers(v):
 out=set()
 def w(x):
  if isinstance(x,dict):
   for k,y in x.items():
    if k in ("consumers","consumer_bindings","consumer") and isinstance(y,str):out.add(y)
    elif k in ("consumers","consumer_bindings") and isinstance(y,list):out.update(z for z in y if isinstance(z,str))
    w(y)
  elif isinstance(x,list):
   for y in x:w(y)
 w(v);return out
def build():
 layers={"R9P":load(P),"R9W":load(W),"R9Z":load(Z),"R9AB":load(AB)}
 expected=rule_ids(load(CNP))
 if len(expected)!=48:raise RuntimeError("CNP_RULE_UNIVERSE_NOT_48:"+str(len(expected)))
 coverage={}
 for name,obj in layers.items():
  ids=rule_ids(obj)
  for rid in ids:
   coverage.setdefault(rid,{"layers":[],"consumers":[]})["layers"].append(name)
  # Schema-aware consumer extraction for R9P rules; other layers already encode consumer fields.
  if name=="R9P":
   for r in obj.get("rules",[]):
    rid=r.get("rule_id")
    if rid in expected:
     cs=r.get("adopted_consumers",r.get("proven_consumers",r.get("consumers",[])))
     if isinstance(cs,str):cs=[cs]
     coverage.setdefault(rid,{"layers":[],"consumers":[]})["consumers"].extend(cs or [])
  else:
   def walk(x):
    if isinstance(x,dict):
     rid=x.get("rule_id")
     if rid in expected:
      cs=x.get("consumers",x.get("consumer_bindings",x.get("consumer",[])))
      if isinstance(cs,str):cs=[cs]
      if isinstance(cs,list):coverage.setdefault(rid,{"layers":[],"consumers":[]})["consumers"].extend(cs)
     for y in x.values():walk(y)
    elif isinstance(x,list):
     for y in x:walk(y)
   walk(obj)
 for e in coverage.values():
  e["layers"]=sorted(set(e["layers"]));e["consumers"]=sorted(set(e["consumers"]))
 covered=set(coverage)&expected;missing=sorted(expected-covered);unexpected=sorted(set(coverage)-expected)
 no_consumer=sorted(r for r in covered if not coverage[r]["consumers"])
 complete=len(covered)==48 and not missing and not unexpected and not no_consumer
 return {"schema":"oce.p159.occ1k.r9ac2.schema.aware.consolidated.binding.coverage.v1","milestone":"P159/OCC-1K-R9AC2",
 "status":"CONSOLIDATED_48_RULE_BINDING_MAP_READY" if complete else "CONSOLIDATION_REQUIRES_FURTHER_SCHEMA_RESOLUTION",
 "inputs":{k.lower()+"_sha256":sha(v) for k,v in {"R9P":P,"R9W":W,"R9Z":Z,"R9AB":AB,"CNP":CNP,"R9AC":OLD}.items()},
 "counts":{"expected_rules":48,"covered_rules":len(covered),"missing_rules":len(missing),"unexpected_rules":len(unexpected),"covered_without_consumer":len(no_consumer)},
 "missing_rule_ids":missing,"unexpected_rule_ids":unexpected,"covered_without_consumer_ids":no_consumer,
 "consolidated_rule_map":dict(sorted(coverage.items())),"coverage_complete":complete,"s10_replay_authorized":complete,
 "diagnostic_correction":{"prior_r9ac_schema_assumption":"bindings[] only","r9p_actual_rule_container":"rules[]","historical_artifact_rewritten":False},
 "boundaries":{"rule_bindings_modified":False,"runtime_binding_created":False,"runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,"fl_b3":"BLOCKED_PENDING_INDEPENDENT_S10_REPLAY","p160b_opened":False},
 "next_required_step":"R9AD_INDEPENDENT_S10_REPLAY" if complete else "R9AC3_SCHEMA_GAP_RESOLUTION"}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b);return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();c=d["counts"]
 print("P159_OCC1K_R9AC2_SCHEMA_AWARE_CONSOLIDATED_BINDING_COVERAGE_COMPLETE");print("STATUS="+d["status"])
 for k,v in c.items():print(k.upper()+"="+str(v))
 print("COVERAGE_COMPLETE="+str(d["coverage_complete"]).lower());print("S10_REPLAY_AUTHORIZED="+str(d["s10_replay_authorized"]).lower())
 print("HISTORICAL_R9AC_REWRITTEN=false");print("RULE_BINDINGS_MODIFIED=false");print("FL_B3=BLOCKED_PENDING_INDEPENDENT_S10_REPLAY");print("P160B_OPENED=false")
 print("NEXT="+d["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
