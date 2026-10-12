#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"

COMPONENT = "ontology/dynamics_of_constraints.py"
CALLABLE = "get_metadata"
SOURCE_SHA256 = "b5e3a896589954444448b304ca15fff3a5d100856c0f514bdc0d21d51e3488ee"
CONTRACT_KIND = "METADATA_QUERY_V1"

EXPECTED_D2 = "a5d73be29c31266c754559054999da31475d6e63d384ef0042fd96cccbd7e876"
EXPECTED_CROWN = "3d5849c85a30424b9995d62a5e6cd5f463958e3205a2bab912ae97c3cc460114"
EXPECTED_GATE = "ea0728ee65ee30dc63a3e6c649bdf2e9472555c9e6e8eddad9a41bacab48f651"
EXPECTED_FIRST = "a04fa1764decaf50a02cbb0ded9b04a6102b77a058f9a4936c090ee8a40afd09"

D2_REPORT = ROOT / "p014_d2_contractual_preflight_report.json"
CROWN_REPORT = ROOT / "p014_d2_adversarial_crown_report.json"
GATE_REPORT = ROOT / "p014_d3_experimental_adapter_gate_report.json"
FIRST_REPORT = ROOT / "p014_d3_first_real_invocation_report.json"
REPORT = ROOT / "p014_d3_replication_report.json"

CANONICAL = [
    ROOT / "ontology_inventory.txt",
    D2_REPORT,
    CROWN_REPORT,
    GATE_REPORT,
    FIRST_REPORT,
]

def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_sha(obj) -> str:
    return sha_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def hashes():
    missing = [str(p) for p in CANONICAL if not p.is_file()]
    if missing:
        raise SystemExit("missing canonical artifact(s): " + ", ".join(missing))
    return {str(p.relative_to(ROOT)): sha_bytes(p.read_bytes()) for p in CANONICAL}

def verify_identity(report: dict, field: str, expected: str, label: str):
    if report.get(field) != expected:
        raise SystemExit(label + " identity drift")
    tmp = dict(report)
    got = tmp.pop(field, None)
    if canonical_sha(tmp) != got:
        raise SystemExit(label + " identity round-trip failure")

def invoke_once(source: Path, correlation_id: str):
    module_name = "_oce_p014_d3_replication_dynamics_of_constraints"
    spec = importlib.util.spec_from_file_location(module_name, str(source))
    if spec is None or spec.loader is None:
        return {
            "execution_status": "EXCEPTION",
            "correlation_id": correlation_id,
            "exception_type": "ImportSpecError",
            "exception_message": "unable to construct exact-file import spec",
            "contract_conformance": "UNDETERMINED",
            "runtime_evidence": "INSUFFICIENT",
            "compatibility_status": "UNKNOWN",
            "compatibility_promotion": "NONE",
        }

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        fn = getattr(module, CALLABLE, None)
        if not callable(fn):
            return {
                "execution_status": "REFUSED",
                "reason": "BOUND_CALLABLE_MISSING",
                "correlation_id": correlation_id,
                "contract_conformance": "UNDETERMINED",
                "runtime_evidence": "INSUFFICIENT",
                "compatibility_status": "UNKNOWN",
                "compatibility_promotion": "NONE",
            }
        value = fn()
    except Exception as exc:
        return {
            "execution_status": "EXCEPTION",
            "correlation_id": correlation_id,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "contract_conformance": "UNDETERMINED",
            "runtime_evidence": "INSUFFICIENT",
            "compatibility_status": "UNKNOWN",
            "compatibility_promotion": "NONE",
        }
    finally:
        sys.modules.pop(module_name, None)

    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
        serializable = True
    except (TypeError, ValueError):
        encoded = None
        serializable = False

    if serializable:
        return {
            "execution_status": "SUCCESS",
            "correlation_id": correlation_id,
            "raw_result": value,
            "raw_result_type": type(value).__name__,
            "raw_result_sha256": sha_bytes(encoded.encode()),
            "contract_conformance": "PASS",
            "runtime_evidence": "POSITIVE",
            "compatibility_status": "COMPATIBLE",
            "compatibility_promotion": "REPORT_LAYER_ONLY",
        }

    return {
        "execution_status": "SUCCESS",
        "correlation_id": correlation_id,
        "raw_result_type": type(value).__name__,
        "contract_conformance": "FAIL",
        "runtime_evidence": "NEGATIVE",
        "compatibility_status": "INCOMPATIBLE",
        "compatibility_promotion": "REPORT_LAYER_ONLY",
    }

