from pathlib import Path
import json, hashlib, datetime

ROOT=Path.home()/"open-cognitive-ecology"
M=ROOT/"validation_artifacts/p159/occ1k_r9an/final_lock_manifest_lock_ready_candidate_v1.json"
B=ROOT/"validation_artifacts/p159/occ1k_r9ag/final_lock_evidence_bundle_v1.json"
V=ROOT/"validation_artifacts/p159/occ1k_r9am2/independent_occ_final_lock_verify_schema_aware_v2.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ao/final_lock_transition_receipt_v1.json"

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def build(timestamp=None):
    m,b,v=load(M),load(B),load(V)
    eligible=(
        m.get("status")=="LOCK_READY"
        and m.get("transition_receipt_present") is False
        and m.get("runtime_active") is False
        and m.get("authority_created") is False
        and m.get("authorization_created") is False
        and m.get("execution_performed") is False
        and m.get("p160b_opened") is False
        and v.get("status")=="VERIFIED"
        and v.get("lock_ready") is True
        and b.get("status")=="BUNDLE_MATERIALIZED_COMPLETE"
    )
    ts=timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")
    x={
      "schema":"oce.p159.occ1k.final_lock_transition_receipt.v1",
      "milestone":"P159/OCC-1K",
      "lock_id":m.get("lock_id"),
      "manifest_hash":m.get("manifest_hash"),
      "manifest_artifact_sha256":sha(M),
      "previous_baseline":"HISTORICAL_OCC1K_LOCK_PRESERVED",
      "new_baseline":"P159_OCC1K_EXHAUSTIVE_LOCK_CANDIDATE",
      "authority":"GOVERNED_P159_OCC1K_FINAL_LOCK_TRANSITION",
      "decision":"APPROVE_LOCK_TRANSITION" if eligible else "DENY_LOCK_TRANSITION",
      "timestamp":ts,
      "reason":"All exhaustive P159 OCC-1K lock prerequisites verified; transition receipt records governed decision only." if eligible else "One or more exhaustive P159 OCC-1K lock prerequisites are not satisfied.",
      "evidence_bundle_hash":b.get("bundle_sha256"),
      "evidence_bundle_artifact_sha256":sha(B),
      "independent_verifier_artifact_sha256":sha(V),
      "eligible_for_transition":eligible,
      "receipt_is_lock":False,
      "lock_applied":False,
      "runtime_active":False,
      "authority_created":False,
      "authorization_created":False,
      "execution_performed":False,
      "p160b_opened":False,
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True
    }
    base=canon(x).encode()
    x["receipt_hash"]=hashlib.sha256(base).hexdigest()
    return x

def write():
    x=build()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    tmp=OUT.with_suffix(".json.tmp")
    tmp.write_text(canon(x)+"\n",encoding="utf-8")
    tmp.replace(OUT)
    return x,sha(OUT)

def main():
    x,h=write()
    print("P159_OCC1K_R9AO_GOVERNED_FINAL_LOCK_TRANSITION_RECEIPT_COMPLETE")
    print("DECISION="+x["decision"])
    print("ELIGIBLE_FOR_TRANSITION="+str(x["eligible_for_transition"]).lower())
    print("MANIFEST_HASH="+str(x["manifest_hash"]))
    print("RECEIPT_IS_LOCK=false")
    print("LOCK_APPLIED=false")
    print("RUNTIME_ACTIVE=false")
    print("P160B_OPENED=false")
    print("NEXT=R9AP_APPLY_GOVERNED_LOCK_TRANSITION")
    print("RECEIPT_SHA256="+h)

if __name__=="__main__": main()
