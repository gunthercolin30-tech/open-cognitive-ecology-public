#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
INV = ROOT / "ontology_inventory.txt"
B = ROOT / "p013_b_evidence_enriched_migration_assessment_report.json"
C = ROOT / "p013_c_governed_v1_v2_mapping_matrix_report.json"
OUT = ROOT / "p013_d_adversarial_completeness_crown_report.json"

EXPECTED_B = "6aeb78ff49105ee8568f9065c7b48a98b4af92afca3a1a415463e0f502414105"
EXPECTED_C = "4bdc45a13ee781c0de53176b65689646011e29d174f10e890d40432d2490e0eb"
ALLOWED = {"KEEP","ADAPT","WRAP","MERGE","REPLACE","DEPRECATE","UNKNOWN"}
TRANSFORMATIVE = {"ADAPT","WRAP","MERGE","REPLACE","DEPRECATE"}

def fail(msg): raise SystemExit("P013_D_REFUSED: " + msg)
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def identity_without(d, key):
    x=copy.deepcopy(d); x.pop(key,None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

for p in (INV,B,C):
    if not p.is_file(): fail("missing prerequisite: " + str(p))
inv0=sha(INV); b=load(B); c=load(C)

if b.get("assessment_identity_sha256") != EXPECTED_B: fail("P013-B identity drift")
if c.get("mapping_matrix_identity_sha256") != EXPECTED_C: fail("P013-C identity drift")
if identity_without(c,"mapping_matrix_identity_sha256") != EXPECTED_C: fail("P013-C content/identity mismatch")

def validate(doc):
    errors=[]
    rows=doc.get("rows")
    if not isinstance(rows,list): return ["rows_not_list"]
    if doc.get("component_count") != 2095: errors.append("component_count")
    if doc.get("coverage") != "2095/2095": errors.append("coverage")
    paths=[r.get("path") for r in rows]
    if len(rows)!=2095: errors.append("row_count")
    if len(set(paths))!=2095: errors.append("path_uniqueness")
    if any(not isinstance(p,str) or not p for p in paths): errors.append("path_validity")

    calc={k:0 for k in ALLOWED}
    for r in rows:
        d=r.get("migration_decision")
        if d not in ALLOWED:
            errors.append("decision_vocabulary"); continue
        calc[d]+=1
        if not r.get("source_sha256"): errors.append("source_sha")
        if d!="UNKNOWN":
            if r.get("v2_target") in (None,"","UNKNOWN"): errors.append("target_required")
            if r.get("migration_risk") in (None,"","UNKNOWN"): errors.append("risk_required")
            if r.get("justification") in (None,"","UNKNOWN"): errors.append("justification_required")
        if d=="KEEP":
            prov=r.get("dependencies_and_provenance",{})
            if r.get("decision_readiness")!="READY_FOR_DECISION": errors.append("keep_not_ready")
            if r.get("overlap_signal") is not False: errors.append("keep_overlap")
            if not prov.get("p008_architectural_evidence"): errors.append("keep_without_p008")
            if not prov.get("p012_segmentation_evidence"): errors.append("keep_without_p012")
        if d=="MERGE" and r.get("overlap_signal") is True:
            errors.append("merge_from_overlap_without_explicit_target_evidence")
        if d in TRANSFORMATIVE:
            errors.append("transformative_decision_not_authorized_by_c_policy")

    stated=doc.get("decision_counts",{})
    for k in ALLOWED:
        if stated.get(k,0)!=calc[k]: errors.append("decision_count_mismatch")
    if calc["KEEP"]!=973: errors.append("keep_boundary")
    if calc["UNKNOWN"]!=1122: errors.append("unknown_boundary")
    if any(calc[k] for k in TRANSFORMATIVE): errors.append("transformative_boundary")
    pol=doc.get("policy",{})
    required_policy={
      "conservative":True,
      "transformative_decisions_require_explicit_target_level_evidence":True,
      "filename_alone_never_determines_decision":True,
      "overlap_signal_never_implies_merge":True,
      "p008_absence_never_implies_deprecate":True,
      "product_relevance_never_implies_keep":True,
      "unknown_preserved":True,
      "p014_not_implemented":True,
    }
    for k,v in required_policy.items():
        if pol.get(k)!=v: errors.append("policy_"+k)
    for k,v in {
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True,
      "consciousness_proven":False,
      "subjectivity_proven":False,
      "qualia_proven":False,
      "phenomenology_proven":False,
    }.items():
        if doc.get(k)!=v: errors.append("invariant_"+k)
    binds=doc.get("bindings",{})
    if binds.get("p013_b_identity_sha256")!=EXPECTED_B: errors.append("b_binding")
    if doc.get("mapping_matrix_identity_sha256")!=EXPECTED_C: errors.append("c_identity")
    if identity_without(doc,"mapping_matrix_identity_sha256")!=doc.get("mapping_matrix_identity_sha256"):
        errors.append("content_identity")
    return sorted(set(errors))

baseline_errors=validate(c)
if baseline_errors: fail("canonical C fails crown precheck: "+",".join(baseline_errors))

tests=[]
def check(name, mutated, expected_error):
    errs=validate(mutated)
    passed=expected_error in errs
    tests.append({"name":name,"passed":passed,"expected_rejection":expected_error,"observed_errors":errs})
    if not passed: fail("mutation escaped: "+name)

def mut():
    return copy.deepcopy(c)

x=mut(); x["rows"].pop(); check("delete_component",x,"row_count")
x=mut(); x["rows"].append(copy.deepcopy(x["rows"][0])); check("duplicate_component",x,"row_count")
x=mut(); x["rows"][0]["migration_decision"]="INVALID"; check("invalid_decision_vocabulary",x,"decision_vocabulary")
keep_i=next(i for i,r in enumerate(c["rows"]) if r["migration_decision"]=="KEEP")
unk_i=next(i for i,r in enumerate(c["rows"]) if r["migration_decision"]=="UNKNOWN")
over_i=next(i for i,r in enumerate(c["rows"]) if r.get("overlap_signal") is True)

x=mut(); x["rows"][keep_i]["decision_readiness"]="PARTIAL_EVIDENCE"; check("false_keep_not_ready",x,"keep_not_ready")
x=mut(); x["rows"][keep_i]["overlap_signal"]=True; check("false_keep_with_overlap",x,"keep_overlap")
x=mut(); x["rows"][keep_i]["dependencies_and_provenance"]["p008_architectural_evidence"]=False; check("false_keep_without_p008",x,"keep_without_p008")
x=mut(); x["rows"][keep_i]["dependencies_and_provenance"]["p012_segmentation_evidence"]=False; check("false_keep_without_p012",x,"keep_without_p012")
x=mut(); x["rows"][keep_i]["v2_target"]="UNKNOWN"; check("keep_missing_target",x,"target_required")
x=mut(); x["rows"][keep_i]["migration_risk"]="UNKNOWN"; check("keep_missing_risk",x,"risk_required")
x=mut(); x["rows"][keep_i]["justification"]="UNKNOWN"; check("keep_missing_justification",x,"justification_required")

for d in ["ADAPT","WRAP","REPLACE","DEPRECATE"]:
    x=mut(); r=x["rows"][unk_i]; r["migration_decision"]=d; r["v2_target"]="V2_FAKE"; r["migration_risk"]="LOW"; r["justification"]="FAKE"
    check("unauthorized_"+d.lower(),x,"transformative_decision_not_authorized_by_c_policy")
x=mut(); r=x["rows"][over_i]; r["migration_decision"]="MERGE"; r["v2_target"]="V2_FAKE"; r["migration_risk"]="LOW"; r["justification"]="name overlap"
check("merge_from_nominal_overlap",x,"merge_from_overlap_without_explicit_target_evidence")

x=mut(); x["rows"][unk_i]["migration_decision"]="KEEP"; check("arbitrary_unknown_to_keep",x,"keep_not_ready")
x=mut(); x["rows"][0]["source_sha256"]="0"*64; check("source_sha_tamper",x,"content_identity")
x=mut(); x["bindings"]["p013_b_identity_sha256"]="0"*64; check("break_b_binding",x,"b_binding")
x=mut(); x["mapping_matrix_identity_sha256"]="0"*64; check("break_c_identity",x,"c_identity")
x=mut(); x["decision_counts"]["KEEP"]=972; check("falsify_decision_counts",x,"decision_count_mismatch")
x=mut(); x["policy"]["overlap_signal_never_implies_merge"]=False; check("weaken_overlap_policy",x,"policy_overlap_signal_never_implies_merge")
x=mut(); x["policy"]["p014_not_implemented"]=False; check("premature_p014",x,"policy_p014_not_implemented")
x=mut(); x["functional_conclusion_only"]=False; check("functional_only_violation",x,"invariant_functional_conclusion_only")
x=mut(); x["consciousness_proven"]=True; check("consciousness_overclaim",x,"invariant_consciousness_proven")
x=mut(); x["phenomenology_undetermined"]=False; check("phenomenology_overclaim",x,"invariant_phenomenology_undetermined")

passed=sum(t["passed"] for t in tests)
report={
 "schema":"oce.p013.adversarial_completeness_crown.v1",
 "milestone":"P013-D",
 "status":"PASSED",
 "canonical_population":2095,
 "canonical_keep":973,
 "canonical_unknown":1122,
 "canonical_transformative_decisions":0,
 "checks_total":len(tests),
 "checks_passed":passed,
 "checks_failed":len(tests)-passed,
 "tests":tests,
 "bindings":{
   "p013_b_identity_sha256":EXPECTED_B,
   "p013_b_report_sha256":sha(B),
   "p013_c_identity_sha256":EXPECTED_C,
   "p013_c_report_sha256":sha(C),
   "ontology_inventory_sha256":inv0
 },
 "conclusions":{
   "completeness_boundary_preserved":True,
   "unknown_preservation_adversarially_tested":True,
   "transformative_decision_guard_tested":True,
   "nominal_overlap_merge_guard_tested":True,
   "p014_boundary_tested":True,
   "functional_only":True,
   "phenomenology_undetermined":True
 }
}
report["crown_identity_sha256"]=hashlib.sha256(
 json.dumps(report,sort_keys=True,separators=(",",":")).encode()
).hexdigest()
if sha(INV)!=inv0: fail("ontology inventory mutated")
OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
rt=load(OUT); rid=rt.pop("crown_identity_sha256")
if hashlib.sha256(json.dumps(rt,sort_keys=True,separators=(",",":")).encode()).hexdigest()!=rid:
    fail("round-trip identity failure")
if sha(INV)!=inv0: fail("ontology inventory mutated after crown")

print("P013_D_ADVERSARIAL_COMPLETENESS_CROWN_OK")
print(f"checks={passed}/{len(tests)}")
print("components=2095")
print("KEEP=973")
print("UNKNOWN=1122")
print("transformative_decisions=0")
print("unknown_preservation=TESTED")
print("nominal_overlap_merge_guard=TESTED")
print("p014_boundary=TESTED")
print("p013_b_binding=VERIFIED")
print("p013_c_binding=VERIFIED")
print("ontology_inventory_non_mutation=OK")
print("crown_identity_sha256="+rid)
print("report="+str(OUT))
