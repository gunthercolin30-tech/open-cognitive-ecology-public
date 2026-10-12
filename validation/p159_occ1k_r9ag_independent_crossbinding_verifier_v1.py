from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
BUNDLE=ROOT/"validation_artifacts/p159/occ1k_r9ag/final_lock_evidence_bundle_v1.json"
R9AF=ROOT/"validation_artifacts/p159/occ1k_r9af/fl_b1_b12_gate_reconciliation_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ag/independent_crossbinding_verification_v1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def verify(bundle=None):
 b=bundle if bundle is not None else load(BUNDLE); mism=[];missing=[]
 for e in b.get("evidence_files",[]):
  q=ROOT/e["path"]
  if not q.is_file():missing.append(e["path"])
  elif sha(q)!=e["sha256"]:mism.append(e["path"])
 g=load(R9AF)
 checks={"bundle_complete":b.get("status")=="BUNDLE_MATERIALIZED_COMPLETE",
 "invariant_sets_equal":b.get("invariant_sets_equal") is True,
 "no_declared_missing":b.get("missing_evidence")==[],
 "files_present":not missing,"hashes_match":not mism,
 "r9af_anchor_matches":b.get("anchors",{}).get("r9af_sha256")==sha(R9AF),
 "fl_b1_b9_pass":all(g["gates"][f"FL-B{i}"]["current_verdict"]=="PASS" for i in range(1,10)),
 "no_authority_execution":b.get("authorization_created") is False and b.get("execution_performed") is False,
 "no_lock_p160b":b.get("lock_granted") is False and b.get("p160b_opened") is False}
 ok=all(checks.values())
 return {"schema":"oce.p159.occ1k.r9ag.independent_crossbinding_verification.v1","milestone":"P159/OCC-1K-R9AG",
 "status":"FL_B10_PASS" if ok else "FL_B10_INCONCLUSIVE","checks":checks,"missing_files":missing,"hash_mismatches":mism,
 "fl_b10":"PASS" if ok else "INCONCLUSIVE","historical_r9af_rewritten":False,
 "lock_ready":False,"lock_granted":False,"p160b_opened":False,
 "next_required_step":"R9AH_FL_B11_RESIDUAL_RISK_AND_ASSURANCE_DEBT_REEVALUATION" if ok else "R9AG_EVIDENCE_REPAIR",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 x=verify();OUT.parent.mkdir(parents=True,exist_ok=True);bb=(canon(x)+"\n").encode();OUT.write_bytes(bb);return x,hashlib.sha256(bb).hexdigest()
def main():
 x,h=write();print("P159_OCC1K_R9AG_INDEPENDENT_CROSSBINDING_COMPLETE");print("STATUS="+x["status"])
 print("FL_B10="+x["fl_b10"]);print("MISSING_FILES="+str(len(x["missing_files"])));print("HASH_MISMATCHES="+str(len(x["hash_mismatches"])))
 print("LOCK_READY=false");print("LOCK_GRANTED=false");print("P160B_OPENED=false");print("NEXT="+x["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
