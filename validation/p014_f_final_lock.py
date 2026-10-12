#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
INV=ROOT/"ontology_inventory.txt"
OUT=ROOT/"p014_f_final_lock_report.json"
EXPECTED={'A': ('p014_a_legacy_capability_boundary_contract_report.json', 'contract_identity_sha256', '6698bee8229a108f290f3797b6f34e94c28040a365900dba81c98268885adae4'), 'B': ('p014_b_governed_legacy_candidate_assessment_report.json', 'assessment_identity_sha256', '48891a4800e4661a90dfec2f8f654cd4a4153babcee378d694085590493fc947'), 'C': ('p014_c_legacy_capability_adapter_core_report.json', 'adapter_core_identity_sha256', '6b4183c294b178adda09e699b0a2a4c060747f8f52cdfa5040df12c0cc602824'), 'D': ('p014_d4_campaign_closure_report.json', 'campaign_closure_identity_sha256', '44eac6aba3d10e1185f65a457ad7ffe8fddaa6384517371a0e58ed14f4d59f40'), 'E': ('p014_e_adversarial_degradation_crown_report.json', 'crown_identity_sha256', 'ed75166e9cc53961dbd48c8909042e415d8e98a1b94530c3796f1e63583018bb')}

def fail(msg): raise SystemExit("P014_F_REFUSED: "+msg)
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def content_identity(doc,key):
    x=copy.deepcopy(doc); x.pop(key,None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

if not INV.is_file(): fail("missing ontology_inventory.txt")
inv0=sha(INV)
docs={}
paths={}
for k,(name,field,ident) in EXPECTED.items():
    p=ROOT/name
    if not p.is_file(): fail("missing prerequisite: "+name)
    d=load(p)
    if d.get(field)!=ident: fail(k+" identity drift")
    if content_identity(d,field)!=ident: fail(k+" content drift")
    docs[k]=d; paths[k]=p

a,b,c,d,e=(docs[x] for x in ("A","B","C","D","E"))

if b.get("summary",{}).get("candidate_count")!=973: fail("P014-B population drift")
if b.get("summary",{}).get("COMPATIBLE")!=0 or b.get("summary",{}).get("INCOMPATIBLE")!=0 or b.get("summary",{}).get("UNKNOWN")!=973:
    fail("P014-B historical status boundary drift")
if d.get("status")!="CLOSED": fail("P014-D not CLOSED")
if d.get("coverage",{}).get("real_component_count")!=3: fail("P014-D real component coverage drift")
if d.get("coverage",{}).get("contract_family_count")!=2: fail("P014-D contract family coverage drift")
if d.get("criteria",{}).get("generalization_beyond_tested_components") is not False: fail("P014-D generalization boundary drift")
if d.get("epistemic_limits",{}).get("general_legacy_compatibility_proven") is not False: fail("P014-D epistemic scope drift")
if d.get("epistemic_limits",{}).get("historical_unknowns_remain_historical_unknowns") is not True: fail("P014-D historical UNKNOWN drift")
es=e.get("summary",{})
if e.get("status")!="VALIDATED" or es.get("attacks")!=38 or es.get("passed")!=38 or es.get("failed")!=0:
    fail("P014-E crown not 38/38")
if es.get("real_legacy_runtime_execution")!="NONE": fail("P014-E runtime drift")
if es.get("compatibility_promotions")!=0: fail("P014-E promotion drift")
if e.get("coverage",{}).get("canonical_nonmutation") is not True: fail("P014-E canonical nonmutation drift")
if e.get("coverage",{}).get("generalization_beyond_tested_components") is not False: fail("P014-E generalization drift")
epi=e.get("epistemic_status",{})
for k,v in {
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
 "general_legacy_compatibility_proven":False,
 "historical_unknowns_preserved":True,
 "crown_adds_runtime_compatibility_evidence":False,
}.items():
    if epi.get(k)!=v: fail("P014-E epistemic invariant drift: "+k)

if sha(INV)!=inv0: fail("ontology inventory mutated before lock")

report={
 "schema":"oce.p014.final_lock.v1",
 "milestone":"P014-F",
 "status":"LOCKED",
 "p014_status":"CLOSED_LOCKED",
 "historical_candidate_population":973,
 "historical_status_counts":{"COMPATIBLE":0,"INCOMPATIBLE":0,"UNKNOWN":973},
 "representative_runtime_evidence":{
   "real_components_tested":3,
   "contract_families_tested":2,
   "campaign_status":"CLOSED",
   "scope":"tested component + source hash + callable + explicit contract only"
 },
 "adversarial_degradation_crown":"38/38",
 "bindings":{
   "p014_a_identity_sha256":EXPECTED["A"][2],"p014_a_report_sha256":sha(paths["A"]),
   "p014_b_identity_sha256":EXPECTED["B"][2],"p014_b_report_sha256":sha(paths["B"]),
   "p014_c_identity_sha256":EXPECTED["C"][2],"p014_c_report_sha256":sha(paths["C"]),
   "p014_d_identity_sha256":EXPECTED["D"][2],"p014_d_report_sha256":sha(paths["D"]),
   "p014_e_identity_sha256":EXPECTED["E"][2],"p014_e_report_sha256":sha(paths["E"]),
   "ontology_inventory_sha256":inv0,
 },
 "locked_claims":{
   "legacy_capability_boundary_validated":True,
   "governed_candidate_assessment_validated":True,
   "adapter_core_validated":True,
   "representative_compatibility_campaign_closed":True,
   "adversarial_degradation_crown_passed":True,
   "historical_unknown_population_preserved":True,
   "runtime_compatibility_claims_are_local_only":True,
   "general_legacy_compatibility_proven":False,
   "no_population_wide_compatibility_promotion":True,
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
   "closes":"P014 Legacy Capability Adapter only",
   "does_not_close":"later W1 milestones or any claim of general legacy runtime compatibility",
   "historical_unknown_semantics":"P014-B historical UNKNOWN remains unchanged by local report-layer runtime observations",
   "compatible_semantics":"only exact tested component, source hash, callable and explicit contract with positive evidence",
 },
 "next_step":"global non-regression via python3 -m validation.main"
}
report["final_lock_identity_sha256"]=hashlib.sha256(
 json.dumps(report,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
).hexdigest()

if sha(INV)!=inv0: fail("ontology inventory mutated during lock")
OUT.write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
rt=load(OUT); rid=rt.pop("final_lock_identity_sha256")
if hashlib.sha256(json.dumps(rt,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()!=rid:
    fail("round-trip final-lock identity failure")
if sha(INV)!=inv0: fail("ontology inventory mutated after lock")

print("P014_F_FINAL_LOCK_OK")
print("status=LOCKED")
print("p014_status=CLOSED_LOCKED")
print("historical_candidates=973")
print("historical_UNKNOWN=973")
print("real_components_tested=3")
print("contract_families_tested=2")
print("p014_e_crown=38/38")
print("p014_a_binding=VERIFIED")
print("p014_b_binding=VERIFIED")
print("p014_c_binding=VERIFIED")
print("p014_d_binding=VERIFIED")
print("p014_e_binding=VERIFIED")
print("general_legacy_compatibility_proven=NO")
print("ontology_inventory_non_mutation=OK")
print("final_lock_identity_sha256="+rid)
print("report="+str(OUT))
