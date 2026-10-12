from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R9R=ROOT/"validation_artifacts/p159/occ1k_r9r/governed_residual_family_binding_dossier_v1.json"
SOURCES=[
 ROOT/"normative/occ1a/genesis/genesis.yaml",
 ROOT/"normative/occ1a/dna/dna_h.yaml",
 ROOT/"normative/occ1a/dna/dna_l0.yaml",
 ROOT/"normative/occ1a/dna/dna_l1.yaml"]
OUT=ROOT/"validation_artifacts/p159/occ1k_r9s/source_backed_residual_family_semantic_evidence_audit_v1.json"
def jload(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build():
 r=jload(R9R); norms={}
 for p in SOURCES:
  for n in jload(p)["norms"]: norms[n["canonical_id"]]=dict(n,source_path=str(p.relative_to(ROOT)))
 rows=[]; family_audits=[]
 for f in r["families"]:
  members=[]
  for rid in f["rule_ids"]:
   n=norms.get(rid)
   if n is None: raise RuntimeError("MISSING_CANONICAL_NORM:"+rid)
   members.append({"rule_id":rid,"source_object_id":n.get("source_object_id"),
    "evidence_ids":n.get("evidence_ids",[]),"formalization":n.get("formalization"),
    "semantic_status":n.get("semantic_status"),"text_present":n.get("text") is not None,
    "source_path":n["source_path"]})
  signatures={(x["source_object_id"],tuple(x["evidence_ids"]),x["formalization"],x["semantic_status"]) for x in members}
  homogeneous=len(signatures)==1
  family_audits.append({"family":f["family"],"rule_count":len(members),"members":members,
    "semantic_signature_count":len(signatures),"source_semantically_homogeneous":homogeneous,
    "family_level_consumer_binding_safe":False,
    "reason":"FAMILY_GROUPING_ALONE_NOT_SUFFICIENT_FOR_CONSUMER_BINDING" if homogeneous else "SOURCE_SEMANTICS_HETEROGENEOUS_REQUIRES_SUBGROUP_OR_RULE_LEVEL_REVIEW"})
  rows.extend(members)
 return {"schema":"oce.p159.occ1k.r9s.source.backed.residual.family.semantic.evidence.audit.v1",
  "milestone":"P159/OCC-1K-R9S","status":"SOURCE_EVIDENCE_AUDITED_REFINEMENT_REQUIRED",
  "inputs":{"r9r_sha256":sha(R9R),"canonical_source_hashes":{str(p.relative_to(ROOT)):sha(p) for p in SOURCES}},
  "rules_audited":len(rows),"family_audits":family_audits,
  "counts":{"families":len(family_audits),"homogeneous_families":sum(x["source_semantically_homogeneous"] for x in family_audits),
   "heterogeneous_families":sum(not x["source_semantically_homogeneous"] for x in family_audits),
   "safe_family_bindings":sum(x["family_level_consumer_binding_safe"] for x in family_audits)},
  "policy":{"source_text_not_keyword_mapped_to_consumer":True,"family_membership_not_binding":True,
   "semantic_signature_not_binding":True,"unknown_preserved":True},
  "boundaries":{"rule_bindings_modified":False,"cnp_modified":False,"runtime_binding_created":False,
   "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
   "fl_b3":"BLOCKED","lock_ready":False,"p160b_opened":False},
  "next_required_step":"R9T_SOURCE_BACKED_RESIDUAL_SEMANTIC_SUBGROUPING",
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();c=d["counts"]
 print("P159_OCC1K_R9S_SOURCE_BACKED_RESIDUAL_FAMILY_SEMANTIC_EVIDENCE_AUDIT_COMPLETE")
 print("STATUS="+d["status"]);print("RULES_AUDITED=%d/24"%d["rules_audited"]);print("FAMILIES=%d/4"%c["families"])
 print("HOMOGENEOUS_FAMILIES=%d"%c["homogeneous_families"]);print("HETEROGENEOUS_FAMILIES=%d"%c["heterogeneous_families"])
 print("SAFE_FAMILY_BINDINGS=%d"%c["safe_family_bindings"]);print("KEYWORD_CONSUMER_MAPPING=false")
 print("RULE_BINDINGS_MODIFIED=false");print("RUNTIME_BINDING_CREATED=false");print("FL_B3=BLOCKED");print("P160B_OPENED=false")
 print("NEXT="+d["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
