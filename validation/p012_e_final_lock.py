#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
INV = ROOT / "ontology_inventory.txt"
OUT = ROOT / "p012_e_final_lock_report.json"

SOURCES = {
    "a2": ROOT / "validation/p012_a2_component_segmentation.py",
    "b": ROOT / "validation/p012_b_product_relevance_mapping.py",
    "c": ROOT / "validation/p012_c_evidence_gap_analysis.py",
    "d": ROOT / "validation/p012_d_adversarial_crown.py",
}
REPORTS = {
    "a2": ROOT / "p012_a2_component_segmentation_report.json",
    "b": ROOT / "p012_b_product_relevance_mapping_report.json",
    "c": ROOT / "p012_c_evidence_gap_analysis_report.json",
    "d": ROOT / "p012_d_adversarial_crown_report.json",
}

EXPECTED_SOURCE_SHA = {
    "a2": "1a82d136e47b5e55413a4cf86291b1001de0124d3d9a8ce702fefcfc35726340",
    "b": "215cde0d635583c6057539c8134c0d2d29a19fb5115a6290ea3902df9224ef2a",
    "c": "4b3ab2b9425dbabc9545738bedcfb936330e3adf9a3660f8b47f4708369410ce",
    "d": "67a3f0594c840574f10dfc27ea45f2fa25469cbb2564acdfaa2ec0435f28515b",
}
EXPECTED_ID = {
    "a2": "6cf3daa5bc6fc13df143d3e8e6a563a30243eb68563ed3aeebd863889ae15204",
    "b": "8bd5a7ccab5ce05ef0bec6dd07ba6065cbe5c2cdaa47c75ac98c583b412d0660",
    "c": "8b364e7057720a7011872f36e85fb8e53d9349c69a414398e99e65e337af9d8e",
    "d": "980de44833d1fb03f52e6ae74186595156bc2914d40ec87fa9d4fea1332402f8",
}
ID_FIELD = {
    "a2": "segmentation_identity_sha256",
    "b": "mapping_identity_sha256",
    "c": "analysis_identity_sha256",
    "d": "crown_identity_sha256",
}
EXPECTED_STATUS = {
    "a2": "COMPONENT_SEGMENTATION_COMPLETE",
    "b": "PRODUCT_RELEVANCE_MAPPING_COMPLETE",
    "c": "EVIDENCE_GAP_ANALYSIS_COMPLETE",
    "d": "ADVERSARIAL_CROWN_PASSED",
}

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def fail(msg: str):
    raise SystemExit("P012_E_REFUSED: " + msg)

if not INV.is_file():
    fail("ontology_inventory.txt missing")
for p in list(SOURCES.values()) + list(REPORTS.values()):
    if not p.is_file():
        fail("required artifact missing: " + str(p))

inv_before = sha(INV)
data = {k: json.loads(v.read_text()) for k, v in REPORTS.items()}

for k, p in SOURCES.items():
    if sha(p) != EXPECTED_SOURCE_SHA[k]:
        fail(k.upper() + " source hash drift")
    if data[k].get(ID_FIELD[k]) != EXPECTED_ID[k]:
        fail(k.upper() + " report identity drift")
    if data[k].get("status") != EXPECTED_STATUS[k]:
        fail(k.upper() + " status drift")

a2, b, c, d = data["a2"], data["b"], data["c"], data["d"]

if a2.get("product_surface_candidate_count") != 1300:
    fail("A2 candidate population drift")
if b.get("candidate_count") != 1300 or b.get("mapped_candidate_count") != 1300 or b.get("unmapped_candidate_count") != 0:
    fail("B candidate coverage drift")
if b.get("aggregate_count") != 12:
    fail("B aggregate population drift")
if c.get("summary", {}).get("aggregate_count") != 12 or c.get("summary", {}).get("covered_candidate_count") != 1300:
    fail("C coverage drift")
if d.get("checks_passed") != 173:
    fail("D adversarial check count drift")
if d.get("candidate_coverage") != "1300/1300" or d.get("aggregate_coverage") != "12/12":
    fail("D coverage drift")

if b.get("a2_segmentation_identity_sha256") != EXPECTED_ID["a2"]:
    fail("B->A2 binding drift")
if c.get("a2_segmentation_identity_sha256") != EXPECTED_ID["a2"]:
    fail("C->A2 binding drift")
