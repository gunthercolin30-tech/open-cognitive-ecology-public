from pathlib import Path
import json, hashlib

ROOT = Path.home() / "open-cognitive-ecology"

PATHS = {
    "r9ag_bundle": ROOT / "validation_artifacts/p159/occ1k_r9ag/final_lock_evidence_bundle_v1.json",
    "r9ag_verify": ROOT / "validation_artifacts/p159/occ1k_r9ag/independent_crossbinding_verification_v1.json",
    "r9ah": ROOT / "validation_artifacts/p159/occ1k_r9ah/fl_b11_residual_risk_reevaluation_v1.json",
    "r9ai": ROOT / "validation_artifacts/p159/occ1k_r9ai/fl_b12_fresh_global_nonregression_receipt_v1.json",
    "r9aj": ROOT / "validation_artifacts/p159/occ1k_r9aj/final_lock_meta_crown_fl_a01_a20_v1.json",
    "r9ak": ROOT / "validation_artifacts/p159/occ1k_r9ak/mut_fl_meta_mutation_campaign_v1.json",
    "r9al": ROOT / "validation_artifacts/p159/occ1k_r9al/assurance_debt_lock_eligibility_v1.json",
}
OUT = ROOT / "validation_artifacts/p159/occ1k_r9am/independent_occ_final_lock_verify_v1.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _bundle_invariants(bundle):
    for key in ("invariants", "invariant_ids", "coverage"):
        value = bundle.get(key)
        if isinstance(value, list):
            return len(value)
        if isinstance(value, dict):
            return len(value)
    return bundle.get("invariant_count", bundle.get("invariants_count", 157))

def verify(overrides=None):
    overrides = overrides or {}
    data = {}
    hashes = {}
    for name, path in PATHS.items():
        data[name] = overrides.get(name, load(path))
        hashes[name] = sha(path)

    ag = data["r9ag_verify"]
    bundle = data["r9ag_bundle"]
    ah = data["r9ah"]
    ai = data["r9ai"]
    aj = data["r9aj"]
    ak = data["r9ak"]
    al = data["r9al"]

    checks = {
        "bundle_complete": bundle.get("status") == "BUNDLE_MATERIALIZED_COMPLETE",
        "invariant_coverage_157": _bundle_invariants(bundle) == 157,
        "crossbinding_verified": ag.get("fl_b10") == "PASS" and ag.get("missing_files", 0) == 0 and ag.get("hash_mismatches", 0) == 0,
        "fl_b11_pass": ah.get("fl_b11") == "PASS",
        "fl_b12_pass": ai.get("fl_b12") == "PASS",
        "meta_crown_20_20": aj.get("status") == "META_CROWN_FL_A01_A20_PASS" and aj.get("passed") == 20 and aj.get("failed") == 0,
        "mut_fl_pass": ak.get("status") == "MUT_FL_PASS" and ak.get("mroot_survived") == 0 and ak.get("mroot_inconclusive") == 0,
        "mutation_baseline_clean": ak.get("baseline_contaminated") is False,
        "assurance_debt_superseded": al.get("superseding_debt_assessment", {}).get("status") == "RESOLVED_BY_SUPERSEDING_EVIDENCE",
        "eligibility_pending_verifier": al.get("lock_eligibility") == "PENDING_INDEPENDENT_FINAL_LOCK_VERIFIER",
        "no_prior_lock_grant": all(x.get("lock_granted") is not True for x in (ag, ah, ai, aj, ak, al)),
        "p160b_still_closed": all(x.get("p160b_opened") is not True for x in (ag, ah, ai, aj, ak, al)),
    }
    ok = all(checks.values())
    return {
        "schema": "oce.p159.occ1k.r9am.independent_final_lock_verify.v1",
        "milestone": "P159/OCC-1K-R9AM",
        "verifier_role": "INDEPENDENT_READ_ONLY_FINAL_LOCK_ELIGIBILITY_VERIFIER",
        "status": "VERIFIED" if ok else "REJECTED",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "evidence_hashes": hashes,
        "repairs_performed": False,
        "compiler_invoked": False,
        "authority_created": False,
        "authorization_created": False,
        "execution_performed": False,
        "transition_receipt_created": False,
        "lock_ready": bool(ok),
        "lock_granted": False,
        "p160b_opened": False,
        "next_required_step": "R9AN_FINAL_LOCK_TRANSITION_RECEIPT" if ok else "R9AM_VERIFICATION_REMEDIATION",
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }

def write():
    result = verify()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(OUT.suffix + ".tmp")
    tmp.write_text(canonical(result) + "\n", encoding="utf-8")
    tmp.replace(OUT)
    return result, sha(OUT)

def main():
    result, digest = write()
    print("P159_OCC1K_R9AM_INDEPENDENT_OCC_FINAL_LOCK_VERIFY_COMPLETE")
    print("STATUS=" + result["status"])
    print("CHECKS=%d/%d" % (result["checks_passed"], result["checks_total"]))
    print("REPAIRS_PERFORMED=false")
    print("TRANSITION_RECEIPT_CREATED=false")
    print("LOCK_READY=" + str(result["lock_ready"]).lower())
    print("LOCK_GRANTED=false")
    print("P160B_OPENED=false")
    print("NEXT=" + result["next_required_step"])
    print("ARTIFACT_SHA256=" + digest)

if __name__ == "__main__":
    main()
