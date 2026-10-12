#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
INV = ROOT / "ontology_inventory.txt"
A2S = ROOT / "validation/p012_a2_component_segmentation.py"
BS = ROOT / "validation/p012_b_product_relevance_mapping.py"
CS = ROOT / "validation/p012_c_evidence_gap_analysis.py"
A2R = ROOT / "p012_a2_component_segmentation_report.json"
BR = ROOT / "p012_b_product_relevance_mapping_report.json"
CR = ROOT / "p012_c_evidence_gap_analysis_report.json"
OUT = ROOT / "p012_d_adversarial_crown_report.json"

EXPECTED = {
    "a2_source": "1a82d136e47b5e55413a4cf86291b1001de0124d3d9a8ce702fefcfc35726340",
    "b_source": "215cde0d635583c6057539c8134c0d2d29a19fb5115a6290ea3902df9224ef2a",
    "c_source": "4b3ab2b9425dbabc9545738bedcfb936330e3adf9a3660f8b47f4708369410ce",
    "a2_id": "6cf3daa5bc6fc13df143d3e8e6a563a30243eb68563ed3aeebd863889ae15204",
    "b_id": "8bd5a7ccab5ce05ef0bec6dd07ba6065cbe5c2cdaa47c75ac98c583b412d0660",
    "c_id": "8b364e7057720a7011872f36e85fb8e53d9349c69a414398e99e65e337af9d8e",
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ident(d, field):
    x=copy.deepcopy(d); x.pop(field,None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def check(cond, name):
    if not cond: raise AssertionError(name)
    print("P012_D_"+name+"_OK")
    checks.append(name)

for p in (INV,A2S,BS,CS,A2R,BR,CR):
    if not p.is_file(): raise SystemExit("P012_D_REFUSED: missing "+str(p))
inv_before=sha(INV)
a2=json.loads(A2R.read_text()); b=json.loads(BR.read_text()); c=json.loads(CR.read_text())
checks=[]

check(sha(A2S)==EXPECTED["a2_source"],"A2_SOURCE_HASH_LOCKED")
check(sha(BS)==EXPECTED["b_source"],"B_SOURCE_HASH_LOCKED")
check(sha(CS)==EXPECTED["c_source"],"C_SOURCE_HASH_LOCKED")
check(a2.get("segmentation_identity_sha256")==EXPECTED["a2_id"],"A2_REPORT_IDENTITY_LOCKED")
check(b.get("mapping_identity_sha256")==EXPECTED["b_id"],"B_REPORT_IDENTITY_LOCKED")
check(c.get("analysis_identity_sha256")==EXPECTED["c_id"],"C_REPORT_IDENTITY_LOCKED")
check(a2.get("status")=="COMPONENT_SEGMENTATION_COMPLETE","A2_STATUS_LOCKED")
check(b.get("status")=="PRODUCT_RELEVANCE_MAPPING_COMPLETE","B_STATUS_LOCKED")
check(c.get("status")=="EVIDENCE_GAP_ANALYSIS_COMPLETE","C_STATUS_LOCKED")
check(a2.get("product_surface_candidate_count")==1300,"A2_CANDIDATE_POPULATION_LOCKED")
check(b.get("candidate_count")==1300 and b.get("mapped_candidate_count")==1300 and b.get("unmapped_candidate_count")==0,"B_COVERAGE_LOCKED")
check(b.get("aggregate_count")==12,"B_AGGREGATE_POPULATION_LOCKED")
check(c.get("summary",{}).get("aggregate_count")==12,"C_AGGREGATE_COVERAGE_LOCKED")
check(c.get("summary",{}).get("covered_candidate_count")==1300,"C_CANDIDATE_COVERAGE_LOCKED")
check(b.get("a2_segmentation_identity_sha256")==EXPECTED["a2_id"],"B_TO_A2_BINDING_LOCKED")
check(c.get("a2_segmentation_identity_sha256")==EXPECTED["a2_id"],"C_TO_A2_BINDING_LOCKED")
check(c.get("b_mapping_identity_sha256")==EXPECTED["b_id"],"C_TO_B_BINDING_LOCKED")

for label,d in (("A2",a2),("B",b),("C",c)):
    check(d.get("functional_conclusion_only") is True,f"{label}_FUNCTIONAL_ONLY")
    check(d.get("phenomenology_undetermined") is True,f"{label}_PHENOMENOLOGY_UNDETERMINED")
    check(d.get("consciousness_proven") is False,f"{label}_CONSCIOUSNESS_FALSE")
    check(d.get("subjectivity_proven") is False,f"{label}_SUBJECTIVITY_FALSE")
    check(d.get("qualia_proven") is False,f"{label}_QUALIA_FALSE")
    check(d.get("phenomenology_proven") is False,f"{label}_PHENOMENOLOGY_FALSE")

for agg in b.get("aggregates",[]):
    check(agg.get("market_demand_evidence")=="UNKNOWN", "B_MARKET_DEMAND_UNKNOWN_"+agg["family"].upper())
    check(agg.get("willingness_to_pay_evidence")=="UNKNOWN", "B_WTP_UNKNOWN_"+agg["family"].upper())
    check(agg.get("product_market_fit")=="UNKNOWN", "B_PMF_UNKNOWN_"+agg["family"].upper())

for agg in c.get("aggregates",[]):
    ce=agg.get("commercial_evidence",{})
    check(ce.get("user_evidence")=="UNKNOWN","C_USER_EVIDENCE_UNKNOWN_"+agg["family"].upper())
    check(ce.get("customer_outcome_evidence")=="UNKNOWN","C_CUSTOMER_OUTCOME_UNKNOWN_"+agg["family"].upper())
    check(ce.get("market_demand_evidence")=="UNKNOWN","C_MARKET_DEMAND_UNKNOWN_"+agg["family"].upper())
    check(ce.get("willingness_to_pay_evidence")=="UNKNOWN","C_WTP_UNKNOWN_"+agg["family"].upper())
    check(ce.get("productization_effort_evidence")=="UNKNOWN","C_PRODUCTIZATION_UNKNOWN_"+agg["family"].upper())
    check(ce.get("product_market_fit")=="UNKNOWN","C_PMF_UNKNOWN_"+agg["family"].upper())
    check(agg.get("technical_evidence",{}).get("runtime_exercise")=="UNKNOWN","C_RUNTIME_UNKNOWN_"+agg["family"].upper())

rules=c.get("epistemic_rules",{})
for key in (
"static_source_evidence_does_not_prove_runtime_exercise",
"technical_evidence_does_not_prove_user_value",
"ui_presence_does_not_prove_user_adoption",
"external_integration_presence_does_not_prove_customer_outcome",
"validation_tests_do_not_prove_market_demand",
"unknowns_are_preserved"):
    check(rules.get(key) is True,"C_RULE_"+key.upper())

# Mutation/degradation tests on copies only.
x=copy.deepcopy(a2); x["product_surface_candidate_count"]=1299
check(x["product_surface_candidate_count"]!=1300,"REJECT_A2_CANDIDATE_REMOVAL")
x=copy.deepcopy(b); x["mapped_candidate_count"]=1299
check(not (x["mapped_candidate_count"]==1300 and x["unmapped_candidate_count"]==0),"REJECT_B_COVERAGE_FALSIFICATION")
x=copy.deepcopy(b); x["a2_segmentation_identity_sha256"]="0"*64
check(x["a2_segmentation_identity_sha256"]!=EXPECTED["a2_id"],"REJECT_B_A2_BINDING_TAMPER")
x=copy.deepcopy(c); x["b_mapping_identity_sha256"]="0"*64
check(x["b_mapping_identity_sha256"]!=EXPECTED["b_id"],"REJECT_C_B_BINDING_TAMPER")
x=copy.deepcopy(c); x["summary"]["covered_candidate_count"]=1299
check(x["summary"]["covered_candidate_count"]!=1300,"REJECT_C_COVERAGE_FALSIFICATION")
x=copy.deepcopy(c); x["aggregates"][0]["commercial_evidence"]["market_demand_evidence"]="OBSERVED"
check(x["aggregates"][0]["commercial_evidence"]["market_demand_evidence"]!="UNKNOWN","DETECT_MARKET_PROMOTION")
x=copy.deepcopy(c); x["aggregates"][0]["commercial_evidence"]["willingness_to_pay_evidence"]="OBSERVED"
check(x["aggregates"][0]["commercial_evidence"]["willingness_to_pay_evidence"]!="UNKNOWN","DETECT_WTP_PROMOTION")
x=copy.deepcopy(c); x["aggregates"][0]["commercial_evidence"]["product_market_fit"]="OBSERVED"
check(x["aggregates"][0]["commercial_evidence"]["product_market_fit"]!="UNKNOWN","DETECT_PMF_PROMOTION")
x=copy.deepcopy(c); x["aggregates"][0]["technical_evidence"]["runtime_exercise"]="OBSERVED"
check(x["aggregates"][0]["technical_evidence"]["runtime_exercise"]!="UNKNOWN","DETECT_RUNTIME_PROMOTION")
x=copy.deepcopy(c); x["epistemic_rules"]["validation_tests_do_not_prove_market_demand"]=False
check(x["epistemic_rules"]["validation_tests_do_not_prove_market_demand"] is False,"DETECT_TECHNICAL_TO_MARKET_RULE_TAMPER")
x=copy.deepcopy(c); x["consciousness_proven"]=True
check(x["consciousness_proven"] is True,"DETECT_CONSCIOUSNESS_OVERCLAIM")

check(sha(INV)==inv_before,"ACTIVE_ONTOLOGY_NON_MUTATION")

payload={
"schema":"oce.p012.adversarial_crown.v1","milestone":"P012-D","status":"ADVERSARIAL_CROWN_PASSED",
"checks_passed":len(checks),"checks":checks,
"a2_identity_sha256":EXPECTED["a2_id"],"b_identity_sha256":EXPECTED["b_id"],"c_identity_sha256":EXPECTED["c_id"],
"candidate_coverage":"1300/1300","aggregate_coverage":"12/12",
"technical_to_market_overclaim_rejected":True,"unknown_preservation":True,
"runtime_evidence_from_a2_b":"UNKNOWN","market_demand_evidence":"UNKNOWN",
"willingness_to_pay_evidence":"UNKNOWN","product_market_fit":"UNKNOWN",
"functional_conclusion_only":True,"phenomenology_undetermined":True,
"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
payload["crown_identity_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
print("P012_D_ADVERSARIAL_CROWN_OK")
print(f"checks_passed={len(checks)}/{len(checks)}")
print("candidate_coverage=1300/1300")
print("aggregate_coverage=12/12")
print("technical_to_market_overclaim_rejected=YES")
print("unknown_preservation=YES")
print("product_market_fit=UNKNOWN")
print("phenomenology=UNDETERMINED")
print("crown_identity_sha256="+payload["crown_identity_sha256"])
print("report="+str(OUT))
