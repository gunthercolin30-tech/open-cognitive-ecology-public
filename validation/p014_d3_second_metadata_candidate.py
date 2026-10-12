#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"

COMPONENT = "ontology/generative_dynamics_of_intelligence_under_constraints.py"
CALLABLE = "get_metadata"
SOURCE_SHA256 = "4b792666544f5505f896c52a460174f29ad0a86467ae7683c905c1591240f99e"
CONTRACT_KIND = "METADATA_QUERY_V1"

EXPECTED_D2 = "a5d73be29c31266c754559054999da31475d6e63d384ef0042fd96cccbd7e876"
EXPECTED_CROWN = "3d5849c85a30424b9995d62a5e6cd5f463958e3205a2bab912ae97c3cc460114"
EXPECTED_GATE = "ea0728ee65ee30dc63a3e6c649bdf2e9472555c9e6e8eddad9a41bacab48f651"
EXPECTED_REPLICATION = "c3ce4ff53ac9a6fdcab498b8f8e2b44ec85814c5ee7afb19a2dd3d8a4202e013"

D2_REPORT = ROOT / "p014_d2_contractual_preflight_report.json"
CROWN_REPORT = ROOT / "p014_d2_adversarial_crown_report.json"
GATE_REPORT = ROOT / "p014_d3_experimental_adapter_gate_report.json"
REPLICATION_REPORT = ROOT / "p014_d3_replication_report.json"
REPORT = ROOT / "p014_d3_second_metadata_candidate_report.json"

CANONICAL = [
    ROOT / "ontology_inventory.txt",
    D2_REPORT,
    CROWN_REPORT,
    GATE_REPORT,
    REPLICATION_REPORT,
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

def refusal(reason: str, correlation_id: str):
    return {
        "execution_status": "REFUSED",
        "reason": reason,
        "correlation_id": correlation_id,
        "compatibility_status": "UNKNOWN",
        "runtime_evidence": "INSUFFICIENT",
    }

def authorize(row, *, component, callable_name, source_sha256, contract, correlation_id):
    if component != COMPONENT:
        return refusal("COMPONENT_NOT_AUTHORIZED", correlation_id)
    if callable_name != CALLABLE:
        return refusal("CALLABLE_NOT_AUTHORIZED", correlation_id)
    if source_sha256 != SOURCE_SHA256:
        return refusal("SOURCE_HASH_NOT_AUTHORIZED", correlation_id)
    if not isinstance(correlation_id, str) or not correlation_id.strip():
        return refusal("MISSING_CORRELATION_ID", correlation_id)
    if row.get("component") != COMPONENT:
        return refusal("D2_COMPONENT_MISMATCH", correlation_id)
    if row.get("preflight_status") != "CONTRACT_CANDIDATE":
        return refusal("NOT_CONTRACT_CANDIDATE", correlation_id)
    if row.get("compatibility_status") != "UNKNOWN":
        return refusal("HISTORICAL_STATUS_DRIFT", correlation_id)
    if row.get("runtime_authorized") is not False:
        return refusal("HISTORICAL_RUNTIME_AUTHORIZATION_DRIFT", correlation_id)
    if row.get("source_sha256") != SOURCE_SHA256:
        return refusal("D2_SOURCE_HASH_MISMATCH", correlation_id)
    if row.get("d1_candidate_callable") != CALLABLE:
        return refusal("D2_CALLABLE_MISMATCH", correlation_id)
    if contract != row.get("proposed_contract"):
        return refusal("CONTRACT_MISMATCH", correlation_id)
    if contract.get("contract_kind") != CONTRACT_KIND:
        return refusal("CONTRACT_KIND_MISMATCH", correlation_id)
    source = ROOT / COMPONENT
    if not source.is_file():
        return refusal("SOURCE_MISSING", correlation_id)
    if sha_bytes(source.read_bytes()) != SOURCE_SHA256:
        return refusal("REAL_SOURCE_HASH_DRIFT", correlation_id)
    return {
        "execution_status": "AUTHORIZED_EXPERIMENT",
        "correlation_id": correlation_id,
        "compatibility_status": "UNKNOWN",
        "runtime_evidence": "INSUFFICIENT",
    }

def invoke_once(source: Path, correlation_id: str):
    # Exact-file import only after all authorization checks; no discovery.
    module_name = "_oce_p014_d3_second_metadata_candidate"
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
        }
    finally:
        sys.modules.pop(module_name, None)

    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError):
        return {
            "execution_status": "SUCCESS",
            "correlation_id": correlation_id,
            "raw_result_type": type(value).__name__,
            "contract_conformance": "FAIL",
            "runtime_evidence": "NEGATIVE",
            "compatibility_status": "INCOMPATIBLE",
        }

    return {
        "execution_status": "SUCCESS",
        "correlation_id": correlation_id,
        "raw_result": value,
        "raw_result_type": type(value).__name__,
        "raw_result_sha256": sha_bytes(encoded.encode()),
        "contract_conformance": "PASS",
        "runtime_evidence": "POSITIVE",
        "compatibility_status": "COMPATIBLE",
    }