if c.get("b_mapping_identity_sha256") != EXPECTED_ID["b"]:
    fail("C->B binding drift")
if d.get("a2_identity_sha256") != EXPECTED_ID["a2"]:
    fail("D->A2 binding drift")
if d.get("b_identity_sha256") != EXPECTED_ID["b"]:
    fail("D->B binding drift")
if d.get("c_identity_sha256") != EXPECTED_ID["c"]:
    fail("D->C binding drift")

for k, x in data.items():
    required = {
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "consciousness_proven": False,
        "subjectivity_proven": False,
        "qualia_proven": False,
        "phenomenology_proven": False,
    }
    for field, expected in required.items():
        if x.get(field) is not expected:
            fail(f"{k.upper()} invariant drift: {field}")

for agg in b.get("aggregates", []):
    if agg.get("market_demand_evidence") != "UNKNOWN":
        fail("B market-demand overclaim")
    if agg.get("willingness_to_pay_evidence") != "UNKNOWN":
        fail("B WTP overclaim")
    if agg.get("product_market_fit") != "UNKNOWN":
        fail("B PMF overclaim")

for agg in c.get("aggregates", []):
    ce = agg.get("commercial_evidence", {})
    for field in (
        "user_evidence", "customer_outcome_evidence", "market_demand_evidence",
        "willingness_to_pay_evidence", "productization_effort_evidence",
        "product_market_fit"
    ):
        if ce.get(field) != "UNKNOWN":
            fail("C commercial evidence overclaim: " + field)
    if agg.get("technical_evidence", {}).get("runtime_exercise") != "UNKNOWN":
        fail("C runtime evidence overclaim")

if d.get("technical_to_market_overclaim_rejected") is not True:
    fail("D technical-to-market protection drift")
if d.get("unknown_preservation") is not True:
    fail("D UNKNOWN preservation drift")
if d.get("market_demand_evidence") != "UNKNOWN":
    fail("D market demand drift")
if d.get("willingness_to_pay_evidence") != "UNKNOWN":
    fail("D WTP drift")
if d.get("product_market_fit") != "UNKNOWN":
    fail("D PMF drift")

artifact_hashes = {}
for k, p in SOURCES.items():
    artifact_hashes[f"{k}_source_sha256"] = sha(p)
for k, p in REPORTS.items():
    artifact_hashes[f"{k}_report_sha256"] = sha(p)

payload = {
    "schema": "oce.p012.final_lock.v1",
    "milestone": "P012-E",
    "status": "LOCKED",
    "locked_chain": ["P012-A2", "P012-B", "P012-C", "P012-D"],
    "locked_identities": EXPECTED_ID,
    "artifact_hashes": artifact_hashes,
    "ontology_inventory_sha256": inv_before,
    "candidate_coverage": "1300/1300",
    "aggregate_coverage": "12/12",
    "adversarial_checks": "173/173",
    "technical_to_market_overclaim_rejected": True,
    "unknown_preservation": True,
    "runtime_evidence_from_a2_b": "UNKNOWN",
    "market_demand_evidence": "UNKNOWN",
    "willingness_to_pay_evidence": "UNKNOWN",
    "product_market_fit": "UNKNOWN",
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
}
payload["final_lock_identity_sha256"] = hashlib.sha256(
    json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

if sha(INV) != inv_before:
    fail("ontology inventory mutated")

OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

# Determinism: reconstruct the identity-bearing payload after serialization.
roundtrip = json.loads(OUT.read_text())
reported = roundtrip.pop("final_lock_identity_sha256")
recomputed = hashlib.sha256(
    json.dumps(roundtrip, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
if reported != recomputed:
    fail("final lock identity non-deterministic")

if sha(INV) != inv_before:
    fail("ontology inventory mutated after report write")

print("P012_E_FINAL_LOCK_OK")
print("status=LOCKED")
print("a2_identity=LOCKED")
print("b_identity=LOCKED")
print("c_identity=LOCKED")
print("d_identity=LOCKED")
print("candidate_coverage=1300/1300")
print("aggregate_coverage=12/12")
print("adversarial_checks=173/173")
print("technical_to_market_overclaim_rejected=YES")
print("market_demand_evidence=UNKNOWN")
print("willingness_to_pay_evidence=UNKNOWN")
print("product_market_fit=UNKNOWN")
print("ontology_inventory_non_mutation=OK")
print("final_lock_identity_sha256=" + reported)
print("report=" + str(OUT))
