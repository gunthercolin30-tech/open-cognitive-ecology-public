from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R9T=ROOT/"validation_artifacts/p159/occ1k_r9t/source_backed_residual_semantic_subgrouping_v1.json"
CONTRACT=ROOT/"validation_artifacts/p159/occ1k_r9m/governed_consumer_semantic_contract_v1.json"
SOURCES=[ROOT/"normative/occ1a/genesis/genesis.yaml",ROOT/"normative/occ1a/dna/dna_h.yaml",ROOT/"normative/occ1a/dna/dna_l0.yaml",ROOT/"normative/occ1a/dna/dna_l1.yaml"]
OUT=ROOT/"validation_artifacts/p159/occ1k_r9u/subgroup_consumer_source_evidence_resolution_v1.json"
DIRECT={
 "F9":["AuthorizationEngine"],
 "F10":["RecoveryEngine"],
 "F11":["AssuranceEngine"],
 "F16":["AssuranceEngine"],
}
CONTEXTUAL={
 "F1":["AuthorizationEngine"],"F2":["CapabilityGate"],"F3":["CapabilityGate"],"F4":["CapabilityGate"],
 "F5":["CapabilityGate"],"F6":["CapabilityGate"],"F7":["CapabilityGate"],"F8":["CapabilityGate"],
 "F12":["CapabilityGate"],"F12+F17":["CapabilityGate"],"F13":["CapabilityGate"],
 "F14":["AssuranceEngine"],"F15":["AssuranceEngine"],
}
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norms():
 out={}
 for p in SOURCES:
  for n in load(p)["norms"]:out[n["canonical_id"]]=n
 return out
def build():
 t=load(R9T); con=load(CONTRACT); roles={x["consumer"]:x["semantic_role"] for x in con["responsibilities"]}
 ns=norms(); rows=[]
 for g in t["subgroups"]:
  evid=set(); texts=[]
  for rid in g["rule_ids"]:
   n=ns[rid]; evid.update(n.get("evidence_ids",[])); texts.append({"rule_id":rid,"text":n.get("text")})
  key=g["source_semantic_signature"].get("source_object_id")
  if key in DIRECT: strength="DIRECT_SEMANTIC_ROLE_MATCH"; candidates=DIRECT[key]
  elif key in CONTEXTUAL: strength="CONTEXTUAL_SEMANTIC_MATCH_REQUIRES_GOVERNED_REVIEW"; candidates=CONTEXTUAL[key]
  else: strength="UNRESOLVED"; candidates=[]
  rows.append({"subgroup_id":g["subgroup_id"],"rule_ids":g["rule_ids"],"source_object_id":key,
   "evidence_ids":sorted(evid),"normative_texts":texts,"evidence_strength":strength,
   "candidate_consumers":candidates,"candidate_role_texts":{c:roles[c] for c in candidates},
   "binding_adopted":False})
 counts={k:sum(x["evidence_strength"]==k for x in rows) for k in ("DIRECT_SEMANTIC_ROLE_MATCH","CONTEXTUAL_SEMANTIC_MATCH_REQUIRES_GOVERNED_REVIEW","UNRESOLVED")}
 return {"schema":"oce.p159.occ1k.r9u.subgroup.consumer.source.evidence.resolution.v1","milestone":"P159/OCC-1K-R9U",
  "status":"SOURCE_EVIDENCE_RESOLUTION_COMPLETE_GOVERNED_REVIEW_REQUIRED",
  "inputs":{"r9t_sha256":sha(R9T),"contract_sha256":sha(CONTRACT),"source_hashes":{str(p.relative_to(ROOT)):sha(p) for p in SOURCES}},
  "subgroups":rows,"counts":{"subgroups":len(rows),**counts},
  "method":{"direct_matches_are_semantic_role_matches_not_bindings":True,
   "contextual_matches_require_governed_review":True,"keyword_only_mapping":False,
   "candidate_is_not_binding":True,"unknown_preserved":True},
  "boundaries":{"rule_bindings_modified":False,"cnp_modified":False,"runtime_binding_created":False,
   "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
   "fl_b3":"BLOCKED","lock_ready":False,"p160b_opened":False},
  "next_required_step":"R9V_GOVERNED_DIRECT_BINDING_ADOPTION_DOSSIER",
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();c=d["counts"]
 print("P159_OCC1K_R9U_SUBGROUP_CONSUMER_SOURCE_EVIDENCE_RESOLUTION_COMPLETE")
 print("STATUS="+d["status"]);print("SUBGROUPS=%d/21"%c["subgroups"])
 print("DIRECT_SEMANTIC_ROLE_MATCH=%d"%c["DIRECT_SEMANTIC_ROLE_MATCH"])
 print("CONTEXTUAL_REVIEW_REQUIRED=%d"%c["CONTEXTUAL_SEMANTIC_MATCH_REQUIRES_GOVERNED_REVIEW"])
 print("UNRESOLVED=%d"%c["UNRESOLVED"])
 print("BINDINGS_ADOPTED=0");print("KEYWORD_ONLY_MAPPING=false");print("RULE_BINDINGS_MODIFIED=false")
 print("RUNTIME_BINDING_CREATED=false");print("FL_B3=BLOCKED");print("P160B_OPENED=false")
 print("NEXT="+d["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
