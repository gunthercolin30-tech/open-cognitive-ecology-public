#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
INV = ROOT / "ontology_inventory.txt"
A = ROOT / "p013_a_canonical_population_contract_report.json"
P008 = ROOT / "p008_global_audit_report.json"
P012A2 = ROOT / "p012_a2_component_segmentation_report.json"
P012E = ROOT / "p012_e_final_lock_report.json"
REGISTRIES = [ROOT / "dependency_registry.py", ROOT / "ontology" / "dependency_registry.py"]
OUT = ROOT / "p013_b_evidence_enriched_migration_assessment_report.json"

EXPECTED_A_ID = "c81a2b24140cbe31f3d0fb9f64b320a35c6d689b3e4ac01b0a67bed391ad4d3b"
EXPECTED_P012E_ID = "c46a6eb9a5c485a96b5666b370f14ee880ab29066b498a673b5c70e4c1515d19"

def fail(msg): raise SystemExit("P013_B_REFUSED: " + msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())

for p in [INV, A, P008, P012A2, P012E, *REGISTRIES]:
    if not p.is_file(): fail("missing prerequisite: " + str(p))

inv_before = sha(INV)
a, p8, a2, e = load(A), load(P008), load(P012A2), load(P012E)

if a.get("status") != "CANONICAL_POPULATION_AND_DECISION_CONTRACT_COMPLETE": fail("P013-A status drift")
if a.get("population_contract_identity_sha256") != EXPECTED_A_ID: fail("P013-A identity drift")
if e.get("status") != "LOCKED" or e.get("final_lock_identity_sha256") != EXPECTED_P012E_ID: fail("P012-E lock drift")
if a.get("component_count") != 2095: fail("P013-A population drift")
if any(c.get("migration_decision") != "UNKNOWN" for c in a.get("components", [])): fail("P013-A contains premature migration decision")

p8map = {m["path"]: m for m in p8.get("modules", []) if m.get("path")}
a2map = {c["path"]: c for c in a2.get("components", []) if c.get("path")}

basename_index = defaultdict(list)
stem_index = defaultdict(list)
for c in a["components"]:
    path = c["path"]
    q = Path(path)
    basename_index[q.name].append(path)
    stem_index[q.stem.lower()].append(path)

registry_text = "\n".join(p.read_text(errors="replace") for p in REGISTRIES)

records = []
for c in a["components"]:
    path = c["path"]
    m8 = p8map.get(path, {})
    m12 = a2map.get(path, {})
    q = Path(path)
    evidence = {
        "git_tracked_source": True,
        "source_sha256": c["sha256"],
        "parse_status": c["parse_status"],
        "p008_architectural_evidence": bool(m8),
        "p012_segmentation_evidence": bool(m12),
        "dependency_registry_text_reference": (q.stem in registry_text or q.name in registry_text),
        "imports": m8.get("imports", []),
        "calls": m8.get("calls", []),
        "interfaces": m8.get("interfaces", []),
        "declared_dependencies": m8.get("declared_dependencies", []),
        "families": m12.get("families", c.get("p012_families", [])),
        "family_scores": m12.get("family_scores", {}),
        "evidence_surfaces": m12.get("evidence_surfaces", c.get("p012_evidence_surfaces", [])),
    }

    same_basename = [x for x in basename_index[q.name] if x != path]
    same_stem = [x for x in stem_index[q.stem.lower()] if x != path]
    overlap = {
        "same_basename_candidates": same_basename,
        "same_stem_candidates": same_stem,
        "overlap_signal": bool(same_basename or same_stem),
        "note": "SIGNAL_ONLY_NOT_MERGE_EVIDENCE" if (same_basename or same_stem) else "NONE_OBSERVED_BY_THIS_HEURISTIC",
    }

    evidence_dimensions = [
        True,
        c["parse_status"] == "OK",
        bool(m8),
        bool(m12),
        bool(evidence["imports"] or evidence["declared_dependencies"] or evidence["dependency_registry_text_reference"]),
        bool(evidence["families"]),
        bool(evidence["evidence_surfaces"]),
    ]
    score = sum(evidence_dimensions)

    conflicts = []
    if not m8: conflicts.append("P008_ARCHITECTURAL_EVIDENCE_ABSENT")
    if not m12: conflicts.append("P012_SEGMENTATION_EVIDENCE_ABSENT")
    if overlap["overlap_signal"]: conflicts.append("POTENTIAL_NAME_OVERLAP_REQUIRES_SEMANTIC_REVIEW")

    if c["parse_status"] != "OK":
        readiness = "CONFLICTING_EVIDENCE"
    elif score >= 6 and not overlap["overlap_signal"]:
        readiness = "READY_FOR_DECISION"
    elif score >= 4:
        readiness = "PARTIAL_EVIDENCE"
    else:
        readiness = "INSUFFICIENT_EVIDENCE"

    records.append({
        "path": path,
        "sha256": c["sha256"],
        "evidence": evidence,
        "overlap_redundancy_indicators": overlap,
        "evidence_dimension_score": score,
        "evidence_conflicts_or_gaps": conflicts,
        "decision_readiness": readiness,
        "migration_decision": "UNKNOWN",
        "candidate_v2_target": "UNKNOWN",
        "migration_risk": "UNKNOWN",
        "decision_justification": "UNKNOWN",
        "epistemic_note": "P013-B enriches evidence only; P013-C owns governed migration decisions.",
    })

