#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from collections import Counter
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
A2 = ROOT / "p012_a2_component_segmentation_report.json"
B = ROOT / "p012_b_product_relevance_mapping_report.json"
INV = ROOT / "ontology_inventory.txt"
OUT = ROOT / "p012_c_evidence_gap_analysis_report.json"

EXPECTED_A2_ID = "6cf3daa5bc6fc13df143d3e8e6a563a30243eb68563ed3aeebd863889ae15204"
EXPECTED_B_ID = "8bd5a7ccab5ce05ef0bec6dd07ba6065cbe5c2cdaa47c75ac98c583b412d0660"

TECH_EVIDENCE = {
    "EXECUTABLE_API_SURFACE": "EXECUTABLE",
    "VALIDATION_OR_TEST_SURFACE": "VALIDATION_TEST",
    "REPORT_OR_AUDIT_SURFACE": "REPORT_AUDIT",
    "USER_INTERFACE_SURFACE": "UI",
    "EXTERNAL_INTEGRATION_SURFACE": "EXTERNAL_INTEGRATION",
    "SOURCE_ONLY": "SOURCE_ONLY",
}

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def identity(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

if not A2.is_file() or not B.is_file() or not INV.is_file():
    raise SystemExit("P012_C_REFUSED: required A2/B/inventory missing")

inv_before = sha(INV)
a2 = json.loads(A2.read_text())
b = json.loads(B.read_text())

if a2.get("segmentation_identity_sha256") != EXPECTED_A2_ID:
    raise SystemExit("P012_C_REFUSED: A2 identity drift")
if b.get("mapping_identity_sha256") != EXPECTED_B_ID:
    raise SystemExit("P012_C_REFUSED: B identity drift")
if b.get("a2_segmentation_identity_sha256") != EXPECTED_A2_ID:
    raise SystemExit("P012_C_REFUSED: B not bound to expected A2")

components = {c["path"]: c for c in a2.get("components", [])}
candidates = set(a2.get("product_surface_candidates", []))
aggregates = b.get("aggregates", [])

if len(candidates) != 1300:
    raise SystemExit("P012_C_REFUSED: unexpected candidate population")
if len(aggregates) != 12:
    raise SystemExit("P012_C_REFUSED: unexpected aggregate population")
if b.get("mapped_candidate_count") != len(candidates) or b.get("unmapped_candidate_count") != 0:
    raise SystemExit("P012_C_REFUSED: B coverage inconsistent")

analyses = []
covered = set()

for agg in sorted(aggregates, key=lambda x: x["family"]):
    family = agg["family"]
    cand = sorted(set(agg.get("candidate_components", [])))
    covered.update(cand)

    counts = Counter()
    for path in cand:
        c = components.get(path)
        if c is None:
            raise SystemExit(f"P012_C_REFUSED: missing A2 component: {path}")
        for surface in c.get("evidence_surfaces", []):
            counts[TECH_EVIDENCE.get(surface, "OTHER_TECHNICAL")] += 1

    technical_evidence = {
        "source_or_structural": "OBSERVED" if agg.get("component_count", 0) > 0 else "NOT_OBSERVED",
        "executable": "OBSERVED" if counts["EXECUTABLE"] else "NOT_OBSERVED",
        "validation_test": "OBSERVED" if counts["VALIDATION_TEST"] else "NOT_OBSERVED",
        "report_audit": "OBSERVED" if counts["REPORT_AUDIT"] else "NOT_OBSERVED",
        "ui": "OBSERVED" if counts["UI"] else "NOT_OBSERVED",
        "external_integration": "OBSERVED" if counts["EXTERNAL_INTEGRATION"] else "NOT_OBSERVED",
        # A2/B are static/source-derived. They cannot establish runtime exercise.
        "runtime_exercise": "UNKNOWN",
    }

    commercial_evidence = {
        "user_evidence": "UNKNOWN",
        "customer_outcome_evidence": "UNKNOWN",
        "market_demand_evidence": "UNKNOWN",
        "willingness_to_pay_evidence": "UNKNOWN",
        "productization_effort_evidence": "UNKNOWN",
        "product_market_fit": "UNKNOWN",
    }

    gaps = [k for k, v in technical_evidence.items() if v in ("UNKNOWN", "NOT_OBSERVED")]
    gaps += list(commercial_evidence.keys())

    # Confidence concerns only the source-derived technical mapping, never market relevance.
    observed_technical = sum(v == "OBSERVED" for v in technical_evidence.values())
    technical_mapping_confidence = (
        "HIGH" if observed_technical >= 4 else
        "MEDIUM" if observed_technical >= 2 else
        "LOW"
    )

    analyses.append({
        "family": family,
        "component_count": agg.get("component_count", 0),
        "candidate_count": len(cand),
        "technical_evidence_counts": dict(sorted(counts.items())),
        "technical_evidence": technical_evidence,
        "commercial_evidence": commercial_evidence,
        "technical_mapping_confidence": technical_mapping_confidence,
        "product_relevance_status": "HYPOTHESIS_ONLY_NOT_MARKET_VALIDATED",
        "gaps": gaps,
    })

if covered != candidates:
    missing = sorted(candidates - covered)
    extra = sorted(covered - candidates)
    raise SystemExit(f"P012_C_REFUSED: coverage mismatch missing={len(missing)} extra={len(extra)}")

summary = {
    "aggregate_count": len(analyses),
    "candidate_count": len(candidates),
    "covered_candidate_count": len(covered),
    "aggregates_with_validation_test_evidence": sum(
        x["technical_evidence"]["validation_test"] == "OBSERVED" for x in analyses
    ),
    "aggregates_with_ui_evidence": sum(
        x["technical_evidence"]["ui"] == "OBSERVED" for x in analyses
    ),
    "aggregates_with_external_integration_evidence": sum(
        x["technical_evidence"]["external_integration"] == "OBSERVED" for x in analyses
    ),
    "aggregates_with_runtime_evidence_from_a2_b": 0,
    "aggregates_with_market_demand_evidence": 0,
    "aggregates_with_willingness_to_pay_evidence": 0,
    "aggregates_with_pmf_evidence": 0,
}

payload = {
    "schema": "oce.p012.evidence_gap_analysis.v1",
    "milestone": "P012-C",
    "status": "EVIDENCE_GAP_ANALYSIS_COMPLETE",
    "a2_segmentation_identity_sha256": EXPECTED_A2_ID,
    "b_mapping_identity_sha256": EXPECTED_B_ID,
    "ontology_inventory_sha256": inv_before,
    "summary": summary,
    "aggregates": analyses,
    "epistemic_rules": {
        "static_source_evidence_does_not_prove_runtime_exercise": True,
        "technical_evidence_does_not_prove_user_value": True,
        "ui_presence_does_not_prove_user_adoption": True,
        "external_integration_presence_does_not_prove_customer_outcome": True,
        "validation_tests_do_not_prove_market_demand": True,
        "unknowns_are_preserved": True,
    },
    "limits": [
        "P012-C analyzes evidence present in A2/B; it does not import market evidence from outside those reports.",
        "Runtime exercise remains UNKNOWN because A2/B are source-derived mappings.",
        "Potential users and customer outcomes in B remain hypotheses, not empirical observations.",
        "Productization effort, market demand, willingness to pay and product-market fit remain UNKNOWN absent dedicated evidence."
    ],
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
}
payload["analysis_identity_sha256"] = identity(payload)

if sha(INV) != inv_before:
    raise SystemExit("P012_C_REFUSED: ontology inventory mutated")

OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

print("P012_C_EVIDENCE_GAP_ANALYSIS_OK")
print(f"aggregates={summary['aggregate_count']}/12")
print(f"covered_candidates={summary['covered_candidate_count']}/{summary['candidate_count']}")
print(f"aggregates_with_validation_test_evidence={summary['aggregates_with_validation_test_evidence']}")
print(f"aggregates_with_ui_evidence={summary['aggregates_with_ui_evidence']}")
print(f"aggregates_with_external_integration_evidence={summary['aggregates_with_external_integration_evidence']}")
print("runtime_evidence_from_a2_b=UNKNOWN")
print("market_demand_evidence=UNKNOWN")
print("willingness_to_pay_evidence=UNKNOWN")
print("product_market_fit=UNKNOWN")
print("ontology_inventory_non_mutation=OK")
print("analysis_identity_sha256=" + payload["analysis_identity_sha256"])
print("report=" + str(OUT))
