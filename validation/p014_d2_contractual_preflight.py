#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"

EXPECTED_A = "6698bee8229a108f290f3797b6f34e94c28040a365900dba81c98268885adae4"
EXPECTED_B = "48891a4800e4661a90dfec2f8f654cd4a4153babcee378d694085590493fc947"
EXPECTED_C = "6b4183c294b178adda09e699b0a2a4c060747f8f52cdfa5040df12c0cc602824"
EXPECTED_D1 = "7647c5369125e3b4485e9d096f4f91ef4af77765a00635baa947bee919f4a88f"

REPORT = ROOT / "p014_d2_contractual_preflight_report.json"

TEST_PREFIXES = ("test_",)
ENTRYPOINT_NAMES = {"main", "parse_args"}
CLI_MARKERS = {"argparse", "sys.argv", "__main__"}
SIDE_EFFECT_CALLS = {
    "open", "print", "input", "write", "save", "dump", "dumps",
    "run", "Popen", "system", "remove", "unlink", "mkdir", "makedirs",
    "rename", "replace", "connect", "request", "get", "post", "put", "delete",
}
METADATA_NAMES = {"get_metadata", "metadata"}
TRANSFORM_NAMES = {"step", "process", "transform", "evaluate", "compute", "predict", "detect", "classify"}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()

def canonical_sha(obj):
    return sha_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())

def ident(obj, preferred):
    return obj.get(preferred) or obj.get("identity_sha256")

def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = dotted(node.value)
        return (left + "." if left else "") + node.attr
    return ""

def public_functions(tree):
    return [
        n for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("_")
    ]

def required_args(fn):
    pos = list(fn.args.posonlyargs) + list(fn.args.args)
    req_pos = max(0, len(pos) - len(fn.args.defaults))
    req_kw = sum(x is None for x in fn.args.kw_defaults)
    return req_pos + req_kw