counts = Counter(r["decision_readiness"] for r in records)
payload = {
    "schema": "oce.p013.evidence_enriched_migration_assessment.v1",
    "milestone": "P013-B",
    "status": "EVIDENCE_ENRICHED_MIGRATION_ASSESSMENT_COMPLETE",
    "component_count": len(records),
    "coverage": f"{len(records)}/{a['component_count']}",
    "decision_readiness_counts": dict(sorted(counts.items())),
    "migration_decision_counts": {"UNKNOWN": len(records)},
    "rules": [
        "Filename alone never determines a migration decision.",
        "Overlap indicators are signals only and never constitute MERGE evidence.",
        "P008 absence is an evidence gap, never deprecation evidence.",
        "P012 product relevance never implies KEEP.",
        "Registry textual reference is an evidence signal, not a dependency proof.",
        "All migration decisions remain UNKNOWN in P013-B.",
        "P013-C must preserve UNKNOWN when evidence is insufficient or contradictory.",
    ],
    "records": records,
    "bindings": {
        "p013_a_identity_sha256": a["population_contract_identity_sha256"],
        "p013_a_report_sha256": sha(A),
        "p008_report_sha256": sha(P008),
        "p012_a2_identity_sha256": a2["segmentation_identity_sha256"],
        "p012_a2_report_sha256": sha(P012A2),
        "p012_e_final_lock_identity_sha256": e["final_lock_identity_sha256"],
        "p012_e_report_sha256": sha(P012E),
        "dependency_registry_sha256": {str(p.relative_to(ROOT)): sha(p) for p in REGISTRIES},
    },
    "ontology_inventory_sha256": inv_before,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
}
raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
payload["assessment_identity_sha256"] = hashlib.sha256(raw).hexdigest()

if sha(INV) != inv_before: fail("ontology inventory mutated")
OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
rt = load(OUT)
rid = rt.pop("assessment_identity_sha256")
if hashlib.sha256(json.dumps(rt, sort_keys=True, separators=(",", ":")).encode()).hexdigest() != rid:
    fail("round-trip identity failure")
if sha(INV) != inv_before: fail("ontology inventory mutated after report write")

print("P013_B_EVIDENCE_ENRICHED_ASSESSMENT_OK")
print(f"components={len(records)}")
print(f"coverage={len(records)}/{a['component_count']}")
for k in ["READY_FOR_DECISION","PARTIAL_EVIDENCE","INSUFFICIENT_EVIDENCE","CONFLICTING_EVIDENCE"]:
    print(f"{k}={counts.get(k,0)}")
print(f"migration_decision_UNKNOWN={len(records)}/{len(records)}")
print("p013_a_binding=VERIFIED")
print("p012_e_lock=VERIFIED")
print("ontology_inventory_non_mutation=OK")
print("assessment_identity_sha256=" + rid)
print("report=" + str(OUT))
