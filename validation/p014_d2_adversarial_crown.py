#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"

EXPECTED_A = "6698bee8229a108f290f3797b6f34e94c28040a365900dba81c98268885adae4"
EXPECTED_B = "48891a4800e4661a90dfec2f8f654cd4a4153babcee378d694085590493fc947"
EXPECTED_C = "6b4183c294b178adda09e699b0a2a4c060747f8f52cdfa5040df12c0cc602824"
EXPECTED_D1 = "7647c5369125e3b4485e9d096f4f91ef4af77765a00635baa947bee919f4a88f"
EXPECTED_D2 = "a5d73be29c31266c754559054999da31475d6e63d384ef0042fd96cccbd7e876"

D2_REPORT = ROOT / "p014_d2_contractual_preflight_report.json"
CROWN_REPORT = ROOT / "p014_d2_adversarial_crown_report.json"

CANONICAL_FILES = [
    ROOT / "ontology_inventory.txt",
    ROOT / "p014_a_legacy_capability_boundary_contract_report.json",
    ROOT / "p014_b_governed_legacy_candidate_assessment_report.json",
    ROOT / "p014_c_legacy_capability_adapter_core_report.json",
    ROOT / "p014_d1_representative_testability_selection_report.json",
    ROOT / "p014_d2_contractual_preflight_report.json",
]

ALLOWED = {
    "CONTRACT_CANDIDATE",
    "REQUIRES_DEPENDENCY_CONTRACT",
    "ENTRYPOINT_NOT_CAPABILITY",
    "TEST_SURFACE_EXCLUDED",
    "UNRESOLVED",
}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

def canonical_sha(obj):
    return sha_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())

def file_hashes():
    missing = [str(p) for p in CANONICAL_FILES if not p.is_file()]
    if missing:
        raise SystemExit("missing canonical P014 artifact(s): " + ", ".join(missing))
    return {str(p.relative_to(ROOT)): sha_bytes(p.read_bytes()) for p in CANONICAL_FILES}

