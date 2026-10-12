#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"

EXPECTED_P014_A = "6698bee8229a108f290f3797b6f34e94c28040a365900dba81c98268885adae4"
EXPECTED_P014_B = "48891a4800e4661a90dfec2f8f654cd4a4153babcee378d694085590493fc947"
EXPECTED_P014_C = "6b4183c294b178adda09e699b0a2a4c060747f8f52cdfa5040df12c0cc602824"
EXPECTED_PROFILE = "d9331f5afd3587cc1767777e4eced85c68f9a42bb5180fa7a0a178e01d007702"

REPORT = ROOT / "p014_d1_representative_testability_selection_report.json"

EXCLUDED_TOP_LEVEL = {"tests", "test", "examples", "example", "validation", "benchmarks", "benchmark"}
PRIMITIVE_ANNOTATIONS = {
    "str": "", "int": 0, "float": 0.0, "bool": False,
    "dict": {}, "list": [], "tuple": [], "set": []
}

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical_sha(obj) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())

def identity_from(report, key):
    return report.get(key) or report.get("identity_sha256")

def required_count(args: ast.arguments) -> int:
    positional = len(args.posonlyargs) + len(args.args)
    defaults = len(args.defaults)
    required_positional = max(0, positional - defaults)
    required_kwonly = sum(x is None for x in args.kw_defaults)
    return required_positional + required_kwonly

def annotation_name(node):
    if node is None:
        return None
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None

def primitive_constructible(fn):
    req_nodes = []
    pos = list(fn.args.posonlyargs) + list(fn.args.args)
    nreq = max(0, len(pos) - len(fn.args.defaults))
    req_nodes.extend(pos[:nreq])
    req_nodes.extend(a for a, d in zip(fn.args.kwonlyargs, fn.args.kw_defaults) if d is None)
    if not req_nodes:
        return True
    return all(annotation_name(a.annotation) in PRIMITIVE_ANNOTATIONS for a in req_nodes)

def top_level_call_names(tree):
    names = []
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            targets = [node.value]
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            v = getattr(node, "value", None)
            if isinstance(v, ast.Call):
                targets = [v]
        for call in targets:
            f = call.func
            if isinstance(f, ast.Name):
                names.append(f.id)
            elif isinstance(f, ast.Attribute):
                names.append(f.attr)
    return sorted(set(names))

def classify_source(path: Path):
    raw = path.read_bytes()
    tree = ast.parse(raw.decode("utf-8"), filename=str(path))
    public_functions = [
        n for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("_")
    ]
    public_classes = [
        n for n in tree.body
        if isinstance(n, ast.ClassDef) and not n.name.startswith("_")
    ]
    direct = []
    constructible = []
    dependent = []
    for fn in public_functions:
        req = required_count(fn.args)
        item = {
            "name": fn.name,
            "kind": "async_function" if isinstance(fn, ast.AsyncFunctionDef) else "function",
            "required_arguments": req,
            "primitive_constructible": primitive_constructible(fn),
        }
        if req == 0:
            direct.append(item)
        elif item["primitive_constructible"]:
            constructible.append(item)
        else:
            dependent.append(item)

    top = path.relative_to(ROOT).parts[0] if path.relative_to(ROOT).parts else ""
    excluded_surface = top.lower() in EXCLUDED_TOP_LEVEL
    top_calls = top_level_call_names(tree)

    if excluded_surface:
        status = "UNSUITABLE_INITIAL_CAMPAIGN"
        reason = "non-production surface excluded from representative initial runtime campaign"
    elif direct:
        status = "DIRECT"
        reason = "public top-level callable with no required arguments"
    elif constructible:
        status = "CONSTRUCTIBLE"
        reason = "public top-level callable whose required arguments have primitive annotations"
    elif public_functions or public_classes:
        status = "DEPENDENT"
        reason = "public surface exists but requires unresolved construction/dependencies"
    else:
        status = "UNSUITABLE_INITIAL_CAMPAIGN"
        reason = "no explicit public top-level callable surface"

    return {
        "testability_status": status,
        "reason": reason,
        "public_function_count": len(public_functions),
        "public_class_count": len(public_classes),
        "direct_callables": direct,
        "constructible_callables": constructible,
        "dependent_callable_count": len(dependent),
        "top_level_call_names": top_calls,
        "excluded_surface": excluded_surface,
    }