def main():
    before = hashes()
    d2 = load(D2_REPORT)
    crown = load(CROWN_REPORT)
    gate = load(GATE_REPORT)
    first = load(FIRST_REPORT)

    verify_identity(d2, "contractual_preflight_identity_sha256", EXPECTED_D2, "P014-D2")
    verify_identity(crown, "crown_identity_sha256", EXPECTED_CROWN, "P014-D2 crown")
    verify_identity(gate, "experimental_gate_identity_sha256", EXPECTED_GATE, "P014-D3 gate")
    verify_identity(first, "first_real_invocation_identity_sha256", EXPECTED_FIRST, "P014-D3 first observation")

    target = first.get("authorized_target", {})
    obs1 = first.get("observation", {})

    if target.get("component") != COMPONENT:
        raise SystemExit("first observation component drift")
    if target.get("source_sha256") != SOURCE_SHA256:
        raise SystemExit("first observation source SHA drift")
    if target.get("callable") != CALLABLE:
        raise SystemExit("first observation callable drift")
    if target.get("contract", {}).get("contract_kind") != CONTRACT_KIND:
        raise SystemExit("first observation contract drift")
    if obs1.get("execution_status") != "SUCCESS":
        raise SystemExit("first observation was not successful; replication precondition failed")
    if obs1.get("contract_conformance") != "PASS":
        raise SystemExit("first observation contract did not pass")
    if obs1.get("runtime_evidence") != "POSITIVE":
        raise SystemExit("first observation runtime evidence was not positive")
    if obs1.get("compatibility_status") != "COMPATIBLE":
        raise SystemExit("first observation local compatibility verdict drift")
    if not obs1.get("raw_result_sha256"):
        raise SystemExit("first observation lacks raw result SHA")

    source = ROOT / COMPONENT
    if not source.is_file():
        raise SystemExit("authorized legacy source missing")
    current_source_sha = sha_bytes(source.read_bytes())
    if current_source_sha != SOURCE_SHA256:
        raise SystemExit("authorized legacy source SHA drift; refusing replication")

    # D2 must still describe this exact target as an UNKNOWN contract candidate.
    rows = [x for x in d2.get("results", []) if x.get("component") == COMPONENT]
    if len(rows) != 1:
        raise SystemExit("target not uniquely bound in D2")
    row = rows[0]
    if row.get("preflight_status") != "CONTRACT_CANDIDATE":
        raise SystemExit("D2 target no longer contract candidate")
    if row.get("compatibility_status") != "UNKNOWN":
        raise SystemExit("D2 historical status mutated")
    if row.get("runtime_authorized") is not False:
        raise SystemExit("D2 historical runtime authorization mutated")
    if row.get("source_sha256") != SOURCE_SHA256:
        raise SystemExit("D2 source binding drift")
    if row.get("d1_candidate_callable") != CALLABLE:
        raise SystemExit("D2 callable binding drift")
    if row.get("proposed_contract") != target.get("contract"):
        raise SystemExit("D2/first-observation contract mismatch")

    # Only now is the second real invocation attempted.
    correlation_id = "p014-d3-real-002"
    obs2 = invoke_once(source, correlation_id)

    after = hashes()
    if after != before:
        raise SystemExit("canonical P014 mutation detected after replication")

    if obs2.get("execution_status") != "SUCCESS":
        result_match = "UNDETERMINED"
        reproducibility = "NOT_REPRODUCED" if obs2.get("execution_status") in {"EXCEPTION", "REFUSED"} else "UNDETERMINED"
        compatibility = "UNKNOWN"
    elif obs2.get("contract_conformance") != "PASS":
        result_match = "UNDETERMINED"
        reproducibility = "NOT_REPRODUCED"
        compatibility = "INCOMPATIBLE" if obs2.get("contract_conformance") == "FAIL" else "UNKNOWN"
    else:
        result_match = "MATCH" if obs2.get("raw_result_sha256") == obs1.get("raw_result_sha256") else "MISMATCH"
        reproducibility = "REPRODUCED" if result_match == "MATCH" else "NOT_REPRODUCED"
        compatibility = "COMPATIBLE" if reproducibility == "REPRODUCED" else "UNKNOWN"

    tests = {
        "d2_identity_verified": True,
        "crown_identity_verified": True,
        "gate_identity_verified": True,
        "first_identity_verified": True,
        "first_component_verified": target.get("component") == COMPONENT,
        "first_source_verified": target.get("source_sha256") == SOURCE_SHA256,
        "first_callable_verified": target.get("callable") == CALLABLE,
        "first_contract_verified": target.get("contract", {}).get("contract_kind") == CONTRACT_KIND,
        "first_success_verified": obs1.get("execution_status") == "SUCCESS",
        "first_contract_pass_verified": obs1.get("contract_conformance") == "PASS",
        "first_result_sha_present": bool(obs1.get("raw_result_sha256")),
        "current_source_hash_verified": current_source_sha == SOURCE_SHA256,
        "d2_historical_unknown_preserved": row.get("compatibility_status") == "UNKNOWN",
        "d2_historical_runtime_unauthorized_preserved": row.get("runtime_authorized") is False,
        "replication_attempted_once": obs2.get("execution_status") in {"SUCCESS", "EXCEPTION", "REFUSED"},
        "replication_correlation_preserved": obs2.get("correlation_id") == correlation_id,
        "canonical_nonmutation": after == before,
    }
    if not all(tests.values()):
        raise SystemExit("P014-D3 replication harness test failure: " +
                         ", ".join(k for k,v in tests.items() if not v))

    body = {
        "schema": "oce.p014.d3.replication.v1",
        "milestone": "P014-D3-REPLICATION",
        "status": "OBSERVED",
        "bindings": {
            "p014_d2": EXPECTED_D2,
            "p014_d2_crown": EXPECTED_CROWN,
            "p014_d3_gate": EXPECTED_GATE,
            "p014_d3_first_observation": EXPECTED_FIRST,
        },
        "target": {
            "component": COMPONENT,
            "source_sha256": SOURCE_SHA256,
            "callable": CALLABLE,
            "contract_kind": CONTRACT_KIND,
        },
        "observation_1": {
            "correlation_id": obs1.get("correlation_id"),
            "execution_status": obs1.get("execution_status"),
            "contract_conformance": obs1.get("contract_conformance"),
            "runtime_evidence": obs1.get("runtime_evidence"),
            "compatibility_status": obs1.get("compatibility_status"),
            "raw_result_sha256": obs1.get("raw_result_sha256"),
        },
        "observation_2": obs2,
        "comparison": {
            "result_match": result_match,
            "reproducibility_status": reproducibility,
            "replicated_local_compatibility_status": compatibility,
        },
        "tests": tests,
        "canonical_hashes_before": before,
        "canonical_hashes_after": after,
        "epistemic_status": {
            "replication_scope": "exact component, source hash, callable and METADATA_QUERY_V1 contract",
            "general_legacy_compatibility_proven": False,
            "historical_d2_status_mutated": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
    }
    identity = canonical_sha(body)
    body["replication_identity_sha256"] = identity
    REPORT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("P014_D3_REPLICATION_OBSERVED")
    print("status=OBSERVED")
    print("component=" + COMPONENT)
    print("callable=" + CALLABLE)
    print("source_sha256=" + SOURCE_SHA256)
    print("replication_attempts=1")
    print("execution_status=" + obs2.get("execution_status", "UNKNOWN"))
    print("contract_conformance=" + obs2.get("contract_conformance", "UNDETERMINED"))
    print("runtime_evidence=" + obs2.get("runtime_evidence", "INSUFFICIENT"))
    print("raw_result_sha256=" + str(obs2.get("raw_result_sha256", "NONE")))
    print("result_match=" + result_match)
    print("reproducibility_status=" + reproducibility)
    print("compatibility_status=" + compatibility)
    print("canonical_p014_nonmutation=OK")
    print("replication_identity_sha256=" + identity)
    print("report=" + str(REPORT))

if __name__ == "__main__":
    main()
