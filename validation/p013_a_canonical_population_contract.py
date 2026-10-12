#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json, subprocess
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
OUT = ROOT / "p013_a_canonical_population_contract_report.json"
INV = ROOT / "ontology_inventory.txt"

P008 = ROOT / "p008_global_audit_report.json"
P012 = ROOT / "p012_a2_component_segmentation_report.json"
P012E = ROOT / "p012_e_final_lock_report.json"

ALLOWED_DECISIONS = ["KEEP", "ADAPT", "WRAP", "MERGE", "REPLACE", "DEPRECATE", "UNKNOWN"]

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p: Path):
    return json.loads(p.read_text())

def git_lines(*args):
    cp = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True)
    return [x for x in cp.stdout.splitlines() if x.strip()]

def fail(msg):
    raise SystemExit("P013_A_REFUSED: " + msg)

for p in (INV, P008, P012, P012E):
    if not p.is_file():
        fail("missing prerequisite: " + str(p))

inv_before = sha(INV)
p008, p012, p012e = load(P008), load(P012), load(P012E)

if p012e.get("status") != "LOCKED":
    fail("P012-E is not LOCKED")
if p012e.get("final_lock_identity_sha256") != "c46a6eb9a5c485a96b5666b370f14ee880ab29066b498a673b5c70e4c1515d19":
    fail("P012-E identity drift")

tracked = sorted(set(git_lines("ls-files", "*.py")))
if not tracked:
    fail("empty tracked Python population")

p008_by_path = {x.get("path"): x for x in p008.get("modules", []) if x.get("path")}
p012_by_path = {x.get("path"): x for x in p012.get("components", []) if x.get("path")}

components = []
parse_errors = []
for rel in tracked:
    p = ROOT / rel
    if not p.is_file():
        fail("tracked Python file missing from working tree: " + rel)
    raw = p.read_bytes()
    try:
        tree = ast.parse(raw.decode("utf-8"), filename=rel)
        parse_status = "OK"
        functions = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
        classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
    except Exception as e:
        parse_status = "ERROR"
        functions = classes = 0
        parse_errors.append({"path": rel, "error": f"{type(e).__name__}: {e}"})

    a8 = p008_by_path.get(rel)
    a12 = p012_by_path.get(rel)
    provenance = []
    if a8: provenance.append("P008_ARCHITECTURAL_AUDIT")
    if a12: provenance.append("P012_PRODUCT_SEGMENTATION")
    provenance.append("GIT_TRACKED_SOURCE")

    components.append({
        "path": rel,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "parse_status": parse_status,
        "function_count": functions,
        "class_count": classes,
        "provenance": provenance,
        "p008_present": bool(a8),
        "p008_domains": (a8 or {}).get("domains", []),
        "p008_interfaces": (a8 or {}).get("interfaces", []),
        "p012_present": bool(a12),
        "p012_families": (a12 or {}).get("families", []),
        "p012_evidence_surfaces": (a12 or {}).get("evidence_surfaces", []),
        "migration_decision": "UNKNOWN",
        "decision_status": "UNASSESSED",
        "v2_target": "UNKNOWN",
        "justification": "UNKNOWN",
        "migration_risk": "UNKNOWN",
        "dependencies": "UNKNOWN",
    })

contract = {
    "allowed_decisions": ALLOWED_DECISIONS,
    "decision_semantics": {
        "KEEP": "retain component substantially unchanged because evidence supports direct V2 fit",
        "ADAPT": "modify component while preserving its principal responsibility",
        "WRAP": "preserve legacy component behind a V2-compatible boundary or adapter",
        "MERGE": "consolidate overlapping responsibilities into a selected V2 target",
        "REPLACE": "supersede component with another implementation when justified by evidence",
        "DEPRECATE": "retire component from the active V2 architecture while preserving traceability",
        "UNKNOWN": "insufficient evidence for a governed migration decision",
    },
    "mandatory_fields_before_non_unknown_decision": [
        "migration_decision", "v2_target", "justification", "migration_risk", "dependencies"
    ],
    "rules": [
        "No decision may be inferred from filename alone.",
        "Product relevance does not imply KEEP.",
        "Absence from P012 does not imply DEPRECATE.",
        "Presence in P008 does not imply KEEP.",
        "Working-tree modification does not imply ADAPT or REPLACE.",
        "MERGE requires explicit overlap evidence and a named target.",
        "REPLACE requires an identified replacement or target architecture.",
        "DEPRECATE requires explicit evidence that V2 does not require the responsibility or that it is safely superseded.",
        "UNKNOWN is mandatory when evidence is insufficient or contradictory.",
        "P013 records migration decisions only; it must not implement P014 adapters or mutate functional modules.",
    ],
}

payload = {
    "schema": "oce.p013.canonical_population_contract.v1",
    "milestone": "P013-A",
    "status": "CANONICAL_POPULATION_AND_DECISION_CONTRACT_COMPLETE",
    "population_basis": "CURRENT_GIT_TRACKED_PYTHON_SOURCES",
    "component_count": len(components),
    "parse_error_count": len(parse_errors),
    "parse_errors": parse_errors,
    "p008_joined_count": sum(x["p008_present"] for x in components),
    "p012_joined_count": sum(x["p012_present"] for x in components),
    "initial_decision_counts": {d: (len(components) if d == "UNKNOWN" else 0) for d in ALLOWED_DECISIONS},
    "decision_contract": contract,
    "components": components,
    "prerequisite_locks": {
        "p012_e_final_lock_identity_sha256": p012e["final_lock_identity_sha256"],
        "p012_e_report_sha256": sha(P012E),
        "p008_report_sha256": sha(P008),
        "p012_a2_report_sha256": sha(P012),
    },
    "ontology_inventory_sha256": inv_before,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
}

identity_payload = dict(payload)
payload["population_contract_identity_sha256"] = hashlib.sha256(
    json.dumps(identity_payload, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

if sha(INV) != inv_before:
    fail("ontology inventory mutated")

OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

roundtrip = load(OUT)
reported = roundtrip.pop("population_contract_identity_sha256")
recomputed = hashlib.sha256(
    json.dumps(roundtrip, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
if reported != recomputed:
    fail("identity determinism failure")
if sha(INV) != inv_before:
    fail("ontology inventory mutated after report write")

print("P013_A_CANONICAL_POPULATION_CONTRACT_OK")
print(f"components={len(components)}")
print(f"parse_errors={len(parse_errors)}")
print(f"p008_joined={sum(x['p008_present'] for x in components)}")
print(f"p012_joined={sum(x['p012_present'] for x in components)}")
print(f"initial_UNKNOWN={len(components)}/{len(components)}")
print("allowed_decisions=" + ",".join(ALLOWED_DECISIONS))
print("p012_e_lock=VERIFIED")
print("ontology_inventory_non_mutation=OK")
print("population_contract_identity_sha256=" + reported)
print("report=" + str(OUT))
