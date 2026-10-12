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

D2_REPORT = ROOT / "p014_d2_contractual_preflight_report.json"
CROWN_REPORT = ROOT / "p014_d2_adversarial_crown_report.json"
GATE_REPORT = ROOT / "p014_d3_experimental_adapter_gate_report.json"
REPORT = ROOT / "p014_d3_first_real_invocation_report.json"

CANONICAL = [
    ROOT / "ontology_inventory.txt",
    D2_REPORT,
    CROWN_REPORT,
    GATE_REPORT,
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

def refuse(reason, correlation_id):
    return {
        "execution_status": "REFUSED",
        "reason": reason,
        "correlation_id": correlation_id,
        "runtime_evidence": "INSUFFICIENT",
        "compatibility_status": "UNKNOWN",
        "compatibility_promotion": "NONE",
    }

def preflight(row, *, component, callable_name, source_sha256, contract, correlation_id):
    if component != COMPONENT:
        return refuse("COMPONENT_NOT_AUTHORIZED", correlation_id)
    if callable_name != CALLABLE:
        return refuse("CALLABLE_NOT_AUTHORIZED", correlation_id)
    if source_sha256 != SOURCE_SHA256:
        return refuse("DECLARED_SOURCE_HASH_MISMATCH", correlation_id)
    if not isinstance(correlation_id, str) or not correlation_id.strip():
        return refuse("MISSING_CORRELATION_ID", correlation_id)
    if row.get("component") != COMPONENT:
        return refuse("D2_COMPONENT_MISMATCH", correlation_id)
    if row.get("preflight_status") != "CONTRACT_CANDIDATE":
        return refuse("NOT_CONTRACT_CANDIDATE", correlation_id)
    if row.get("compatibility_status") != "UNKNOWN":
        return refuse("PREEXISTING_COMPATIBILITY_PROMOTION", correlation_id)
    if row.get("runtime_authorized") is not False:
        return refuse("PREMATURE_RUNTIME_AUTHORIZATION", correlation_id)
    if row.get("source_sha256") != SOURCE_SHA256:
        return refuse("D2_SOURCE_HASH_MISMATCH", correlation_id)
    if row.get("d1_candidate_callable") != CALLABLE:
        return refuse("D2_CALLABLE_MISMATCH", correlation_id)
    if contract != row.get("proposed_contract"):
        return refuse("CONTRACT_MISMATCH", correlation_id)
    if contract.get("contract_kind") != CONTRACT_KIND:
        return refuse("CONTRACT_KIND_MISMATCH", correlation_id)

    source = ROOT / COMPONENT
    if not source.is_file():
        return refuse("SOURCE_MISSING", correlation_id)
    if sha_bytes(source.read_bytes()) != SOURCE_SHA256:
        return refuse("REAL_SOURCE_HASH_DRIFT", correlation_id)

    return {
        "execution_status": "AUTHORIZED_EXPERIMENT",
        "correlation_id": correlation_id,
        "runtime_evidence": "INSUFFICIENT",
        "compatibility_status": "UNKNOWN",
        "compatibility_promotion": "NONE",
    }

def invoke_once(source: Path, correlation_id: str):
    module_name = "_oce_p014_d3_dynamics_of_constraints"
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
            "compatibility_basis": "single bounded real invocation satisfied explicit METADATA_QUERY_V1 contract",
            "compatibility_promotion": "REPORT_LAYER_ONLY",
        }
    return {
        "execution_status": "SUCCESS",
        "correlation_id": correlation_id,
        "raw_result_type": type(value).__name__,
        "contract_conformance": "FAIL",
        "runtime_evidence": "NEGATIVE",
        "compatibility_status": "INCOMPATIBLE",
        "compatibility_basis": "real invocation returned a value not JSON-serializable without coercion",
        "compatibility_promotion": "REPORT_LAYER_ONLY",
    }