def validate_report(d):
    reasons = []
    if d.get("contractual_preflight_identity_sha256") != EXPECTED_D2:
        reasons.append("D2_IDENTITY_DRIFT")

    bindings = d.get("bindings", {})
    expected_bindings = {
        "p014_a": EXPECTED_A,
        "p014_b": EXPECTED_B,
        "p014_c": EXPECTED_C,
        "p014_d1": EXPECTED_D1,
    }
    if bindings != expected_bindings:
        reasons.append("UPSTREAM_BINDING_DRIFT")

    results = d.get("results")
    if not isinstance(results, list) or len(results) != 12:
        reasons.append("PANEL_CARDINALITY_INVALID")
        return False, sorted(set(reasons))

    components = [x.get("component") for x in results]
    if len(set(components)) != 12 or any(not isinstance(x, str) or not x for x in components):
        reasons.append("PANEL_UNIQUENESS_INVALID")

    for x in results:
        status = x.get("preflight_status")
        contract = x.get("proposed_contract")

        if status not in ALLOWED:
            reasons.append("UNGOVERNED_STATUS")

        if x.get("compatibility_status") != "UNKNOWN":
            reasons.append("COMPATIBILITY_PROMOTION")

        if x.get("runtime_authorized") is not False:
            reasons.append("PREMATURE_RUNTIME_AUTHORIZATION")

        if x.get("runtime_execution") != "NONE":
            reasons.append("RUNTIME_EXECUTION_CLAIM")

        if status == "CONTRACT_CANDIDATE":
            if not isinstance(contract, dict):
                reasons.append("MISSING_CONTRACT")
            else:
                required = {
                    "contract_kind", "callable", "input_contract",
                    "output_contract", "error_contract",
                    "provenance_required", "source_hash_required",
                    "correlation_required",
                }
                if not required.issubset(contract):
                    reasons.append("INCOMPLETE_CONTRACT")
                if contract.get("callable") != x.get("d1_candidate_callable"):
                    reasons.append("CALLABLE_CONTRACT_MISMATCH")
                if contract.get("provenance_required") is not True:
                    reasons.append("PROVENANCE_GUARD_DISABLED")
                if contract.get("source_hash_required") is not True:
                    reasons.append("SOURCE_HASH_GUARD_DISABLED")
                if contract.get("correlation_required") is not True:
                    reasons.append("CORRELATION_GUARD_DISABLED")
        elif contract is not None:
            reasons.append("CONTRACT_ON_NONCANDIDATE")

        name = Path(x.get("component", "")).name
        if name.startswith("test_") and status != "TEST_SURFACE_EXCLUDED":
            reasons.append("TEST_SURFACE_SPOOF")

        if x.get("d1_candidate_callable") == "main" and status not in {
            "ENTRYPOINT_NOT_CAPABILITY", "TEST_SURFACE_EXCLUDED"
        }:
            reasons.append("MAIN_CAPABILITY_SPOOF")

        if x.get("d1_candidate_callable") == "parse_args" and status != "ENTRYPOINT_NOT_CAPABILITY":
            reasons.append("PARSE_ARGS_CAPABILITY_SPOOF")

        src = ROOT / x.get("component", "")
        if not src.is_file():
            reasons.append("SOURCE_MISSING")
        elif sha_bytes(src.read_bytes()) != x.get("source_sha256"):
            reasons.append("SOURCE_HASH_DRIFT")

    summary = d.get("summary", {})
    actual_counts = {}
    for x in results:
        s = x.get("preflight_status")
        actual_counts[s] = actual_counts.get(s, 0) + 1
    if summary.get("preflight_counts") != dict(sorted(actual_counts.items())):
        reasons.append("SUMMARY_COUNT_DRIFT")
    if summary.get("contract_candidates") != actual_counts.get("CONTRACT_CANDIDATE", 0):
        reasons.append("CONTRACT_CANDIDATE_COUNT_DRIFT")
    if summary.get("runtime_authorized") != 0:
        reasons.append("SUMMARY_RUNTIME_AUTHORIZATION")
    if summary.get("compatibility_promotions") != 0:
        reasons.append("SUMMARY_COMPATIBILITY_PROMOTION")

    method = d.get("method", {})
    if method.get("legacy_imports") != "NONE":
        reasons.append("LEGACY_IMPORT_CLAIM")
    if method.get("runtime_execution") != "NONE":
        reasons.append("METHOD_RUNTIME_EXECUTION")
    if method.get("runtime_authorizations") != 0:
        reasons.append("METHOD_RUNTIME_AUTHORIZATION")
    if method.get("compatibility_promotions") != 0:
        reasons.append("METHOD_COMPATIBILITY_PROMOTION")

    return not reasons, sorted(set(reasons))

def mutation(base, label, fn, expected_reason):
    d = copy.deepcopy(base)
    fn(d)
    ok, reasons = validate_report(d)
    passed = (not ok) and expected_reason in reasons
    return {
        "attack": label,
        "expected_rejection_reason": expected_reason,
        "rejected": not ok,
        "observed_reasons": reasons,
        "passed": passed,
    }

