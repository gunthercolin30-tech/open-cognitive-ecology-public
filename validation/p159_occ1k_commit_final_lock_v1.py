import hashlib,os
from pathlib import Path
from ontology import occ_p159_final_lock as fl
def main(filesystem_effect_context=None):
 r=fl.root();p=Path(os.environ.get("OCC1K_GLOBAL_VALIDATION_RECEIPT",""))
 if not p.is_file():raise SystemExit("GLOBAL_VALIDATION_RECEIPT_MISSING")
 if "FAST_ACCEPTANCE_ALL_OK" not in p.read_text(encoding="utf-8",errors="replace"):raise SystemExit("GLOBAL_VALIDATION_NOT_GREEN")
 elig=fl.load(r/fl.ELIG_REL);now=fl.evaluate_eligibility(r)
 if now["status"]!="ELIGIBLE" or now["eligibility_identity_sha256"]!=elig["eligibility_identity_sha256"]:raise SystemExit("ELIGIBILITY_DRIFT_BEFORE_LOCK")
 lock=fl.build_lock(elig,hashlib.sha256(p.read_bytes()).hexdigest());fl.atomic_json(r/fl.LOCK_REL,lock,filesystem_effect_context)
 print("P159_OCC1K_FINAL_LOCK_COMMITTED");print("P159_FINAL_LOCK=true");print("P160_OPENED=false");print("LOCK="+str(r/fl.LOCK_REL));print("LOCK_SHA256="+fl.sha(r/fl.LOCK_REL))
if __name__=="__main__":main()
