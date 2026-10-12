from pathlib import Path
import json,hashlib,time,sys
ROOT=Path.home()/"open-cognitive-ecology"
AH=ROOT/"validation_artifacts/p159/occ1k_r9ah/fl_b11_residual_risk_reevaluation_v1.json"
DIR=ROOT/"validation_artifacts/p159/occ1k_r9ai"
PREP=DIR/"fresh_global_validation_prepare_v1.json"
LOG=DIR/"fresh_global_validation.log"
RECEIPT=DIR/"fl_b12_fresh_global_nonregression_receipt_v1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def prepare():
 a=load(AH)
 if a.get("fl_b11")!="PASS": raise RuntimeError("FL_B11_NOT_PASS")
 DIR.mkdir(parents=True,exist_ok=True)
 if LOG.exists(): LOG.unlink()
 x={"schema":"oce.p159.occ1k.r9ai.prepare.v1","milestone":"P159/OCC-1K-R9AI",
    "prepared_at_ns":time.time_ns(),"r9ah_sha256":sha(AH),"expected_command":"python3 -m validation.main",
    "lock_ready":False,"lock_granted":False,"p160b_opened":False}
 PREP.write_text(canon(x)+"\n",encoding="utf-8")
 print("R9AI_PREPARED");print("LOG="+str(LOG));print("R9AH_SHA256="+x["r9ah_sha256"])
def assess(prep=None,log_text=None,log_mtime_ns=None):
 p=prep if prep is not None else load(PREP)
 txt=log_text if log_text is not None else (LOG.read_text(encoding="utf-8",errors="replace") if LOG.is_file() else "")
 mt=log_mtime_ns if log_mtime_ns is not None else (LOG.stat().st_mtime_ns if LOG.is_file() else 0)
 fresh=mt>p["prepared_at_ns"]
 fast="FAST_ACCEPTANCE_ALL_OK" in txt
 bad=any(s in txt for s in ["FAST_ACCEPTANCE_FAILED","failed_modules=1","error_count=1"])
 ah_ok=sha(AH)==p["r9ah_sha256"] and load(AH).get("fl_b11")=="PASS"
 ok=fresh and fast and not bad and ah_ok
 return {"schema":"oce.p159.occ1k.r9ai.fl_b12.receipt.v1","milestone":"P159/OCC-1K-R9AI",
 "status":"FL_B12_PASS" if ok else "FL_B12_INCONCLUSIVE","fl_b12":"PASS" if ok else "INCONCLUSIVE",
 "checks":{"fresh_log":fresh,"fast_acceptance_all_ok":fast,"no_explicit_failure_marker":not bad,"r9ah_anchor_unchanged":ah_ok},
 "anchors":{"r9ah_sha256":p["r9ah_sha256"],"validation_log_sha256":hashlib.sha256(txt.encode()).hexdigest()},
 "validation_command":"python3 -m validation.main","historical_receipts_rewritten":False,
 "assurance_debt_closed":False,"meta_assurance_complete":False,
 "lock_ready":False,"lock_granted":False,"p160b_opened":False,
 "next_required_step":"OCC1K_META_ASSURANCE_FL_A01_A20" if ok else "R9AI_GLOBAL_NONREGRESSION_REPAIR",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def finalize():
 x=assess();RECEIPT.write_text(canon(x)+"\n",encoding="utf-8");h=sha(RECEIPT)
 print("P159_OCC1K_R9AI_FL_B12_FRESH_GLOBAL_NONREGRESSION_COMPLETE");print("STATUS="+x["status"]);print("FL_B12="+x["fl_b12"])
 print("FRESH_LOG="+str(x["checks"]["fresh_log"]).lower());print("FAST_ACCEPTANCE_ALL_OK="+str(x["checks"]["fast_acceptance_all_ok"]).lower())
 print("ASSURANCE_DEBT_CLOSED=false");print("META_ASSURANCE_COMPLETE=false");print("LOCK_READY=false");print("LOCK_GRANTED=false");print("P160B_OPENED=false")
 print("NEXT="+x["next_required_step"]);print("RECEIPT_SHA256="+h)
if __name__=="__main__":
 if len(sys.argv)!=2 or sys.argv[1] not in ("--prepare","--finalize"): raise SystemExit("usage: ... --prepare|--finalize")
 prepare() if sys.argv[1]=="--prepare" else finalize()
