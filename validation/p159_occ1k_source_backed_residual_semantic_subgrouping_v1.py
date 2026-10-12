from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R9S=ROOT/"validation_artifacts/p159/occ1k_r9s/source_backed_residual_family_semantic_evidence_audit_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9t/source_backed_residual_semantic_subgrouping_v1.json"
def load():return json.loads(R9S.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def signature(m):
 return (m.get("source_object_id"),tuple(m.get("evidence_ids",[])),m.get("formalization"),m.get("semantic_status"))
def build():
 s=load(); groups=[]
 for f in s["family_audits"]:
  buckets={}
  for m in f["members"]:buckets.setdefault(signature(m),[]).append(m["rule_id"])
  for i,(sig,ids) in enumerate(sorted(buckets.items(),key=lambda x:(str(x[0]),x[1])),1):
   groups.append({"subgroup_id":f["family"]+"::SG%02d"%i,"parent_family":f["family"],
    "rule_ids":sorted(ids),"rule_count":len(ids),
    "source_semantic_signature":{"source_object_id":sig[0],"evidence_ids":list(sig[1]),"formalization":sig[2],"semantic_status":sig[3]},
    "consumer_binding_state":"NOT_DERIVED","consumer_binding_candidates":[],
    "reason":"SUBGROUPING_BY_CANONICAL_SOURCE_SEMANTIC_SIGNATURE_ONLY"})
 return {"schema":"oce.p159.occ1k.r9t.source.backed.residual.semantic.subgrouping.v1",
  "milestone":"P159/OCC-1K-R9T","status":"SOURCE_BACKED_SUBGROUPING_COMPLETE_CONSUMER_BINDING_NOT_DERIVED",
  "input_r9s_sha256":sha(R9S),"rules":sum(x["rule_count"] for x in groups),"subgroups":groups,
  "counts":{"subgroups":len(groups),"multi_rule_subgroups":sum(x["rule_count"]>1 for x in groups),
   "singleton_subgroups":sum(x["rule_count"]==1 for x in groups),"consumer_bindings_derived":0},
  "policy":{"subgroup_signature_is_not_consumer_binding":True,"no_keyword_mapping":True,
   "no_automatic_consumer_assignment":True,"unknown_preserved":True},
  "boundaries":{"rule_bindings_modified":False,"cnp_modified":False,"runtime_binding_created":False,
   "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
   "fl_b3":"BLOCKED","lock_ready":False,"p160b_opened":False},
  "next_required_step":"R9U_SUBGROUP_TO_CONSUMER_SOURCE_EVIDENCE_RESOLUTION",
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();c=d["counts"]
 print("P159_OCC1K_R9T_SOURCE_BACKED_RESIDUAL_SEMANTIC_SUBGROUPING_COMPLETE")
 print("STATUS="+d["status"]);print("RULES=%d/24"%d["rules"]);print("SUBGROUPS=%d"%c["subgroups"])
 print("MULTI_RULE_SUBGROUPS=%d"%c["multi_rule_subgroups"]);print("SINGLETON_SUBGROUPS=%d"%c["singleton_subgroups"])
 print("CONSUMER_BINDINGS_DERIVED=0");print("RULE_BINDINGS_MODIFIED=false");print("RUNTIME_BINDING_CREATED=false")
 print("FL_B3=BLOCKED");print("P160B_OPENED=false");print("NEXT="+d["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
