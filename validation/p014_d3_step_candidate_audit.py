#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"

CANDIDATES = {
    "ontology/civilizational_notification_engine.py": {
        "callable": "step",
        "sha256": "08c1459cb64b54f59179b38a3dd94443223b009a2fd815390df9177fc36e394e",
    },
    "ontology/conversational_event_detector.py": {
        "callable": "step",
        "sha256": "08cae4fa4fab80e801d5bd4323b39cbae5ca86577b4010af1043b003431ad783",
    },
}

EXPECTED_D2 = "a5d73be29c31266c754559054999da31475d6e63d384ef0042fd96cccbd7e876"
EXPECTED_SECOND_METADATA = "352ae70747a6536e902d35fd60df14bc89c32a827214ffb030364c70668adf78"

D2_REPORT = ROOT / "p014_d2_contractual_preflight_report.json"
SECOND_REPORT = ROOT / "p014_d3_second_metadata_candidate_report.json"
REPORT = ROOT / "p014_d3_step_candidate_audit_report.json"

def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_sha(obj) -> str:
    return sha_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def verify_identity(report: dict, field: str, expected: str, label: str):
    if report.get(field) != expected:
        raise SystemExit(label + " identity drift")
    tmp = dict(report)
    got = tmp.pop(field, None)
    if canonical_sha(tmp) != got:
        raise SystemExit(label + " identity round-trip failure")

def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return (base + "." + node.attr) if base else node.attr
    return ""

def literalish(node):
    try:
        return ast.literal_eval(node)
    except Exception:
        return None

def analyze(path: Path, callable_name: str):
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(path))

    imports = []
    top_level_calls = []
    global_assignments = []
    functions = {}
    classes = {}
    risky_calls = []
    mutation_signals = []
    time_signals = []
    io_signals = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                name = dotted(t)
                if name:
                    global_assignments.append(name)
            value = node.value
            if isinstance(value, ast.Call):
                top_level_calls.append(dotted(value.func))
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            top_level_calls.append(dotted(node.value.func))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = node
        elif isinstance(node, ast.ClassDef):
            classes[node.name] = node

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = dotted(node.func)
            low = name.lower()
            if any(x in low for x in (
                "open", "write", "unlink", "remove", "rename", "replace", "mkdir",
                "makedirs", "rmdir", "subprocess", "system", "popen", "socket",
                "requests.", "urllib", "http.", "shutil.", "pathlib.path.write"
            )):
                risky_calls.append(name)
            if any(x in low for x in ("time.", "datetime.", "_now", "utcnow", "now")):
                time_signals.append(name)
            if any(x in low for x in (
                "open", "write", "read_text", "read_bytes", "write_text", "write_bytes",
                "unlink", "remove", "rename", "replace", "mkdir", "makedirs"
            )):
                io_signals.append(name)
        elif isinstance(node, (ast.AugAssign, ast.Delete)):
            mutation_signals.append(type(node).__name__)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                n = dotted(t)
                if "." in n or "[" in ast.unparse(t) if hasattr(ast, "unparse") else False:
                    mutation_signals.append(n or type(t).__name__)

    fn = functions.get(callable_name)
    callable_info = {"present": fn is not None}
    if fn is not None:
        args = fn.args
        callable_info.update({
            "positional_args": [a.arg for a in args.posonlyargs + args.args],
            "kwonly_args": [a.arg for a in args.kwonlyargs],
            "defaults_count": len(args.defaults),
            "kw_defaults_count": sum(x is not None for x in args.kw_defaults),
            "calls": sorted({dotted(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call) and dotted(n.func)}),
            "returns": len([n for n in ast.walk(fn) if isinstance(n, ast.Return)]),
        })

    # Analyze ENGINE class if a module-level ENGINE = SomeClass(...) exists.
    engine_class = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "ENGINE" for t in node.targets):
                if isinstance(node.value, ast.Call):
                    engine_class = dotted(node.value.func)
    engine_step = {}
    if engine_class and engine_class in classes:
        for item in classes[engine_class].body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == callable_name:
                engine_step = {
                    "calls": sorted({dotted(n.func) for n in ast.walk(item) if isinstance(n, ast.Call) and dotted(n.func)}),
                    "assignments": sorted({
                        dotted(t)
                        for n in ast.walk(item) if isinstance(n, (ast.Assign, ast.AnnAssign))
                        for t in (n.targets if isinstance(n, ast.Assign) else [n.target])
                        if dotted(t)
                    }),
                    "returns": len([n for n in ast.walk(item) if isinstance(n, ast.Return)]),
                }

    score = 0
    reasons = []
    if top_level_calls:
        score += 2
        reasons.append("top_level_calls")
    if engine_class:
        score += 2
        reasons.append("global_engine_instance")
    if risky_calls:
        score += 4
        reasons.append("potential_external_io_or_process")
    if time_signals:
        score += 2
        reasons.append("time_dependency")
    if mutation_signals:
        score += 2
        reasons.append("mutation_signals")
    if io_signals:
        score += 3
        reasons.append("io_signals")
    if engine_step.get("assignments"):
        score += 2
        reasons.append("engine_step_assignments")

    return {
        "component": str(path.relative_to(ROOT)),
        "sha256": sha_bytes(path.read_bytes()),
        "callable": callable_name,
        "imports": sorted(set(imports)),
        "top_level_calls": sorted(set(x for x in top_level_calls if x)),
        "global_assignments": sorted(set(global_assignments)),
        "global_engine_class": engine_class,
        "callable_info": callable_info,
        "engine_step": engine_step,
        "potential_risky_calls": sorted(set(risky_calls)),
        "time_signals": sorted(set(time_signals)),
        "io_signals": sorted(set(io_signals)),
        "mutation_signals_count": len(mutation_signals),
        "static_risk_score": score,
        "static_risk_reasons": sorted(set(reasons)),
    }

