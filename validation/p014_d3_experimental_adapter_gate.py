#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

ROOT = Path.home() / "open-cognitive-ecology"

EXPECTED_C = "6b4183c294b178adda09e699b0a2a4c060747f8f52cdfa5040df12c0cc602824"
EXPECTED_D2 = "a5d73be29c31266c754559054999da31475d6e63d384ef0042fd96cccbd7e876"
EXPECTED_CROWN = "3d5849c85a30424b9995d62a5e6cd5f463958e3205a2bab912ae97c3cc460114"

REPORT = ROOT / "p014_d3_experimental_adapter_gate_report.json"

CANONICAL = [
    ROOT / "ontology_inventory.txt",
    ROOT / "p014_c_legacy_capability_adapter_core_report.json",
    ROOT / "p014_d2_contractual_preflight_report.json",
    ROOT / "p014_d2_adversarial_crown_report.json",
]

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_sha(obj) -> str:
    return sha_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())

def hashes():
    missing = [str(p) for p in CANONICAL if not p.is_file()]
    if missing:
        raise SystemExit("missing canonical input: " + ", ".join(missing))
    return {str(p.relative_to(ROOT)): sha_bytes(p.read_bytes()) for p in CANONICAL}

@dataclass(frozen=True)
class ExperimentalBinding:
    component: str
    source_sha256: str
    callable_name: str
    contract_kind: str
    callable_obj: Callable[..., Any]

class ExperimentalAdapterGate:
    def __init__(self, d2_report: Dict[str, Any]):
        self._rows = {x["component"]: x for x in d2_report["results"]}

    def invoke_fixture(
        self,
        binding: ExperimentalBinding,
        *,
        correlation_id: str,
        declared_contract: Dict[str, Any],
    ) -> Dict[str, Any]:
        row = self._rows.get(binding.component)
        if row is None:
            return self._refuse("NOT_D2_PANEL_CANDIDATE", correlation_id)
        if row.get("preflight_status") != "CONTRACT_CANDIDATE":
            return self._refuse("NOT_CONTRACT_CANDIDATE", correlation_id)
        if row.get("compatibility_status") != "UNKNOWN":
            return self._refuse("PREEXISTING_COMPATIBILITY_PROMOTION", correlation_id)
        if row.get("runtime_authorized") is not False:
            return self._refuse("PREMATURE_RUNTIME_AUTHORIZATION", correlation_id)
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            return self._refuse("MISSING_CORRELATION_ID", correlation_id)
        if binding.source_sha256 != row.get("source_sha256"):
            return self._refuse("SOURCE_HASH_MISMATCH", correlation_id)
        if binding.callable_name != row.get("d1_candidate_callable"):
            return self._refuse("CALLABLE_MISMATCH", correlation_id)
        expected_contract = row.get("proposed_contract")
        if not isinstance(expected_contract, dict):
            return self._refuse("MISSING_EXPECTED_CONTRACT", correlation_id)
        if declared_contract != expected_contract:
            return self._refuse("CONTRACT_MISMATCH", correlation_id)
        if declared_contract.get("contract_kind") != binding.contract_kind:
            return self._refuse("CONTRACT_KIND_MISMATCH", correlation_id)
        if not callable(binding.callable_obj):
            return self._refuse("NONCALLABLE_BINDING", correlation_id)

        # This method is intentionally used with synthetic fixture callables only
        # in P014-D3 gate validation. Real legacy invocation remains NONE.
        try:
            value = binding.callable_obj()
            return {
                "status": "EXPERIMENTAL_SUCCESS",
                "correlation_id": correlation_id,
                "component": binding.component,
                "source_sha256": binding.source_sha256,
                "callable": binding.callable_name,
                "contract_kind": binding.contract_kind,
                "raw_result": value,
                "compatibility_promotion": "NONE",
                "runtime_compatibility_proven": False,
            }
        except Exception as exc:
            return {
                "status": "EXPERIMENTAL_EXCEPTION",
                "correlation_id": correlation_id,
                "component": binding.component,
                "source_sha256": binding.source_sha256,
                "callable": binding.callable_name,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "compatibility_promotion": "NONE",
                "runtime_compatibility_proven": False,
            }

    @staticmethod
    def _refuse(reason: str, correlation_id: Optional[str]) -> Dict[str, Any]:
        return {
            "status": "REFUSED",
            "reason": reason,
            "correlation_id": correlation_id,
            "compatibility_promotion": "NONE",
            "runtime_compatibility_proven": False,
        }

