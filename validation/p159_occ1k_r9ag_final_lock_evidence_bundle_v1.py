from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
MATRIX=ROOT/"validation_artifacts/p159/occ1k_r1/final_lock_coverage_matrix_v1.json"
REG=ROOT/"validation_artifacts/p159/occ1k_r1/occ_invariant_registry_v1.json"
R9AF=ROOT/"validation_artifacts/p159/occ1k_r9af/fl_b1_b12_gate_reconciliation_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ag/final_lock_evidence_bundle_v1.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def build():
 m=load(MATRIX);r=load(REG);g=load(R9AF)
 mids={x["invariant_id"] for x in m["items"]};rids={x["invariant_id"] for x in r["items"] if x.get("retirement_status")=="ACTIVE"}
 refs=sorted({ref for x in m["items"] for ref in x.get("evidence_refs",[])})
 # OCC-1J lifecycle journal is JSONL and is part of the persistence evidence chain.
 life="validation_artifacts/p159/occ1j/normative_lifecycle_journal_v1.jsonl"
 if life not in refs: refs.append(life);refs.sort()
 files=[];missing=[]
 for rel in refs:
  q=ROOT/rel
  if q.is_file(): files.append({"path":rel,"sha256":sha(q),"size":q.stat().st_size})
  else: missing.append(rel)
 first9=all(g["gates"][f"FL-B{i}"]["current_verdict"]=="PASS" for i in range(1,10))
 complete=(mids==rids and not missing and first9)
 return {"schema":"oce.p159.occ1k.r9ag.final_lock_evidence_bundle.v1","milestone":"P159/OCC-1K-R9AG",
 "status":"BUNDLE_MATERIALIZED_COMPLETE" if complete else "BUNDLE_INCOMPLETE",
 "anchors":{"coverage_matrix_sha256":sha(MATRIX),"invariant_registry_sha256":sha(REG),"r9af_sha256":sha(R9AF)},
 "invariant_registry_count":len(rids),"coverage_matrix_count":len(mids),"invariant_sets_equal":mids==rids,
 "evidence_file_count":len(files),"missing_evidence":missing,"evidence_files":files,
 "fl_b1_b9_pass":first9,"authorization_created":False,"execution_performed":False,
 "lock_ready":False,"lock_granted":False,"p160b_opened":False,
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 x=build();OUT.parent.mkdir(parents=True,exist_ok=True);b=(canon(x)+"\n").encode();OUT.write_bytes(b);return x,hashlib.sha256(b).hexdigest()
def main():
 x,h=write();print("R9AG_FINAL_LOCK_EVIDENCE_BUNDLE_MATERIALIZED");print("STATUS="+x["status"])
 print("INVARIANTS="+str(x["invariant_registry_count"]));print("EVIDENCE_FILES="+str(x["evidence_file_count"]))
 print("MISSING_EVIDENCE="+str(len(x["missing_evidence"])));print("BUNDLE_SHA256="+h)
if __name__=="__main__":main()
