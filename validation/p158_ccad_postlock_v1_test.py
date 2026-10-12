from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/"validation/evidence/p158_ccad_final_lock"
R=E/"CCAD_FINAL_LOCK_REPORT.json"; M=E/"MANIFEST.sha256"; S=E/"SCOPE_AND_INVALIDATION.json"; B=E/"CCAD_FINAL_LOCK_BUNDLE_v1.zip"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(v,n): assert v,n; print(n)
def main():
 r=json.loads(R.read_text()); s=json.loads(S.read_text())
 check(r["status"] in {"FINAL_LOCK_CANDIDATE","LOCKED"},"P158_POSTLOCK_STATE_OK")
 check(r["adversarial"]=="PASS_36_OF_36" and r["independent_oracle_poisoning_controls"]=="PASS_36_OF_36","P158_POSTLOCK_ADV36_OK")
 check(r["p158_meta_tests"]=="PASS","P158_POSTLOCK_META_GUARDS_OK")
 check(r["schema_integrity"]=="PASS" and r["schema_corruption_detection"]=="PASS","P158_POSTLOCK_SCHEMA_INTEGRITY_OK")
 check(r["hash_integrity"]=="PASS" and r["hash_drift_detection"]=="PASS","P158_POSTLOCK_HASH_INTEGRITY_OK")
 check(r["bundle_reproducible"] is True,"P158_POSTLOCK_BUNDLE_REPRODUCIBLE_OK")
 check(sha(M)==r["manifest_sha256"] and sha(S)==r["scope_invalidation_sha256"] and sha(B)==r["bundle_sha256"],"P158_POSTLOCK_LOCK_ARTIFACT_HASHES_OK")
 lines=[x for x in M.read_text().splitlines() if x.strip()]; check(len(lines)==r["manifest_entry_count"],"P158_POSTLOCK_MANIFEST_COUNT_OK")
 for line in lines:
  expected,rel=line.split("  ",1); p=ROOT/rel
  assert p.is_file() and sha(p)==expected,rel
 print("P158_POSTLOCK_ALL_PROTECTED_HASHES_OK")
 with zipfile.ZipFile(B) as z:
  names=z.namelist()
  check(len(names)==r["bundle_member_count"] and names==sorted(names) and len(names)==len(set(names)),"P158_POSTLOCK_BUNDLE_MEMBERS_OK")
  check("validation/evidence/p158_ccad_final_lock/MANIFEST.sha256" in names,"P158_POSTLOCK_BUNDLE_MANIFEST_PRESENT_OK")
 check(s["authority"]["creates_sovereignty"] is False and s["authority"]["creates_authorization"] is False and s["authority"]["executes_action"] is False,"P158_POSTLOCK_NON_SOVEREIGN_OK")
 check(r["runtime_enforcement_proven"] is False and r["real_execution_enabled"] is False and r["global_oce_safety_proven"] is False,"P158_POSTLOCK_SCOPE_LIMITS_OK")
 check(r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True,"P158_POSTLOCK_EPISTEMIC_BOUNDARY_OK")
 check(r["p159_opened"] is False and s["p159_opened"] is False,"P158_POSTLOCK_P159_NOT_OPENED_OK")
 print("P158_CCAD_POSTLOCK_V1_OK")
if __name__=="__main__": main()