def function_evidence(fn):
    calls = sorted({dotted(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call) and dotted(n.func)})
    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    attrs = {dotted(n) for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
    implicit_cli = ("sys.argv" in attrs) or ("argv" in names and fn.name == "parse_args")
    side = sorted({c for c in calls if c.split(".")[-1] in SIDE_EFFECT_CALLS})
    return {
        "name": fn.name,
        "required_arguments": required_args(fn),
        "async": isinstance(fn, ast.AsyncFunctionDef),
        "calls": calls,
        "implicit_cli_dependency": implicit_cli,
        "side_effect_call_signals": side,
        "has_return": any(isinstance(n, ast.Return) for n in ast.walk(fn)),
    }

def classify(rel, tree, d1_callable):
    name = Path(rel).name
    funcs = public_functions(tree)
    evidence = [function_evidence(f) for f in funcs]
    by_name = {x["name"]: x for x in evidence}
    imports_set = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imports_set.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                imports_set.add(n.module)
    imports = sorted(imports_set)
    text_markers = set(imports)
    if any(x.startswith("argparse") for x in imports):
        text_markers.add("argparse")

    if name.startswith(TEST_PREFIXES):
        return "TEST_SURFACE_EXCLUDED", None, "root-level or nested test surface is not an initial production capability contract", evidence

    if d1_callable in ENTRYPOINT_NAMES:
        ev = by_name.get(d1_callable)
        if d1_callable == "parse_args" or (ev and ev["implicit_cli_dependency"]):
            return "ENTRYPOINT_NOT_CAPABILITY", None, "CLI/parser entrypoint has implicit process-argument semantics", evidence
        return "ENTRYPOINT_NOT_CAPABILITY", None, "program entrypoint is not treated as a capability merely because it is callable", evidence

    if d1_callable and d1_callable in by_name:
        ev = by_name[d1_callable]
        lname = d1_callable.lower()
        if lname in METADATA_NAMES:
            contract = {
                "contract_kind": "METADATA_QUERY_V1",
                "callable": d1_callable,
                "input_contract": "no required Python arguments",
                "output_contract": "returned value must be JSON-serializable without coercion",
                "error_contract": "exception is observable failure; no swallowing/coercion",
                "provenance_required": True,
                "source_hash_required": True,
                "correlation_required": True,
            }
            return "CONTRACT_CANDIDATE", contract, "explicit metadata query surface with bounded invocation shape", evidence

        if lname in TRANSFORM_NAMES or lname == "step":
            if ev["required_arguments"] == 0 and not ev["implicit_cli_dependency"]:
                if ev["side_effect_call_signals"]:
                    return "REQUIRES_DEPENDENCY_CONTRACT", None, "callable shape is bounded but static body contains side-effect/dependency signals", evidence
                contract = {
                    "contract_kind": "ZERO_ARG_TRANSFORM_V1",
                    "callable": d1_callable,
                    "input_contract": "no required Python arguments; defaults preserved exactly",
                    "output_contract": "returned Python value observed without coercion",
                    "error_contract": "exception is observable failure; no swallowing/coercion",
                    "provenance_required": True,
                    "source_hash_required": True,
                    "correlation_required": True,
                }
                return "CONTRACT_CANDIDATE", contract, "bounded transform-like callable with no required arguments", evidence

        if ev["implicit_cli_dependency"]:
            return "ENTRYPOINT_NOT_CAPABILITY", None, "implicit CLI/process dependency detected", evidence
        if ev["side_effect_call_signals"]:
            return "REQUIRES_DEPENDENCY_CONTRACT", None, "candidate callable contains unresolved side-effect/dependency signals", evidence
        return "UNRESOLVED", None, "callable is syntactically direct but semantic capability contract is not explicit enough", evidence

    return "UNRESOLVED", None, "D1 callable cannot be bound to an explicit production capability contract", evidence

def main():
    inventory = ROOT / "ontology_inventory.txt"
    paths = {
        "a": ROOT / "p014_a_legacy_capability_boundary_contract_report.json",
        "b": ROOT / "p014_b_governed_legacy_candidate_assessment_report.json",
        "c": ROOT / "p014_c_legacy_capability_adapter_core_report.json",
        "d1": ROOT / "p014_d1_representative_testability_selection_report.json",
    }
    missing = [str(x) for x in [inventory, *paths.values()] if not x.is_file()]
    if missing:
        raise SystemExit("missing required P014-D2 input: " + ", ".join(missing))

    inv_before = sha_bytes(inventory.read_bytes())
    a, b, c, d1 = [load(paths[k]) for k in ("a", "b", "c", "d1")]

    if ident(a, "contract_identity_sha256") != EXPECTED_A: raise SystemExit("P014-A binding drift")
    if ident(b, "assessment_identity_sha256") != EXPECTED_B: raise SystemExit("P014-B binding drift")
    if ident(c, "adapter_core_identity_sha256") != EXPECTED_C: raise SystemExit("P014-C binding drift")
    if d1.get("selection_identity_sha256") != EXPECTED_D1: raise SystemExit("P014-D1 binding drift")

    panel = d1.get("representative_precontract_panel", [])
    if len(panel) != 12:
        raise SystemExit("expected exactly 12 D1 panel candidates")

    d1_rows = {x["component"]: x for x in d1.get("rows", [])}
    if len(d1_rows) != 773:
        raise SystemExit("D1 LOW coverage drift")

    results = []
    for p in sorted(panel, key=lambda x: x["component"]):
        rel = p["component"]
        src = ROOT / rel
        if not src.is_file():
            raise SystemExit("missing panel source: " + rel)
        raw = src.read_bytes()
        actual = sha_bytes(raw)
        if actual != p["source_sha256"]:
            raise SystemExit("panel source hash drift: " + rel)
        row = d1_rows.get(rel)
        if not row or row.get("risk_tier") != "LOW":
            raise SystemExit("D1 row/risk binding failure: " + rel)
        if row.get("p014_b_compatibility_status") != "UNKNOWN":
            raise SystemExit("preflight cannot consume promoted compatibility: " + rel)

        tree = ast.parse(raw.decode("utf-8"), filename=rel)
        d1_callable = p.get("candidate_callable")
        status, contract, reason, evidence = classify(rel, tree, d1_callable)
        results.append({
            "component": rel,
            "family": p.get("family"),
            "source_sha256": actual,
            "d1_candidate_callable": d1_callable,
            "preflight_status": status,
            "reason": reason,
            "proposed_contract": contract,
            "static_callable_evidence": evidence,
            "compatibility_status": "UNKNOWN",
            "runtime_authorized": False,
            "runtime_execution": "NONE",
        })

    counts = Counter(x["preflight_status"] for x in results)
    allowed = {
        "CONTRACT_CANDIDATE", "REQUIRES_DEPENDENCY_CONTRACT",
        "ENTRYPOINT_NOT_CAPABILITY", "TEST_SURFACE_EXCLUDED", "UNRESOLVED"
    }
    tests = {
        "p014_a_binding": ident(a, "contract_identity_sha256") == EXPECTED_A,
        "p014_b_binding": ident(b, "assessment_identity_sha256") == EXPECTED_B,
        "p014_c_binding": ident(c, "adapter_core_identity_sha256") == EXPECTED_C,
        "p014_d1_binding": d1.get("selection_identity_sha256") == EXPECTED_D1,
        "panel_exactly_12": len(results) == 12,
        "panel_unique": len({x["component"] for x in results}) == 12,
        "all_low": all(d1_rows[x["component"]]["risk_tier"] == "LOW" for x in results),
        "source_hashes_verified": all(x["source_sha256"] for x in results),
        "statuses_governed": all(x["preflight_status"] in allowed for x in results),
        "root_test_files_excluded": all(
            x["preflight_status"] == "TEST_SURFACE_EXCLUDED"
            for x in results if Path(x["component"]).name.startswith("test_")
        ),
        "main_not_capability": all(
            x["preflight_status"] in {"ENTRYPOINT_NOT_CAPABILITY", "TEST_SURFACE_EXCLUDED"}
            for x in results if x["d1_candidate_callable"] == "main"
        ),
        "parse_args_not_capability": all(
            x["preflight_status"] == "ENTRYPOINT_NOT_CAPABILITY"
            for x in results if x["d1_candidate_callable"] == "parse_args"
        ),
        "contracts_only_for_candidates": all(
            (x["proposed_contract"] is not None) == (x["preflight_status"] == "CONTRACT_CANDIDATE")
            for x in results
        ),
        "compatibility_preserved_unknown": all(x["compatibility_status"] == "UNKNOWN" for x in results),
        "runtime_authorized_zero": all(not x["runtime_authorized"] for x in results),
        "runtime_execution_none": all(x["runtime_execution"] == "NONE" for x in results),
        "ontology_nonmutation": sha_bytes(inventory.read_bytes()) == inv_before,
    }
    if not all(tests.values()):
        raise SystemExit("P014-D2 tests failed: " + ", ".join(k for k,v in tests.items() if not v))

    body = {
        "schema": "oce.p014.d2.contractual_preflight.v1",
        "milestone": "P014-D2",
        "status": "VALIDATED",
        "bindings": {"p014_a": EXPECTED_A, "p014_b": EXPECTED_B, "p014_c": EXPECTED_C, "p014_d1": EXPECTED_D1},
        "method": {
            "analysis": "static AST contractual preflight",
            "legacy_imports": "NONE",
            "runtime_execution": "NONE",
            "runtime_authorizations": 0,
            "compatibility_promotions": 0,
            "contract_candidate_semantics": "eligible for D3 design only; not COMPATIBLE and not authorized",
        },
        "summary": {
            "panel": 12,
            "preflight_counts": dict(sorted(counts.items())),
            "contract_candidates": counts.get("CONTRACT_CANDIDATE", 0),
            "runtime_authorized": 0,
            "compatibility_promotions": 0,
        },
        "results": results,
        "tests": tests,
        "epistemic_status": {
            "contract_candidate_implies_compatible": False,
            "contract_candidate_implies_safe": False,
            "runtime_compatibility_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
    }
    identity = canonical_sha(body)
    body["contractual_preflight_identity_sha256"] = identity
    REPORT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check = load(REPORT)
    got = check.pop("contractual_preflight_identity_sha256")
    if canonical_sha(check) != got:
        raise SystemExit("deterministic report identity round-trip failure")
    if sha_bytes(inventory.read_bytes()) != inv_before:
        raise SystemExit("ontology_inventory.txt mutated")

    print("P014_D2_CONTRACTUAL_PREFLIGHT_OK")
    print("status=VALIDATED")
    print(f"tests={sum(tests.values())}/{len(tests)}")
    print("panel=12")
    for k in sorted(allowed):
        print(f"{k}={counts.get(k,0)}")
    print("runtime_execution=NONE")
    print("legacy_imports=NONE")
    print("runtime_authorized=0")
    print("compatibility_promotions=0")
    print("compatibility_status=UNKNOWN")
    print("ontology_inventory_non_mutation=OK")
    print("contractual_preflight_identity_sha256=" + identity)
    print("report=" + str(REPORT))

if __name__ == "__main__":
    main()