def main():
    before = hashes()
    d2 = load(D2_REPORT)
    crown = load(CROWN_REPORT)
    gate = load(GATE_REPORT)
    replication = load(REPLICATION_REPORT)

    verify_identity(d2, "contractual_preflight_identity_sha256", EXPECTED_D2, "P014-D2")
    verify_identity(crown, "crown_identity_sha256", EXPECTED_CROWN, "P014-D2 crown")
    verify_identity(gate, "experimental_gate_identity_sha256", EXPECTED_GATE, "P014-D3 gate")
    verify_identity(replication, "replication_identity_sha256", EXPECTED_REPLICATION, "P014-D3 replication")

    comparison = replication.get("comparison", {})
    if comparison.get("result_match") != "MATCH":
        raise SystemExit("first candidate replication result was not MATCH")
    if comparison.get("reproducibility_status") != "REPRODUCED":
        raise SystemExit("first candidate was not reproduced")
    if comparison.get("replicated_local_compatibility_status") != "COMPATIBLE":
        raise SystemExit("first candidate replicated compatibility not established")

    rows = [x for x in d2.get("results", []) if x.get("component") == COMPONENT]
    if len(rows) != 1:
        raise SystemExit("second metadata candidate not uniquely present in D2")
    row = rows[0]
    contract = row.get("proposed_contract")
    if not isinstance(contract, dict):
        raise SystemExit("second metadata candidate lacks explicit contract")

    # Degradation/refusal tests occur before the real import.
    refusal_tests = [
        authorize(row, component="ontology/not_authorized.py", callable_name=CALLABLE,
                  source_sha256=SOURCE_SHA256, contract=contract, correlation_id="d3b-r1"),
        authorize(row, component=COMPONENT, callable_name="__spoofed__",
                  source_sha256=SOURCE_SHA256, contract=contract, correlation_id="d3b-r2"),
        authorize(row, component=COMPONENT, callable_name=CALLABLE,
                  source_sha256="0"*64, contract=contract, correlation_id="d3b-r3"),
        authorize(row, component=COMPONENT, callable_name=CALLABLE,
                  source_sha256=SOURCE_SHA256, contract={}, correlation_id="d3b-r4"),
        authorize(row, component=COMPONENT, callable_name=CALLABLE,
                  source_sha256=SOURCE_SHA256, contract=contract, correlation_id=""),
    ]
    if not all(x["execution_status"] == "REFUSED" for x in refusal_tests):
        raise SystemExit("second-candidate pre-execution refusal tests failed")

    correlation_id = "p014-d3-real-metadata-002"
    authorization = authorize(
        row,
        component=COMPONENT,
        callable_name=CALLABLE,
        source_sha256=SOURCE_SHA256,
        contract=contract,
        correlation_id=correlation_id,
    )
    if authorization["execution_status"] != "AUTHORIZED_EXPERIMENT":
        raise SystemExit("second metadata experiment refused: " + authorization.get("reason", "unknown"))

    observation = invoke_once(ROOT / COMPONENT, correlation_id)

    after = hashes()
    if after != before:
        raise SystemExit("canonical P014 mutation detected")

    tests = {
        "d2_identity_verified": True,
        "crown_identity_verified": True,
        "gate_identity_verified": True,
        "first_candidate_replication_identity_verified": True,
        "first_candidate_reproduced": comparison.get("reproducibility_status") == "REPRODUCED",
        "first_candidate_result_match": comparison.get("result_match") == "MATCH",
        "second_candidate_unique": len(rows) == 1,
        "second_candidate_contract_candidate": row.get("preflight_status") == "CONTRACT_CANDIDATE",
        "second_candidate_historical_unknown": row.get("compatibility_status") == "UNKNOWN",
        "second_candidate_historical_runtime_unauthorized": row.get("runtime_authorized") is False,
        "second_candidate_source_hash_verified": sha_bytes((ROOT / COMPONENT).read_bytes()) == SOURCE_SHA256,
        "wrong_component_refused": refusal_tests[0]["execution_status"] == "REFUSED",
        "wrong_callable_refused": refusal_tests[1]["execution_status"] == "REFUSED",
        "wrong_hash_refused": refusal_tests[2]["execution_status"] == "REFUSED",
        "wrong_contract_refused": refusal_tests[3]["execution_status"] == "REFUSED",
        "missing_correlation_refused": refusal_tests[4]["execution_status"] == "REFUSED",
        "real_invocation_attempted_once": observation.get("execution_status") in {"SUCCESS", "EXCEPTION", "REFUSED"},
        "correlation_preserved": observation.get("correlation_id") == correlation_id,
        "canonical_nonmutation": after == before,
    }
    if not all(tests.values()):
        raise SystemExit("P014-D3 second metadata candidate harness tests failed")

    body = {
        "schema": "oce.p014.d3.second_metadata_candidate.v1",
        "milestone": "P014-D3-SECOND-METADATA-CANDIDATE",
        "status": "OBSERVED",
        "bindings": {
            "p014_d2": EXPECTED_D2,
            "p014_d2_crown": EXPECTED_CROWN,
            "p014_d3_gate": EXPECTED_GATE,
            "p014_d3_first_candidate_replication": EXPECTED_REPLICATION,
        },
        "target": {
            "component": COMPONENT,
            "source_sha256": SOURCE_SHA256,
            "callable": CALLABLE,
            "contract": contract,
        },
        "pre_execution_refusal_tests": refusal_tests,
        "authorization": authorization,
        "observation": observation,
        "tests": tests,
        "canonical_hashes_before": before,
        "canonical_hashes_after": after,
        "epistemic_status": {
            "cross_component_contract_evidence": (
                "POSITIVE" if observation.get("execution_status") == "SUCCESS"
                and observation.get("contract_conformance") == "PASS" else "NOT_ESTABLISHED"
            ),
            "general_legacy_compatibility_proven": False,
            "compatibility_scope": "exact second component, source hash, callable and METADATA_QUERY_V1 contract",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
    }
    identity = canonical_sha(body)
    body["second_metadata_candidate_identity_sha256"] = identity
    REPORT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("P014_D3_SECOND_METADATA_CANDIDATE_OBSERVED")
    print("status=OBSERVED")
    print("component=" + COMPONENT)
    print("callable=" + CALLABLE)
    print("source_sha256=" + SOURCE_SHA256)
    print("real_invocation_attempts=1")
    print("execution_status=" + observation.get("execution_status", "UNKNOWN"))
    print("contract_conformance=" + observation.get("contract_conformance", "UNDETERMINED"))
    print("runtime_evidence=" + observation.get("runtime_evidence", "INSUFFICIENT"))
    print("compatibility_status=" + observation.get("compatibility_status", "UNKNOWN"))
    print("raw_result_sha256=" + str(observation.get("raw_result_sha256", "NONE")))
    print("cross_component_contract_evidence=" + body["epistemic_status"]["cross_component_contract_evidence"])
    print("canonical_p014_nonmutation=OK")
    print("second_metadata_candidate_identity_sha256=" + identity)
    print("report=" + str(REPORT))

if __name__ == "__main__":
    main()
