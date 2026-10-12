#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
INV = ROOT / "ontology_inventory.txt"
A = ROOT / "p013_a_canonical_population_contract_report.json"
B = ROOT / "p013_b_evidence_enriched_migration_assessment_report.json"
C = ROOT / "p013_c_governed_v1_v2_mapping_matrix_report.json"
D = ROOT / "p013_d_adversarial_completeness_crown_report.json"
OUT = ROOT / "p013_e_final_lock_report.json"

EXPECTED_A = "c81a2b24140cbe31f3d0fb9f64b320a35c6d689b3e4ac01b0a67bed391ad4d3b"
EXPECTED_B = "6aeb78ff49105ee8568f9065c7b48a98b4af92afca3a1a415463e0f502414105"
EXPECTED_C = "4bdc45a13ee781c0de53176b65689646011e29d174f10e890d40432d2490e0eb"
EXPECTED_D = "2f22832c132996d137db7c9da2f6a14b19699106f98fa6c52cef174c6afc645f"
ALLOWED = {"KEEP","ADAPT","WRAP","MERGE","REPLACE","DEPRECATE","UNKNOWN"}
TRANSFORMATIVE = {"ADAPT","WRAP","MERGE","REPLACE","DEPRECATE"}

def fail(msg): raise SystemExit("P013_E_REFUSED: " + msg)
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def content_identity(doc,key):
    x=copy.deepcopy(doc); x.pop(key,None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

for p in (INV,A,B,C,D):
    if not p.is_file(): fail("missing prerequisite: " + str(p))
inv0=sha(INV)
a,b,c,d=map(load,(A,B,C,D))

if a.get("population_contract_identity_sha256") != EXPECTED_A: fail("P013-A identity drift")
if b.get("assessment_identity_sha256") != EXPECTED_B: fail("P013-B identity drift")
if c.get("mapping_matrix_identity_sha256") != EXPECTED_C: fail("P013-C identity drift")
if d.get("crown_identity_sha256") != EXPECTED_D: fail("P013-D identity drift")
if content_identity(c,"mapping_matrix_identity_sha256") != EXPECTED_C: fail("P013-C content drift")
if content_identity(d,"crown_identity_sha256") != EXPECTED_D: fail("P013-D content drift")

if a.get("component_count") != 2095: fail("P013-A population drift")
if b.get("component_count") != 2095 or b.get("coverage") != "2095/2095": fail("P013-B coverage drift")
if c.get("component_count") != 2095 or c.get("coverage") != "2095/2095": fail("P013-C coverage drift")
if d.get("canonical_population") != 2095: fail("P013-D population drift")
if d.get("status") != "PASSED" or d.get("checks_total") != 25 or d.get("checks_passed") != 25 or d.get("checks_failed") != 0:
    fail("P013-D crown not 25/25")

rows=c.get("rows",[])
if len(rows)!=2095 or len({r.get("path") for r in rows})!=2095: fail("P013-C row population/uniqueness drift")
counts={k:0 for k in ALLOWED}
for r in rows:
    dec=r.get("migration_decision")
    if dec not in ALLOWED: fail("invalid decision vocabulary")
    counts[dec]+=1
if counts["KEEP"] != 973 or counts["UNKNOWN"] != 1122: fail("KEEP/UNKNOWN boundary drift")
if any(counts[k] != 0 for k in TRANSFORMATIVE): fail("transformative decision appeared")

policy=c.get("policy",{})
if policy.get("p014_not_implemented") is not True: fail("P014 boundary drift")
if policy.get("unknown_preserved") is not True: fail("UNKNOWN preservation drift")
if policy.get("transformative_decisions_require_explicit_target_level_evidence") is not True:
    fail("transformative-decision governance drift")

for doc,name in ((c,"P013-C"),):
    expected={
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True,
      "consciousness_proven":False,
      "subjectivity_proven":False,
      "qualia_proven":False,
      "phenomenology_proven":False,
    }
    for k,v in expected.items():
        if doc.get(k)!=v: fail(f"{name} epistemic invariant drift: {k}")

con=d.get("conclusions",{})
for k in (
 "completeness_boundary_preserved",
 "unknown_preservation_adversarially_tested",
 "transformative_decision_guard_tested",
 "nominal_overlap_merge_guard_tested",
 "p014_boundary_tested",
 "functional_only",
 "phenomenology_undetermined",
):
    if con.get(k) is not True: fail("P013-D conclusion drift: "+k)

if sha(INV)!=inv0: fail("ontology inventory mutated before lock")

report={
 "schema":"oce.p013.final_lock.v1",
 "milestone":"P013-E",
 "status":"LOCKED",
 "p013_status":"CLOSED_LOCKED",
 "canonical_population":2095,
 "coverage":"2095/2095",
 "decision_counts":{k:counts[k] for k in sorted(ALLOWED)},
 "keep":973,
 "unknown":1122,
 "transformative_decisions":0,
 "adversarial_crown":"25/25",
 "bindings":{
   "p013_a_identity_sha256":EXPECTED_A,
   "p013_a_report_sha256":sha(A),
   "p013_b_identity_sha256":EXPECTED_B,
   "p013_b_report_sha256":sha(B),
   "p013_c_identity_sha256":EXPECTED_C,
   "p013_c_report_sha256":sha(C),
   "p013_d_identity_sha256":EXPECTED_D,
   "p013_d_report_sha256":sha(D),
   "ontology_inventory_sha256":inv0,
 },
 "locked_claims":{
   "canonical_population_complete":True,
   "mapping_matrix_complete":True,
   "keep_boundary":973,
   "unknown_boundary":1122,
   "unknown_is_valid_epistemic_result":True,
   "transformative_decisions_without_target_evidence":0,
   "adversarial_crown_passed":True,
   "p014_not_started_by_p013":True,
 },
 "epistemic_status":{
   "functional_conclusion_only":True,
   "phenomenology_undetermined":True,
   "consciousness_proven":False,
   "subjectivity_proven":False,
   "qualia_proven":False,
   "phenomenology_proven":False,
 },
 "closure_scope":{
   "closes":"P013 V1_to_V2_mapping_matrix only",
   "does_not_close":"P014 Legacy Capability Adapter or later milestones",
   "keep_semantics":"governed migration-matrix KEEP; not proof of runtime V2 compatibility",
   "unknown_semantics":"insufficient target-level evidence for a stronger governed migration decision"
 }
}
report["final_lock_identity_sha256"]=hashlib.sha256(
    json.dumps(report,sort_keys=True,separators=(",",":")).encode()
).hexdigest()

if sha(INV)!=inv0: fail("ontology inventory mutated during lock")
OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
rt=load(OUT); rid=rt.pop("final_lock_identity_sha256")
if hashlib.sha256(json.dumps(rt,sort_keys=True,separators=(",",":")).encode()).hexdigest()!=rid:
    fail("round-trip final-lock identity failure")
if sha(INV)!=inv0: fail("ontology inventory mutated after lock")

print("P013_E_FINAL_LOCK_OK")
print("status=LOCKED")
print("p013_status=CLOSED_LOCKED")
print("components=2095")
print("coverage=2095/2095")
print("KEEP=973")
print("UNKNOWN=1122")
print("transformative_decisions=0")
print("p013_d_crown=25/25")
print("p013_a_binding=VERIFIED")
print("p013_b_binding=VERIFIED")
print("p013_c_binding=VERIFIED")
print("p013_d_binding=VERIFIED")
print("ontology_inventory_non_mutation=OK")
print("p014_not_started=VERIFIED")
print("final_lock_identity_sha256="+rid)
print("report="+str(OUT))