def main():
    before = file_hashes()
    base = load(D2_REPORT)

    ok, reasons = validate_report(base)
    if not ok:
        raise SystemExit("baseline D2 report failed crown validation: " + ",".join(reasons))

    results = base["results"]
    contract_idx = next(i for i,x in enumerate(results) if x["preflight_status"] == "CONTRACT_CANDIDATE")
    test_idx = next(i for i,x in enumerate(results) if Path(x["component"]).name.startswith("test_"))
    main_idx = next(i for i,x in enumerate(results) if x["d1_candidate_callable"] == "main")
    parse_candidates = [i for i,x in enumerate(results) if x["d1_candidate_callable"] == "parse_args"]
    noncontract_idx = next(i for i,x in enumerate(results) if x["preflight_status"] != "CONTRACT_CANDIDATE")

    attacks = []

    attacks.append(mutation(base, "d2_identity_drift",
        lambda d: d.__setitem__("contractual_preflight_identity_sha256", "0"*64),
        "D2_IDENTITY_DRIFT"))

    attacks.append(mutation(base, "upstream_binding_spoof",
        lambda d: d["bindings"].__setitem__("p014_c", "0"*64),
        "UPSTREAM_BINDING_DRIFT"))

    attacks.append(mutation(base, "panel_candidate_removed",
        lambda d: d["results"].pop(),
        "PANEL_CARDINALITY_INVALID"))

    attacks.append(mutation(base, "panel_candidate_duplicated",
        lambda d: d["results"].__setitem__(1, copy.deepcopy(d["results"][0])),
        "PANEL_UNIQUENESS_INVALID"))

    attacks.append(mutation(base, "compatibility_unknown_to_compatible",
        lambda d: d["results"][contract_idx].__setitem__("compatibility_status", "COMPATIBLE"),
        "COMPATIBILITY_PROMOTION"))

    attacks.append(mutation(base, "premature_runtime_authorization",
        lambda d: d["results"][contract_idx].__setitem__("runtime_authorized", True),
        "PREMATURE_RUNTIME_AUTHORIZATION"))

    attacks.append(mutation(base, "runtime_execution_spoof",
        lambda d: d["results"][contract_idx].__setitem__("runtime_execution", "EXECUTED"),
        "RUNTIME_EXECUTION_CLAIM"))

    attacks.append(mutation(base, "contract_removed",
        lambda d: d["results"][contract_idx].__setitem__("proposed_contract", None),
        "MISSING_CONTRACT"))

    attacks.append(mutation(base, "contract_callable_mismatch",
        lambda d: d["results"][contract_idx]["proposed_contract"].__setitem__("callable", "__spoofed__"),
        "CALLABLE_CONTRACT_MISMATCH"))

    attacks.append(mutation(base, "contract_provenance_disabled",
        lambda d: d["results"][contract_idx]["proposed_contract"].__setitem__("provenance_required", False),
        "PROVENANCE_GUARD_DISABLED"))

    attacks.append(mutation(base, "contract_source_hash_disabled",
        lambda d: d["results"][contract_idx]["proposed_contract"].__setitem__("source_hash_required", False),
        "SOURCE_HASH_GUARD_DISABLED"))

    attacks.append(mutation(base, "contract_correlation_disabled",
        lambda d: d["results"][contract_idx]["proposed_contract"].__setitem__("correlation_required", False),
        "CORRELATION_GUARD_DISABLED"))

    attacks.append(mutation(base, "contract_incomplete",
        lambda d: d["results"][contract_idx]["proposed_contract"].pop("error_contract"),
        "INCOMPLETE_CONTRACT"))

    attacks.append(mutation(base, "contract_on_noncandidate",
        lambda d: d["results"][noncontract_idx].__setitem__("proposed_contract", {"spoof": True}),
        "CONTRACT_ON_NONCANDIDATE"))

    attacks.append(mutation(base, "test_surface_promoted",
        lambda d: d["results"][test_idx].__setitem__("preflight_status", "CONTRACT_CANDIDATE"),
        "TEST_SURFACE_SPOOF"))

    attacks.append(mutation(base, "main_promoted",
        lambda d: d["results"][main_idx].__setitem__("preflight_status", "CONTRACT_CANDIDATE"),
        "MAIN_CAPABILITY_SPOOF"))

    if parse_candidates:
        attacks.append(mutation(base, "parse_args_promoted",
            lambda d: d["results"][parse_candidates[0]].__setitem__("preflight_status", "CONTRACT_CANDIDATE"),
            "PARSE_ARGS_CAPABILITY_SPOOF"))

    attacks.append(mutation(base, "ungoverned_status",
        lambda d: d["results"][contract_idx].__setitem__("preflight_status", "COMPATIBLE"),
        "UNGOVERNED_STATUS"))

    attacks.append(mutation(base, "summary_runtime_authorized_spoof",
        lambda d: d["summary"].__setitem__("runtime_authorized", 1),
        "SUMMARY_RUNTIME_AUTHORIZATION"))

    attacks.append(mutation(base, "summary_compatibility_promotion_spoof",
        lambda d: d["summary"].__setitem__("compatibility_promotions", 1),
        "SUMMARY_COMPATIBILITY_PROMOTION"))

    attacks.append(mutation(base, "summary_contract_count_spoof",
        lambda d: d["summary"].__setitem__("contract_candidates", 999),
        "CONTRACT_CANDIDATE_COUNT_DRIFT"))

    attacks.append(mutation(base, "method_legacy_import_spoof",
        lambda d: d["method"].__setitem__("legacy_imports", "YES"),
        "LEGACY_IMPORT_CLAIM"))

    attacks.append(mutation(base, "method_runtime_execution_spoof",
        lambda d: d["method"].__setitem__("runtime_execution", "YES"),
        "METHOD_RUNTIME_EXECUTION"))

    attacks.append(mutation(base, "method_runtime_authorization_spoof",
        lambda d: d["method"].__setitem__("runtime_authorizations", 1),
        "METHOD_RUNTIME_AUTHORIZATION"))

    attacks.append(mutation(base, "method_compatibility_promotion_spoof",
        lambda d: d["method"].__setitem__("compatibility_promotions", 1),
        "METHOD_COMPATIBILITY_PROMOTION"))

    # Source-drift attack without touching the real source: alter the claimed hash.
    attacks.append(mutation(base, "claimed_source_hash_drift",
        lambda d: d["results"][contract_idx].__setitem__("source_sha256", "0"*64),
        "SOURCE_HASH_DRIFT"))

    passed = sum(1 for x in attacks if x["passed"])
    if passed != len(attacks):
        bad = [x["attack"] for x in attacks if not x["passed"]]
        raise SystemExit("P014-D2 adversarial crown failure: " + ", ".join(bad))

    after = file_hashes()
    nonmutation = before == after
    if not nonmutation:
        raise SystemExit("canonical P014 artifact mutation detected")

    body = {
        "schema": "oce.p014.d2.adversarial_crown.v1",
        "milestone": "P014-D2-CROWN",
        "status": "VALIDATED",
        "binding": {"p014_d2": EXPECTED_D2},
        "method": {
            "attack_mode": "in-memory mutations of report copies only",
            "legacy_imports": "NONE",
            "runtime_execution": "NONE",
            "real_source_mutation": "NONE",
            "compatibility_promotions": 0,
            "runtime_authorizations": 0,
        },
        "summary": {
            "attacks": len(attacks),
            "passed": passed,
            "failed": len(attacks) - passed,
            "canonical_nonmutation": nonmutation,
        },
        "attacks": attacks,
        "canonical_hashes_before": before,
        "canonical_hashes_after": after,
        "epistemic_status": {
            "contract_candidates_remain_unknown": True,
            "runtime_compatibility_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
    }
    identity = canonical_sha(body)
    body["crown_identity_sha256"] = identity
    CROWN_REPORT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check = load(CROWN_REPORT)
    got = check.pop("crown_identity_sha256")
    if canonical_sha(check) != got:
        raise SystemExit("crown deterministic identity round-trip failure")
    if file_hashes() != before:
        raise SystemExit("canonical mutation after report write")

    print("P014_D2_ADVERSARIAL_CROWN_OK")
    print("status=VALIDATED")
    print(f"attacks={len(attacks)}")
    print(f"passed={passed}/{len(attacks)}")
    print("failed=0")
    print("legacy_imports=NONE")
    print("runtime_execution=NONE")
    print("real_source_mutation=NONE")
    print("runtime_authorized=0")
    print("compatibility_promotions=0")
    print("contract_candidates_status=UNKNOWN")
    print("canonical_p014_nonmutation=OK")
    print("crown_identity_sha256=" + identity)
    print("report=" + str(CROWN_REPORT))

if __name__ == "__main__":
    main()