def main():
    inventory = ROOT / "ontology_inventory.txt"
    a_path = ROOT / "p014_a_legacy_capability_boundary_contract_report.json"
    b_path = ROOT / "p014_b_governed_legacy_candidate_assessment_report.json"
    c_path = ROOT / "p014_c_legacy_capability_adapter_core_report.json"
    p_path = ROOT / "p014_d_runtime_risk_profiles.json"

    required = [inventory, a_path, b_path, c_path, p_path]
    missing = [str(x) for x in required if not x.is_file()]
    if missing:
        raise SystemExit("missing required P014-D1 inputs: " + ", ".join(missing))

    inv_before = sha256_bytes(inventory.read_bytes())
    a, b, c, profile = map(load_json, [a_path, b_path, c_path, p_path])

    if identity_from(a, "contract_identity_sha256") != EXPECTED_P014_A:
        raise SystemExit("P014-A binding drift")
    if identity_from(b, "assessment_identity_sha256") != EXPECTED_P014_B:
        raise SystemExit("P014-B binding drift")
    if identity_from(c, "adapter_core_identity_sha256") != EXPECTED_P014_C:
        raise SystemExit("P014-C binding drift")
    if profile.get("profile_identity_sha256") != EXPECTED_PROFILE:
        raise SystemExit("P014-D risk-profile binding drift")

    profiles = profile.get("profiles", [])
    if len(profiles) != 973:
        raise SystemExit(f"expected 973 risk profiles, got {len(profiles)}")
    low = [x for x in profiles if x.get("risk_tier") == "LOW"]
    if len(low) != 773:
        raise SystemExit(f"expected 773 LOW candidates, got {len(low)}")

    b_rows = {x["component"]: x for x in b.get("assessments", [])}
    if len(b_rows) != 973:
        raise SystemExit("P014-B candidate coverage drift")

    rows = []
    for rp in sorted(low, key=lambda x: x["component"]):
        rel = rp["component"]
        src = ROOT / rel
        if not src.is_file():
            raise SystemExit("missing LOW source: " + rel)
        raw = src.read_bytes()
        actual = sha256_bytes(raw)
        if actual != rp.get("source_sha256"):
            raise SystemExit("P014-D source drift: " + rel)
        br = b_rows.get(rel)
        if not br or br.get("source_sha256") != actual:
            raise SystemExit("P014-B/P014-D source binding drift: " + rel)
        if br.get("compatibility_status") != "UNKNOWN":
            raise SystemExit("unexpected pre-D1 compatibility promotion: " + rel)

        cls = classify_source(src)
        family = rel.split("/", 1)[0]
        rows.append({
            "component": rel,
            "family": family,
            "source_sha256": actual,
            "risk_tier": "LOW",
            "p014_b_compatibility_status": "UNKNOWN",
            **cls,
            "runtime_execution": "NONE",
            "target_contract_status": "UNRESOLVED",
            "compatibility_promotion": "NONE",
        })

    counts = Counter(x["testability_status"] for x in rows)

    # Deterministic representative pre-contract panel:
    # at most one DIRECT candidate per production family, then fill to 12
    # from remaining DIRECT candidates in lexical family/path order.
    direct = [x for x in rows if x["testability_status"] == "DIRECT"]
    by_family = defaultdict(list)
    for x in direct:
        by_family[x["family"]].append(x)
    for fam in by_family:
        by_family[fam].sort(key=lambda x: x["component"])

    panel = []
    for fam in sorted(by_family):
        if by_family[fam]:
            panel.append(by_family[fam][0])
        if len(panel) >= 12:
            break
    if len(panel) < 12:
        used = {x["component"] for x in panel}
        for x in sorted(direct, key=lambda y: (y["family"], y["component"])):
            if x["component"] not in used:
                panel.append(x)
                used.add(x["component"])
            if len(panel) >= 12:
                break

    panel_rows = [{
        "component": x["component"],
        "family": x["family"],
        "source_sha256": x["source_sha256"],
        "candidate_callable": x["direct_callables"][0]["name"] if x["direct_callables"] else None,
        "selection_status": "PRECONTRACT_CANDIDATE",
        "runtime_authorized": False,
        "reason": "representative static testability candidate; explicit V2 target contract still unresolved",
    } for x in panel]

    tests = {
        "p014_a_binding": identity_from(a, "contract_identity_sha256") == EXPECTED_P014_A,
        "p014_b_binding": identity_from(b, "assessment_identity_sha256") == EXPECTED_P014_B,
        "p014_c_binding": identity_from(c, "adapter_core_identity_sha256") == EXPECTED_P014_C,
        "risk_profile_binding": profile.get("profile_identity_sha256") == EXPECTED_PROFILE,
        "profile_population_973": len(profiles) == 973,
        "low_population_773": len(low) == 773,
        "low_coverage_773": len(rows) == 773,
        "source_hashes_verified": all(x["source_sha256"] for x in rows),
        "all_preexisting_unknown": all(x["p014_b_compatibility_status"] == "UNKNOWN" for x in rows),
        "runtime_execution_none": all(x["runtime_execution"] == "NONE" for x in rows),
        "compatibility_promotion_none": all(x["compatibility_promotion"] == "NONE" for x in rows),
        "target_contracts_unresolved": all(x["target_contract_status"] == "UNRESOLVED" for x in rows),
        "nonproduction_excluded": all(
            x["testability_status"] == "UNSUITABLE_INITIAL_CAMPAIGN"
            for x in rows if x["excluded_surface"]
        ),
        "panel_max_12": len(panel_rows) <= 12,
        "panel_direct_only": all(
            next(r for r in rows if r["component"] == p["component"])["testability_status"] == "DIRECT"
            for p in panel_rows
        ),
        "panel_runtime_unauthorized": all(not p["runtime_authorized"] for p in panel_rows),
        "panel_unique": len({p["component"] for p in panel_rows}) == len(panel_rows),
        "ontology_nonmutation": sha256_bytes(inventory.read_bytes()) == inv_before,
    }
    if not all(tests.values()):
        bad = [k for k, v in tests.items() if not v]
        raise SystemExit("P014-D1 test failure: " + ", ".join(bad))

    body = {
        "schema": "oce.p014.d1.representative_testability_selection.v1",
        "milestone": "P014-D1",
        "status": "VALIDATED",
        "method": {
            "analysis": "static AST only",
            "imports_of_legacy_modules": "NONE",
            "runtime_execution": "NONE",
            "compatibility_promotion": "NONE",
            "selection_scope": "LOW risk only",
            "nonproduction_surfaces": sorted(EXCLUDED_TOP_LEVEL),
            "panel_semantics": "PRECONTRACT_CANDIDATE only; not COMPATIBLE and not runtime-authorized",
        },
        "bindings": {
            "p014_a": EXPECTED_P014_A,
            "p014_b": EXPECTED_P014_B,
            "p014_c": EXPECTED_P014_C,
            "p014_d_risk_profile": EXPECTED_PROFILE,
        },
        "summary": {
            "p014_candidates": 973,
            "low_candidates": 773,
            "testability_counts": dict(sorted(counts.items())),
            "precontract_panel_size": len(panel_rows),
            "precontract_panel_families": sorted({x["family"] for x in panel_rows}),
            "real_runtime_execution_count": 0,
            "compatibility_promotions": 0,
        },
        "representative_precontract_panel": panel_rows,
        "rows": rows,
        "tests": tests,
        "epistemic_status": {
            "LOW_implies_safe": False,
            "DIRECT_implies_compatible": False,
            "PRECONTRACT_CANDIDATE_implies_runtime_authorized": False,
            "compatibility_remains_unresolved": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
    }
    identity = canonical_sha(body)
    body["selection_identity_sha256"] = identity
    REPORT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # deterministic round-trip
    check = load_json(REPORT)
    got = check.pop("selection_identity_sha256")
    if canonical_sha(check) != got:
        raise SystemExit("P014-D1 deterministic identity round-trip failed")

    inv_after = sha256_bytes(inventory.read_bytes())
    if inv_after != inv_before:
        raise SystemExit("ontology_inventory.txt mutated")

    print("P014_D1_REPRESENTATIVE_TESTABILITY_SELECTION_OK")
    print("status=VALIDATED")
    print(f"tests={sum(tests.values())}/{len(tests)}")
    print("P014_candidates=973")
    print("LOW_candidates=773")
    for k in sorted(counts):
        print(f"{k}={counts[k]}")
    print(f"precontract_panel={len(panel_rows)}")
    print(f"precontract_families={len(set(x['family'] for x in panel_rows))}")
    print("runtime_execution=NONE")
    print("legacy_imports=NONE")
    print("compatibility_promotions=0")
    print("target_contracts=UNRESOLVED")
    print("p014_a_binding=VERIFIED")
    print("p014_b_binding=VERIFIED")
    print("p014_c_binding=VERIFIED")
    print("ontology_inventory_non_mutation=OK")
    print("selection_identity_sha256=" + identity)
    print("report=" + str(REPORT))

if __name__ == "__main__":
    main()