def main():
    before = hashes()
    d2 = load(D2_REPORT)
    crown = load(CROWN_REPORT)
    gate = load(GATE_REPORT)

    if d2.get("contractual_preflight_identity_sha256") != EXPECTED_D2:
        raise SystemExit("P014-D2 binding drift")
    if crown.get("crown_identity_sha256") != EXPECTED_CROWN:
        raise SystemExit("P014-D2 crown binding drift")
    if gate.get("experimental_gate_identity_sha256") != EXPECTED_GATE:
        raise SystemExit("P014-D3 gate binding drift")

    rows = [x for x in d2.get("results", []) if x.get("component") == COMPONENT]
    if len(rows) != 1:
        raise SystemExit("authorized component not uniquely present in D2")
    row = rows[0]
    contract = row.get("proposed_contract")
    if not isinstance(contract, dict):
        raise SystemExit("authorized component has no explicit D2 contract")

    # Refusal/degradation tests happen before any real legacy import.
    refusals = [
        preflight(row, component="ontology/other.py", callable_name=CALLABLE,
                  source_sha256=SOURCE_SHA256, contract=contract, correlation_id="r-component"),
        preflight(row, component=COMPONENT, callable_name="__spoofed__",
                  source_sha256=SOURCE_SHA256, contract=contract, correlation_id="r-callable"),
        preflight(row, component=COMPONENT, callable_name=CALLABLE,
                  source_sha256="0"*64, contract=contract, correlation_id="r-hash"),
        preflight(row, component=COMPONENT, callable_name=CALLABLE,
                  source_sha256=SOURCE_SHA256, contract={}, correlation_id="r-contract"),
        preflight(row, component=COMPONENT, callable_name=CALLABLE,
                  source_sha256=SOURCE_SHA256, contract=contract, correlation_id=""),
    ]
    if not all(x["execution_status"] == "REFUSED" for x in refusals):
        raise SystemExit("pre-execution refusal test failed")

    correlation_id = "p014-d3-real-001"
    authorization = preflight(
        row,
        component=COMPONENT,
        callable_name=CALLABLE,
        source_sha256=SOURCE_SHA256,
        contract=contract,
        correlation_id=correlation_id,
    )
    if authorization["execution_status"] != "AUTHORIZED_EXPERIMENT":
        raise SystemExit("real experimental invocation was not authorized: " + authorization.get("reason", "unknown"))

    source = ROOT / COMPONENT
    observation = invoke_once(source, correlation_id)

    after = hashes()
    if after != before:
        raise SystemExit("canonical P014 mutation detected after real invocation")

    tests = {
        "d2_binding": True,
        "d2_crown_binding": True,
        "d3_gate_binding": True,
        "candidate_unique": len(rows) == 1,
        "candidate_contract_candidate": row.get("preflight_status") == "CONTRACT_CANDIDATE",
        "candidate_initially_unknown": row.get("compatibility_status") == "UNKNOWN",
        "candidate_initially_runtime_unauthorized": row.get("runtime_authorized") is False,
        "source_hash_verified": sha_bytes(source.read_bytes()) == SOURCE_SHA256,
        "wrong_component_refused": refusals[0]["execution_status"] == "REFUSED",
        "wrong_callable_refused": refusals[1]["execution_status"] == "REFUSED",
        "wrong_hash_refused": refusals[2]["execution_status"] == "REFUSED",
        "wrong_contract_refused": refusals[3]["execution_status"] == "REFUSED",
        "missing_correlation_refused": refusals[4]["execution_status"] == "REFUSED",
        "single_real_invocation_attempted": observation["execution_status"] in {"SUCCESS", "EXCEPTION", "REFUSED"},
        "correlation_preserved": observation.get("correlation_id") == correlation_id,
        "canonical_nonmutation": after == before,
    }
    if not all(tests.values()):
        raise SystemExit("P014-D3 first real invocation harness tests failed: " +
                         ", ".join(k for k,v in tests.items() if not v))

    body = {
        "schema": "oce.p014.d3.first_real_invocation.v1",
        "milestone": "P014-D3-FIRST-REAL-INVOCATION",
        "status": "OBSERVED",
        "bindings": {
            "p014_d2": EXPECTED_D2,
            "p014_d2_crown": EXPECTED_CROWN,
            "p014_d3_gate": EXPECTED_GATE,
        },
        "authorized_target": {
            "component": COMPONENT,
            "source_sha256": SOURCE_SHA256,
            "callable": CALLABLE,
            "contract": contract,
            "selection_basis": "bounded zero-argument metadata query; no internal calls in D2 static evidence",
        },
        "pre_execution_refusal_tests": refusals,
        "authorization": authorization,
        "observation": observation,
        "tests": tests,
        "canonical_hashes_before": before,
        "canonical_hashes_after": after,
        "epistemic_status": {
            "single_success_is_general_legacy_compatibility_proof": False,
            "verdict_scope": "this exact component, source hash, callable, contract and observed invocation only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
    }
    identity = canonical_sha(body)
    body["first_real_invocation_identity_sha256"] = identity
    REPORT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("P014_D3_FIRST_REAL_INVOCATION_OBSERVED")
    print("status=OBSERVED")
    print("component=" + COMPONENT)
    print("callable=" + CALLABLE)
    print("source_sha256=" + SOURCE_SHA256)
    print("real_invocation_attempts=1")
    print("execution_status=" + observation["execution_status"])
    print("contract_conformance=" + observation.get("contract_conformance", "UNDETERMINED"))
    print("runtime_evidence=" + observation.get("runtime_evidence", "INSUFFICIENT"))
    print("compatibility_status=" + observation.get("compatibility_status", "UNKNOWN"))
    print("compatibility_promotion=" + observation.get("compatibility_promotion", "NONE"))
    print("canonical_p014_nonmutation=OK")
    print("first_real_invocation_identity_sha256=" + identity)
    print("report=" + str(REPORT))

if __name__ == "__main__":
    main()
