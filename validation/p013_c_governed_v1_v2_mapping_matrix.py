#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from collections import Counter
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
INV = ROOT / "ontology_inventory.txt"
A = ROOT / "p013_a_canonical_population_contract_report.json"
B = ROOT / "p013_b_evidence_enriched_migration_assessment_report.json"
E = ROOT / "p012_e_final_lock_report.json"
OUT = ROOT / "p013_c_governed_v1_v2_mapping_matrix_report.json"

EXPECTED_A = "c81a2b24140cbe31f3d0fb9f64b320a35c6d689b3e4ac01b0a67bed391ad4d3b"
EXPECTED_B = "6aeb78ff49105ee8568f9065c7b48a98b4af92afca3a1a415463e0f502414105"
EXPECTED_E = "c46a6eb9a5c485a96b5666b370f14ee880ab29066b498a673b5c70e4c1515d19"
ALLOWED = {"KEEP","ADAPT","WRAP","MERGE","REPLACE","DEPRECATE","UNKNOWN"}

def fail(msg): raise SystemExit("P013_C_REFUSED: " + msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())

for p in (INV,A,B,E):
    if not p.is_file(): fail("missing prerequisite: " + str(p))

inv0 = sha(INV)
a,b,e = load(A),load(B),load(E)

if a.get("population_contract_identity_sha256") != EXPECTED_A: fail("P013-A identity drift")
if b.get("assessment_identity_sha256") != EXPECTED_B: fail("P013-B identity drift")
if e.get("final_lock_identity_sha256") != EXPECTED_E or e.get("status") != "LOCKED": fail("P012-E lock drift")
if a.get("component_count") != 2095 or b.get("component_count") != 2095: fail("population drift")
if b.get("coverage") != "2095/2095": fail("P013-B coverage drift")

arec = {x["path"]:x for x in a["components"]}
brec = {x["path"]:x for x in b["records"]}
if set(arec) != set(brec): fail("A/B population mismatch")

rows=[]
for path in sorted(arec):
    aa,bb=arec[path],brec[path]
    ev=bb["evidence"]
    gaps=list(bb.get("evidence_conflicts_or_gaps",[]))
    readiness=bb["decision_readiness"]

    # P013-C is deliberately conservative. It may resolve only the least
    # destructive decision (KEEP) when direct architectural + segmentation
    # evidence is present and no overlap/gap signal requires migration design.
    # All transformative/destructive decisions remain UNKNOWN absent explicit
    # target-level comparative evidence.
    direct_arch = bool(ev.get("p008_architectural_evidence"))
    direct_seg = bool(ev.get("p012_segmentation_evidence"))
    overlap = bool(bb.get("overlap_redundancy_indicators",{}).get("overlap_signal"))
    parse_ok = ev.get("parse_status") == "OK"

    if readiness == "READY_FOR_DECISION" and direct_arch and direct_seg and parse_ok and not overlap:
        decision="KEEP"
        target="V2_DIRECT_REUSE_CANDIDATE:" + path
        risk="LOW_TO_MODERATE_UNTIL_V2_INTEGRATION_TEST"
        justification=(
            "Governed KEEP candidate: tracked parsable source with direct P008 architectural "
            "evidence and P012 segmentation evidence; P013-B reports READY_FOR_DECISION and "
            "no overlap signal. This is a migration-matrix decision, not proof of runtime V2 compatibility."
        )
    else:
        decision="UNKNOWN"
        target="UNKNOWN"
        risk="UNKNOWN"
        justification=(
            "Evidence does not justify a specific governed migration action without target-level "
            "comparative or integration evidence. UNKNOWN preserves non-closure."
        )

    if decision in {"MERGE","REPLACE","DEPRECATE","ADAPT","WRAP"}:
        fail("internal policy violation: transformative decision emitted without explicit target evidence")
    if decision not in ALLOWED: fail("invalid decision")
    if decision!="UNKNOWN" and (target=="UNKNOWN" or risk=="UNKNOWN" or justification=="UNKNOWN"):
        fail("incomplete non-UNKNOWN decision")

    rows.append({
        "path":path,
        "source_sha256":aa["sha256"],
        "decision_readiness":readiness,
        "migration_decision":decision,
        "v2_target":target,
        "migration_risk":risk,
        "justification":justification,
        "dependencies_and_provenance":{
            "p008_architectural_evidence":direct_arch,
            "p012_segmentation_evidence":direct_seg,
            "dependency_registry_text_reference":bool(ev.get("dependency_registry_text_reference")),
            "imports":ev.get("imports",[]),
            "declared_dependencies":ev.get("declared_dependencies",[]),
            "families":ev.get("families",[]),
            "evidence_surfaces":ev.get("evidence_surfaces",[]),
        },
        "overlap_signal":overlap,
        "evidence_gaps":gaps,
        "epistemic_limits":[
            "P013-C does not implement P014.",
            "KEEP does not prove runtime V2 compatibility.",
            "Product relevance does not prove customer or market relevance.",
            "UNKNOWN is retained where target-level evidence is insufficient."
        ]
    })