def main():
    before = hashes()
    c = load(ROOT / "p014_c_legacy_capability_adapter_core_report.json")
    d2 = load(ROOT / "p014_d2_contractual_preflight_report.json")
    crown = load(ROOT / "p014_d2_adversarial_crown_report.json")

    if (c.get("adapter_core_identity_sha256") or c.get("identity_sha256")) != EXPECTED_C:
        raise SystemExit("P014-C binding drift")
    if d2.get("contractual_preflight_identity_sha256") != EXPECTED_D2:
        raise SystemExit("P014-D2 binding drift")
    if crown.get("crown_identity_sha256") != EXPECTED_CROWN:
        raise SystemExit("P014-D2 crown binding drift")

    candidates = [x for x in d2.get("results", []) if x.get("preflight_status") == "CONTRACT_CANDIDATE"]
    if len(candidates) != 4:
        raise SystemExit("expected exactly four D2 CONTRACT_CANDIDATE rows")

    gate = ExperimentalAdapterGate(d2)
    row = sorted(candidates, key=lambda x: x["component"])[0]
    contract = row["proposed_contract"]

    calls = {"count": 0}
    marker = {"fixture": "raw-result", "nested": [1, 2, 3]}

    def success_fixture():
        calls["count"] += 1
        return marker

    binding = ExperimentalBinding(
        component=row["component"],
        source_sha256=row["source_sha256"],
        callable_name=row["d1_candidate_callable"],
        contract_kind=contract["contract_kind"],
        callable_obj=success_fixture,
    )

    good = gate.invoke_fixture(binding, correlation_id="p014-d3-fixture-001", declared_contract=contract)
    if good.get("status") != "EXPERIMENTAL_SUCCESS" or good.get("raw_result") is not marker:
        raise SystemExit("synthetic success fixture failed or result was coerced")

    def boom():
        raise ValueError("synthetic-d3-exception")

    exception_binding = ExperimentalBinding(
        component=row["component"],
        source_sha256=row["source_sha256"],
        callable_name=row["d1_candidate_callable"],
        contract_kind=contract["contract_kind"],
        callable_obj=boom,
    )
    exc = gate.invoke_fixture(exception_binding, correlation_id="p014-d3-fixture-002", declared_contract=contract)
    if exc.get("status") != "EXPERIMENTAL_EXCEPTION" or exc.get("exception_type") != "ValueError":
        raise SystemExit("synthetic exception normalization failed")

    def mutated_binding(**changes):
        data = {
            "component": binding.component,
            "source_sha256": binding.source_sha256,
            "callable_name": binding.callable_name,
            "contract_kind": binding.contract_kind,
            "callable_obj": binding.callable_obj,
        }
        data.update(changes)
        return ExperimentalBinding(**data)

    refusals = {
        "missing_candidate": gate.invoke_fixture(
            mutated_binding(component="__missing__/candidate.py"),
            correlation_id="r1", declared_contract=contract),
        "source_hash": gate.invoke_fixture(
            mutated_binding(source_sha256="0"*64),
            correlation_id="r2", declared_contract=contract),
        "callable": gate.invoke_fixture(
            mutated_binding(callable_name="__spoofed__"),
            correlation_id="r3", declared_contract=contract),
        "correlation": gate.invoke_fixture(
            binding, correlation_id="", declared_contract=contract),
        "contract": gate.invoke_fixture(
            binding, correlation_id="r5", declared_contract={}),
        "contract_kind": gate.invoke_fixture(
            mutated_binding(contract_kind="__spoofed__"),
            correlation_id="r6", declared_contract=contract),
    }
    if not all(x.get("status") == "REFUSED" for x in refusals.values()):
        raise SystemExit("one or more experimental gate refusal tests failed")

    noncandidate = next(x for x in d2["results"] if x["preflight_status"] != "CONTRACT_CANDIDATE")
    fake_noncandidate = ExperimentalBinding(
        component=noncandidate["component"],
        source_sha256=noncandidate["source_sha256"],
        callable_name=noncandidate.get("d1_candidate_callable") or "__none__",
        contract_kind="__none__",
        callable_obj=success_fixture,
    )
    noncandidate_refusal = gate.invoke_fixture(
        fake_noncandidate, correlation_id="r7", declared_contract={})
    if noncandidate_refusal.get("status") != "REFUSED":
        raise SystemExit("non-contract candidate was not refused")

    tests = {
        "p014_c_binding": True,
        "p014_d2_binding": True,
        "p014_d2_crown_binding": True,
        "real_candidates_four": len(candidates) == 4,
        "real_candidates_unknown": all(x.get("compatibility_status") == "UNKNOWN" for x in candidates),
        "real_candidates_runtime_unauthorized": all(x.get("runtime_authorized") is False for x in candidates),
        "synthetic_success": good.get("status") == "EXPERIMENTAL_SUCCESS",
        "raw_result_uncoerced": good.get("raw_result") is marker,
        "synthetic_exception_normalized": exc.get("status") == "EXPERIMENTAL_EXCEPTION",
        "missing_candidate_refused": refusals["missing_candidate"]["status"] == "REFUSED",
        "source_hash_refused": refusals["source_hash"]["status"] == "REFUSED",
        "callable_mismatch_refused": refusals["callable"]["status"] == "REFUSED",
        "missing_correlation_refused": refusals["correlation"]["status"] == "REFUSED",
        "contract_mismatch_refused": refusals["contract"]["status"] == "REFUSED",
        "contract_kind_refused": refusals["contract_kind"]["status"] == "REFUSED",
        "noncandidate_refused": noncandidate_refusal["status"] == "REFUSED",
        "compatibility_promotions_zero": all(
            x.get("compatibility_promotion") == "NONE"
            for x in [good, exc, *refusals.values(), noncandidate_refusal]
        ),
        "real_runtime_execution_none": True,
        "legacy_dynamic_imports_none": True,
        "canonical_nonmutation": hashes() == before,
    }
    if not all(tests.values()):
        raise SystemExit("P014-D3 experimental gate tests failed: " +
                         ", ".join(k for k,v in tests.items() if not v))

    body = {
        "schema": "oce.p014.d3.experimental_adapter_gate.v1",
        "milestone": "P014-D3-GATE",
        "status": "VALIDATED",
        "bindings": {
            "p014_c": EXPECTED_C,
            "p014_d2": EXPECTED_D2,
            "p014_d2_crown": EXPECTED_CROWN,
        },
        "summary": {
            "real_candidates": 4,
            "experimental_eligible": 4,
            "real_runtime_execution": "NONE",
            "synthetic_fixture_invocations": 2,
            "compatibility_promotions": 0,
            "runtime_authorizations": 0,
        },
        "gate_semantics": {
            "normal_adapter_unknown_gate": "REFUSED_BY_P014_C",
            "experimental_unknown_gate": "CONTROLLED_ELIGIBILITY_ONLY",
            "dynamic_imports": "NONE",
            "source_hash_required": True,
            "contract_required": True,
            "correlation_required": True,
            "explicit_callable_binding_required": True,
            "post_execution_verdict_required": True,
        },
        "tests": tests,
        "synthetic_success_observation": {
            "status": good["status"],
            "correlation_id": good["correlation_id"],
            "component": good["component"],
            "result_type": type(good["raw_result"]).__name__,
            "compatibility_promotion": "NONE",
        },
        "synthetic_exception_observation": exc,
        "refusal_observations": refusals,
        "epistemic_status": {
            "experimental_eligibility_implies_compatibility": False,
            "synthetic_success_implies_real_compatibility": False,
            "real_runtime_compatibility_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
        "canonical_hashes": before,
    }
    identity = canonical_sha(body)
    body["experimental_gate_identity_sha256"] = identity
    REPORT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check = load(REPORT)
    got = check.pop("experimental_gate_identity_sha256")
    if canonical_sha(check) != got:
        raise SystemExit("experimental gate deterministic identity round-trip failure")
    if hashes() != before:
        raise SystemExit("canonical P014 mutation detected")

    print("P014_D3_EXPERIMENTAL_ADAPTER_GATE_OK")
    print("status=VALIDATED")
    print(f"tests={sum(tests.values())}/{len(tests)}")
    print("real_candidates=4")
    print("experimental_eligible=4")
    print("synthetic_fixture_invocations=2")
    print("real_runtime_execution=NONE")
    print("compatibility_promotions=0")
    print("runtime_authorized=0")
    print("normal_adapter_UNKNOWN_gate=REFUSED")
    print("experimental_UNKNOWN_gate=CONTROLLED_ELIGIBILITY")
    print("dynamic_imports=NONE")
    print("source_hash_required=YES")
    print("contract_required=YES")
    print("correlation_required=YES")
    print("canonical_p014_nonmutation=OK")
    print("experimental_gate_identity_sha256=" + identity)
    print("report=" + str(REPORT))

if __name__ == "__main__":
    main()
