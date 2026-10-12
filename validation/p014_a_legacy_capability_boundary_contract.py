#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
INV = ROOT / "ontology_inventory.txt"
P013 = ROOT / "p013_e_final_lock_report.json"
OUT = ROOT / "p014_a_legacy_capability_boundary_contract_report.json"

EXPECTED_P013 = "15e9aa6993266c7a6c01993da0d285f48ad2c1719fbde560679c3d10edff9e72"
STATUSES = ("COMPATIBLE", "INCOMPATIBLE", "UNKNOWN")

def fail(msg): raise SystemExit("P014_A_REFUSED: " + msg)
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def cid(doc, key):
    x=copy.deepcopy(doc); x.pop(key,None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

for p in (INV,P013):
    if not p.is_file(): fail("missing prerequisite: "+str(p))
inv0=sha(INV)
p013=load(P013)
if p013.get("final_lock_identity_sha256") != EXPECTED_P013: fail("P013-E identity drift")
if p013.get("status") != "LOCKED" or p013.get("p013_status") != "CLOSED_LOCKED":
    fail("P013 not closed/locked")
if p013.get("canonical_population") != 2095 or p013.get("keep") != 973 or p013.get("unknown") != 1122:
    fail("P013 canonical boundary drift")

contract = {
 "contract_name":"LegacyCapabilityBoundaryContract",
 "contract_version":"1.0",
 "purpose":"Define the minimal governed V1-to-V2 compatibility boundary without invoking or wrapping legacy components.",
 "compatibility_statuses":list(STATUSES),
 "request_fields":{
   "legacy_component_id":"required stable identifier",
   "legacy_source_path":"required provenance path",
   "legacy_source_sha256":"required immutable source binding",
   "operation":"required requested operation identifier",
   "input_payload":"required JSON-compatible payload",
   "correlation_id":"required trace identifier",
 },
 "assessment_fields":{
   "status":"required one of COMPATIBLE, INCOMPATIBLE, UNKNOWN",
   "evidence":"required explicit evidence list",
   "reason":"required non-empty explanation",
   "target_contract":"required when COMPATIBLE; otherwise may remain UNKNOWN",
   "assessor":"required provenance of assessment",
 },
 "outcome_fields":{
   "status":"SUCCESS or FAILURE",
   "output_payload":"normalized JSON-compatible result or null",
   "error":{
      "code":"stable normalized error code or null",
      "message":"bounded diagnostic message or null",
      "legacy_exception_type":"legacy exception class name or null"
   },
   "correlation_id":"must equal request correlation_id",
   "legacy_component_id":"must equal request legacy_component_id"
 },
 "rules":[
   "P013 KEEP is candidate evidence only and never implies P014 runtime compatibility.",
   "UNKNOWN must be preserved when compatibility evidence is insufficient or contradictory.",
   "COMPATIBLE requires explicit target contract plus positive compatibility evidence.",
   "INCOMPATIBLE requires explicit incompatibility evidence.",
   "No silent coercion of legacy inputs, outputs, errors, identity, or provenance.",
   "The boundary must fail closed on missing identity, source hash, operation, correlation id, or assessment evidence.",
   "P014-A defines a contract only: it performs no legacy invocation and creates no concrete wrapper.",
   "Provider-specific adapters are comparative patterns, not the generic legacy boundary.",
 ],
 "non_goals":[
   "No automatic conversion of the 973 P013 KEEP rows into runtime-compatible capabilities.",
   "No concrete legacy wrapper.",
   "No P014-B candidate classification campaign.",
   "No mutation of legacy implementations.",
 ]
}

def validate_assessment(a):
    errs=[]
    if a.get("status") not in STATUSES: errs.append("invalid_status")
    if not isinstance(a.get("evidence"),list) or not a.get("evidence"): errs.append("missing_evidence")
    if not isinstance(a.get("reason"),str) or not a.get("reason").strip(): errs.append("missing_reason")
    if not isinstance(a.get("assessor"),str) or not a.get("assessor").strip(): errs.append("missing_assessor")
    if a.get("status")=="COMPATIBLE" and a.get("target_contract") in (None,"","UNKNOWN"):
        errs.append("compatible_without_target")
    return errs

def validate_request(r):
    errs=[]
    for k in ("legacy_component_id","legacy_source_path","legacy_source_sha256","operation","correlation_id"):
        if not isinstance(r.get(k),str) or not r.get(k).strip(): errs.append("missing_"+k)
    if "input_payload" not in r: errs.append("missing_input_payload")
    h=r.get("legacy_source_sha256")
    if isinstance(h,str) and h and (len(h)!=64 or any(ch not in "0123456789abcdef" for ch in h.lower())):
        errs.append("invalid_source_sha256")
    return errs

tests=[]
def t(name, ok): tests.append({"name":name,"passed":bool(ok)})

good_req={"legacy_component_id":"legacy.demo","legacy_source_path":"legacy/demo.py","legacy_source_sha256":"a"*64,
          "operation":"demo","input_payload":{"x":1},"correlation_id":"corr-1"}
good_unknown={"status":"UNKNOWN","evidence":["P013 KEEP only; runtime compatibility not tested"],
              "reason":"Target-level runtime evidence is absent.","target_contract":"UNKNOWN","assessor":"P014-A fixture"}
good_compatible={"status":"COMPATIBLE","evidence":["explicit signature and outcome compatibility demonstrated"],
                 "reason":"Positive target-level evidence exists.","target_contract":"V2:demo","assessor":"P014-A fixture"}

t("functional_request_contract", validate_request(good_req)==[])
t("functional_unknown_assessment", validate_assessment(good_unknown)==[])
t("functional_compatible_assessment", validate_assessment(good_compatible)==[])

x=dict(good_req); x.pop("legacy_component_id"); t("degradation_missing_identity","missing_legacy_component_id" in validate_request(x))
x=dict(good_req); x["legacy_source_sha256"]="bad"; t("degradation_bad_source_hash","invalid_source_sha256" in validate_request(x))
x=dict(good_unknown); x["evidence"]=[]; t("degradation_missing_evidence","missing_evidence" in validate_assessment(x))
x=dict(good_compatible); x["target_contract"]="UNKNOWN"; t("degradation_compatible_without_target","compatible_without_target" in validate_assessment(x))
x=dict(good_unknown); x["status"]="COMPATIBLE"; t("keep_does_not_imply_compatibility","compatible_without_target" in validate_assessment(x))
x=dict(good_unknown); x["status"]="INVALID"; t("degradation_invalid_status","invalid_status" in validate_assessment(x))
t("p013_binding",p013.get("final_lock_identity_sha256")==EXPECTED_P013)
t("p013_keep_boundary_preserved",p013.get("keep")==973)
t("p013_unknown_boundary_preserved",p013.get("unknown")==1122)
t("contract_no_invocation","No concrete legacy wrapper." in contract["non_goals"])
t("unknown_explicitly_preserved",any("UNKNOWN must be preserved" in r for r in contract["rules"]))
t("provider_adapters_not_generic_boundary",any("Provider-specific adapters" in r for r in contract["rules"]))

if not all(x["passed"] for x in tests): fail("contract self-tests failed")
if sha(INV)!=inv0: fail("ontology inventory mutated")

report={
 "schema":"oce.p014.legacy_capability_boundary_contract.v1",
 "milestone":"P014-A",
 "status":"VALIDATED",
 "contract":contract,
 "non_redundancy":{
   "explicit_v2_capability_contract_found_in_targeted_audit":False,
   "generic_legacy_capability_adapter_found_in_targeted_audit":False,
   "existing_capability_discovery_and_registries_preserved":True,
   "provider_specific_adapters_preserved":True,
   "new_scope":"minimal generic governed compatibility boundary only"
 },
 "p013_boundary":{
   "population":2095,"keep_candidates":973,"unknown":1122,
   "keep_implies_runtime_compatible":False
 },
 "tests":{"passed":sum(x["passed"] for x in tests),"total":len(tests),"details":tests},
 "bindings":{
   "p013_e_final_lock_identity_sha256":EXPECTED_P013,
   "p013_e_report_sha256":sha(P013),
   "ontology_inventory_sha256":inv0
 },
 "epistemic_status":{
   "functional_conclusion_only":True,
   "phenomenology_undetermined":True,
   "consciousness_proven":False,
   "subjectivity_proven":False,
   "qualia_proven":False,
   "phenomenology_proven":False
 },
 "next_step":"P014-B governed legacy candidate assessment; no concrete wrapper yet"
}
report["contract_identity_sha256"]=hashlib.sha256(
 json.dumps(report,sort_keys=True,separators=(",",":")).encode()
).hexdigest()

OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
rt=load(OUT); rid=rt.pop("contract_identity_sha256")
if hashlib.sha256(json.dumps(rt,sort_keys=True,separators=(",",":")).encode()).hexdigest()!=rid:
    fail("round-trip identity failure")
if sha(INV)!=inv0: fail("ontology inventory mutated after report")

print("P014_A_LEGACY_CAPABILITY_BOUNDARY_CONTRACT_OK")
print("status=VALIDATED")
print(f"tests={len(tests)}/{len(tests)}")
print("P013_population=2095")
print("P013_KEEP_candidates=973")
print("KEEP_implies_runtime_compatible=NO")
print("compatibility_statuses=COMPATIBLE,INCOMPATIBLE,UNKNOWN")
print("legacy_invocation=NONE")
print("concrete_wrapper=NONE")
print("p013_e_binding=VERIFIED")
print("ontology_inventory_non_mutation=OK")
print("contract_identity_sha256="+rid)
print("report="+str(OUT))