def main():
    inventory = ROOT / "ontology_inventory.txt"
    if not inventory.is_file():
        raise SystemExit("ontology_inventory.txt missing")

    d2 = load(D2_REPORT)
    second = load(SECOND_REPORT)
    verify_identity(d2, "contractual_preflight_identity_sha256", EXPECTED_D2, "P014-D2")
    verify_identity(second, "second_metadata_candidate_identity_sha256",
                    EXPECTED_SECOND_METADATA, "P014-D3 second metadata")

    if second.get("epistemic_status", {}).get("cross_component_contract_evidence") != "POSITIVE":
        raise SystemExit("cross-component metadata evidence not positive")

    inventory_before = sha_bytes(inventory.read_bytes())

    results = []
    for component, expected in sorted(CANDIDATES.items()):
        path = ROOT / component
        if not path.is_file():
            raise SystemExit("candidate source missing: " + component)
        if sha_bytes(path.read_bytes()) != expected["sha256"]:
            raise SystemExit("candidate source SHA drift: " + component)

        rows = [x for x in d2.get("results", []) if x.get("component") == component]
        if len(rows) != 1:
            raise SystemExit("candidate not uniquely present in D2: " + component)
        row = rows[0]
        if row.get("preflight_status") != "CONTRACT_CANDIDATE":
            raise SystemExit("candidate no longer CONTRACT_CANDIDATE: " + component)
        if row.get("compatibility_status") != "UNKNOWN":
            raise SystemExit("historical compatibility status drift: " + component)
        if row.get("runtime_authorized") is not False:
            raise SystemExit("historical runtime authorization drift: " + component)
        if row.get("d1_candidate_callable") != "step":
            raise SystemExit("D2 callable drift: " + component)
        contract = row.get("proposed_contract", {})
        if contract.get("contract_kind") != "ZERO_ARG_TRANSFORM_V1":
            raise SystemExit("D2 contract drift: " + component)

        analysis = analyze(path, "step")
        analysis["d2_contract"] = contract
        analysis["d2_compatibility_status"] = row.get("compatibility_status")
        analysis["runtime_execution"] = "NONE"
        results.append(analysis)

    # Lower score is only a static experimental-risk preference, never compatibility evidence.
    ordered = sorted(results, key=lambda x: (x["static_risk_score"], x["component"]))
    selected = ordered[0]
    tie = len(ordered) > 1 and ordered[0]["static_risk_score"] == ordered[1]["static_risk_score"]

    tests = {
        "candidate_count_two": len(results) == 2,
        "all_source_hashes_verified": all(
            x["sha256"] == CANDIDATES[x["component"]]["sha256"] for x in results
        ),
        "all_callable_step_present": all(x["callable_info"].get("present") for x in results),
        "all_historical_unknown": all(x["d2_compatibility_status"] == "UNKNOWN" for x in results),
        "runtime_execution_none": all(x["runtime_execution"] == "NONE" for x in results),
        "selection_is_static_only": True,
        "compatibility_promotions_zero": True,
        "ontology_inventory_nonmutation": sha_bytes(inventory.read_bytes()) == inventory_before,
    }
    if not all(tests.values()):
        raise SystemExit("P014-D3 step candidate audit tests failed")

    body = {
        "schema": "oce.p014.d3.step_candidate_audit.v1",
        "milestone": "P014-D3-STEP-CANDIDATE-AUDIT",
        "status": "VALIDATED",
        "bindings": {
            "p014_d2": EXPECTED_D2,
            "p014_d3_second_metadata": EXPECTED_SECOND_METADATA,
        },
        "results": results,
        "selection": {
            "selected_component": selected["component"],
            "selected_callable": "step",
            "selected_source_sha256": selected["sha256"],
            "selected_static_risk_score": selected["static_risk_score"],
            "tie": tie,
            "criterion": "lowest static experimental-risk score; lexical tie-break only",
            "compatibility_inference": "NONE",
            "runtime_authorization": False,
        },
        "tests": tests,
        "epistemic_status": {
            "static_risk_score_is_compatibility_evidence": False,
            "selection_is_runtime_compatibility_proof": False,
            "runtime_execution": "NONE",
            "compatibility_promotions": 0,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
    }
    identity = canonical_sha(body)
    body["step_candidate_audit_identity_sha256"] = identity
    REPORT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("P014_D3_STEP_CANDIDATE_AUDIT_OK")
    print("status=VALIDATED")
    print(f"tests={sum(tests.values())}/{len(tests)}")
    print("candidate_count=2")
    for x in sorted(results, key=lambda y: y["component"]):
        print("candidate=" + x["component"])
        print("static_risk_score=" + str(x["static_risk_score"]))
        print("global_engine=" + str(x["global_engine_class"] or "NONE"))
        print("top_level_calls=" + str(len(x["top_level_calls"])))
        print("risky_calls=" + str(len(x["potential_risky_calls"])))
        print("time_signals=" + str(len(x["time_signals"])))
        print("io_signals=" + str(len(x["io_signals"])))
    print("selected_component=" + selected["component"])
    print("selection_tie=" + ("YES" if tie else "NO"))
    print("runtime_execution=NONE")
    print("compatibility_promotions=0")
    print("ontology_inventory_nonmutation=OK")
    print("step_candidate_audit_identity_sha256=" + identity)
    print("report=" + str(REPORT))

if __name__ == "__main__":
    main()
