from pathlib import Path
import sys,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

# Rebuild the evidence report, then independently require the final crown.
cp=subprocess.run([sys.executable,str(ROOT/"validation/p154_evidence_report.py")],cwd=str(ROOT))
if cp.returncode: raise SystemExit(cp.returncode)
cp=subprocess.run([sys.executable,str(ROOT/"validation/p154_final_adversarial_crown_v2_test.py")],cwd=str(ROOT))
if cp.returncode: raise SystemExit(cp.returncode)

def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
protected=[
 "validation/p154_cardinal_economic_hypotheses.py",
 "evidence/p154/p154_specification.json",
 "evidence/p154/p154_evidence_report.json",
 "validation/p154_functional_test.py",
 "validation/p154_degradation_test.py",
 "validation/p154_adversarial_test.py",
 "validation/p154_adversarial_crown_test.py",
 "validation/p154_final_adversarial_crown_v2_test.py",
 "validation/p154_non_regression_test.py",
 "validation/p154_cwd_independence_test.py",
 "evidence/p005/p005_final_lock.json",
 "evidence/p006/p006_final_lock.json",
 "evidence/p151/p151_final_lock.json",
]
lock={
 "canonical_id":"P154","status":"LOCKED",
 "lock_revision":"FINAL_ADVERSARIAL_CROWN_V2",
 "protected_hashes":{p:sha(p) for p in protected},
 "real_economic_hypotheses_validated":False,
 "scope":"functional falsifiability/evidence-governance contract only",
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
}
lock["lock_sha256"]=hashlib.sha256(json.dumps(lock,sort_keys=True,separators=(",",":")).encode()).hexdigest()
out=ROOT/"evidence/p154/p154_final_lock.json"
if out.exists():
    bak=out.with_suffix(out.suffix+".bak")
    if not bak.exists(): bak.write_bytes(out.read_bytes())
out.write_text(json.dumps(lock,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P154_FINAL_LOCK_V2_OK")
print("lock_sha256="+lock["lock_sha256"])
