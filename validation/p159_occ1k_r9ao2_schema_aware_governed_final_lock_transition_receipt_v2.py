from pathlib import Path
import json, hashlib, datetime

ROOT=Path.home()/"open-cognitive-ecology"
M=ROOT/"validation_artifacts/p159/occ1k_r9an/final_lock_manifest_lock_ready_candidate_v1.json"
B=ROOT/"validation_artifacts/p159/occ1k_r9ag/final_lock_evidence_bundle_v1.json"
V=ROOT/"validation_artifacts/p159/occ1k_r9am2/independent_occ_final_lock_verify_schema_aware_v2.json"
OLD=ROOT/"validation_artifacts/p159/occ1k_r9ao/final_lock_transition_receipt_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ao2/final_lock_transition_receipt_schema_aware_v2.json"

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

REQUIRED=("lock_id","manifest_hash","previous_baseline","new_baseline","authority",
          "decision","timestamp","reason","evidence_bundle_hash")

def build(timestamp=None, overrides=None):
    overrides=overrides or {}
    m=overrides.get("manifest",load(M))
    b=overrides.get("bundle",load(B))
    v=overrides.get("verifier",load(V))
    ts=timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")
    # The R9-AG bundle has no self-hash field by design/schema; bind its externally
    # recomputed artifact SHA-256 as the canonical evidence_bundle_hash.
    bundle_hash=overrides.get("bundle_artifact_sha256",sha(B))
    preliminary={
      "schema":"oce.p159.occ1k.final_lock_transition_receipt.schema_aware.v2",
      "milestone":"P159/OCC-1K",
      "lock_id":m.get("lock_id"),
      "manifest_hash":m.get("manifest_hash"),
      "manifest_artifact_sha256":sha(M),
      "previous_baseline":"HISTORICAL_OCC1K_LOCK_PRESERVED",
      "new_baseline":"P159_OCC1K_EXHAUSTIVE_LOCK_CANDIDATE",
      "authority":"GOVERNED_P159_OCC1K_FINAL_LOCK_TRANSITION",
      "decision":"PENDING",
      "timestamp":ts,
      "reason":"PENDING",
      "evidence_bundle_hash":bundle_hash,
      "evidence_bundle_hash_semantics":"EXTERNAL_SHA256_OF_R9AG_BUNDLE_ARTIFACT_BYTES",
      "independent_verifier_artifact_sha256":sha(V),
    }
    prerequisites=(
      m.get("status")=="LOCK_READY"
      and m.get("transition_receipt_present") is False
      and m.get("runtime_active") is False
      and m.get("p160b_opened") is False
      and v.get("status")=="VERIFIED"
      and v.get("lock_ready") is True
      and b.get("status")=="BUNDLE_MATERIALIZED_COMPLETE"
      and bool(bundle_hash)
    )
    required_nondecision=("lock_id","manifest_hash","previous_baseline","new_baseline",
                          "authority","timestamp","evidence_bundle_hash")
    fields_complete=all(preliminary.get(k) not in (None,"") for k in required_nondecision)
    approved=prerequisites and fields_complete
    preliminary["decision"]="APPROVE_LOCK_TRANSITION" if approved else "DENY_LOCK_TRANSITION"
    preliminary["reason"]=(
      "All exhaustive P159 OCC-1K lock prerequisites are verified and all canonical receipt bindings are complete."
      if approved else
      "Transition denied because one or more prerequisites or canonical receipt bindings are incomplete."
    )
    preliminary["eligible_for_transition"]=approved
    preliminary["canonical_fields_complete"]=all(preliminary.get(k) not in (None,"") for k in REQUIRED)
    if not preliminary["canonical_fields_complete"]:
        preliminary["decision"]="DENY_LOCK_TRANSITION"
        preliminary["eligible_for_transition"]=False
    preliminary.update({
      "historical_r9ao_preserved":OLD.is_file(),
      "historical_r9ao_rewritten":False,
      "receipt_is_lock":False,
      "lock_applied":False,
      "runtime_active":False,
      "authority_created":False,
      "authorization_created":False,
      "execution_performed":False,
      "p160b_opened":False,
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True,
    })
    preliminary["receipt_hash"]=hashlib.sha256(canon(preliminary).encode()).hexdigest()
    return preliminary

def write():
    x=build(); OUT.parent.mkdir(parents=True,exist_ok=True)
    tmp=OUT.with_suffix(".json.tmp"); tmp.write_text(canon(x)+"\n",encoding="utf-8"); tmp.replace(OUT)
    return x,sha(OUT)

def main():
    x,h=write()
    print("P159_OCC1K_R9AO2_SCHEMA_AWARE_GOVERNED_FINAL_LOCK_TRANSITION_RECEIPT_COMPLETE")
    print("DECISION="+x["decision"])
    print("ELIGIBLE_FOR_TRANSITION="+str(x["eligible_for_transition"]).lower())
    print("CANONICAL_FIELDS_COMPLETE="+str(x["canonical_fields_complete"]).lower())
    print("EVIDENCE_BUNDLE_HASH="+x["evidence_bundle_hash"])
    print("HISTORICAL_R9AO_PRESERVED="+str(x["historical_r9ao_preserved"]).lower())
    print("HISTORICAL_R9AO_REWRITTEN=false")
    print("RECEIPT_IS_LOCK=false")
    print("LOCK_APPLIED=false")
    print("P160B_OPENED=false")
    print("NEXT=R9AP_APPLY_GOVERNED_LOCK_TRANSITION")
    print("RECEIPT_SHA256="+h)
if __name__=="__main__": main()