counts=Counter(x["migration_decision"] for x in rows)
if sum(counts.values()) != 2095: fail("decision coverage failure")
if any(x["migration_decision"] not in ALLOWED for x in rows): fail("decision vocabulary failure")

payload={
 "schema":"oce.p013.governed_v1_v2_mapping_matrix.v1",
 "milestone":"P013-C",
 "status":"GOVERNED_MAPPING_MATRIX_COMPLETE",
 "component_count":2095,
 "coverage":"2095/2095",
 "decision_counts":{k:counts.get(k,0) for k in sorted(ALLOWED)},
 "policy":{
   "conservative":True,
   "transformative_decisions_require_explicit_target_level_evidence":True,
   "filename_alone_never_determines_decision":True,
   "overlap_signal_never_implies_merge":True,
   "p008_absence_never_implies_deprecate":True,
   "product_relevance_never_implies_keep":True,
   "unknown_preserved":True,
   "p014_not_implemented":True
 },
 "rows":rows,
 "bindings":{
   "p013_a_identity_sha256":a["population_contract_identity_sha256"],
   "p013_a_report_sha256":sha(A),
   "p013_b_identity_sha256":b["assessment_identity_sha256"],
   "p013_b_report_sha256":sha(B),
   "p012_e_identity_sha256":e["final_lock_identity_sha256"],
   "p012_e_report_sha256":sha(E)
 },
 "ontology_inventory_sha256":inv0,
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
 "consciousness_proven":False,
 "subjectivity_proven":False,
 "qualia_proven":False,
 "phenomenology_proven":False
}
payload["mapping_matrix_identity_sha256"]=hashlib.sha256(
 json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
).hexdigest()

if sha(INV)!=inv0: fail("ontology inventory mutated")
OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
rt=load(OUT); rid=rt.pop("mapping_matrix_identity_sha256")
if hashlib.sha256(json.dumps(rt,sort_keys=True,separators=(",",":")).encode()).hexdigest()!=rid:
    fail("round-trip identity failure")
if sha(INV)!=inv0: fail("ontology inventory mutated after report")

print("P013_C_GOVERNED_MAPPING_MATRIX_OK")
print("components=2095")
print("coverage=2095/2095")
for k in ["KEEP","ADAPT","WRAP","MERGE","REPLACE","DEPRECATE","UNKNOWN"]:
    print(f"{k}={counts.get(k,0)}")
print("transformative_decisions_without_target_evidence=0")
print("p013_a_binding=VERIFIED")
print("p013_b_binding=VERIFIED")
print("p012_e_lock=VERIFIED")
print("ontology_inventory_non_mutation=OK")
print("mapping_matrix_identity_sha256="+rid)
print("report="+str(OUT))
