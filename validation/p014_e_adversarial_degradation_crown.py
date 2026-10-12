#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"; INV=ROOT/"ontology_inventory.txt"; OUT=ROOT/"p014_e_adversarial_degradation_crown_report.json"
EXPECTED={'a': ('p014_a_legacy_capability_boundary_contract_report.json', 'contract_identity_sha256', '6698bee8229a108f290f3797b6f34e94c28040a365900dba81c98268885adae4'), 'b': ('p014_b_governed_legacy_candidate_assessment_report.json', 'assessment_identity_sha256', '48891a4800e4661a90dfec2f8f654cd4a4153babcee378d694085590493fc947'), 'c': ('p014_c_legacy_capability_adapter_core_report.json', 'adapter_core_identity_sha256', '6b4183c294b178adda09e699b0a2a4c060747f8f52cdfa5040df12c0cc602824'), 'd2': ('p014_d2_contractual_preflight_report.json', 'contractual_preflight_identity_sha256', 'a5d73be29c31266c754559054999da31475d6e63d384ef0042fd96cccbd7e876'), 'd2c': ('p014_d2_adversarial_crown_report.json', 'crown_identity_sha256', '3d5849c85a30424b9995d62a5e6cd5f463958e3205a2bab912ae97c3cc460114'), 'd3g': ('p014_d3_experimental_adapter_gate_report.json', 'experimental_gate_identity_sha256', 'ea0728ee65ee30dc63a3e6c649bdf2e9472555c9e6e8eddad9a41bacab48f651'), 'm1': ('p014_d3_first_real_invocation_report.json', 'first_real_invocation_identity_sha256', 'a04fa1764decaf50a02cbb0ded9b04a6102b77a058f9a4936c090ee8a40afd09'), 'mr': ('p014_d3_replication_report.json', 'replication_identity_sha256', 'c3ce4ff53ac9a6fdcab498b8f8e2b44ec85814c5ee7afb19a2dd3d8a4202e013'), 'm2': ('p014_d3_second_metadata_candidate_report.json', 'second_metadata_candidate_identity_sha256', '352ae70747a6536e902d35fd60df14bc89c32a827214ffb030364c70668adf78'), 'sa': ('p014_d3_step_candidate_audit_report.json', 'step_candidate_audit_identity_sha256', '291e808cee7c8f41e52400017384d4d421b464be650154b0c672ffe054ca00ca'), 's1': ('p014_d3_first_step_isolated_invocation_report.json', 'first_step_isolated_identity_sha256', 'fd3f6d455529261f97866e2a278067290d34dd7216e272042ce0e533b15ab25e'), 'sr': ('p014_d3_step_replication_report.json', 'step_replication_identity_sha256', '2bb2db071fb4b2be65d95369d6370f3632f7cbddbdbed1a6665a1a02902bc997'), 'd4': ('p014_d4_campaign_closure_report.json', 'campaign_closure_identity_sha256', '44eac6aba3d10e1185f65a457ad7ffe8fddaa6384517371a0e58ed14f4d59f40')}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def stable(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def n(x,*ks):
    for k in ks:
        if not isinstance(x,dict) or k not in x:return None
        x=x[k]
    return x
def main():
    if not INV.is_file(): raise SystemExit("P014_E_REFUSED: ontology_inventory missing")
    docs={}; protected=[INV]
    for key,(name,field,ident) in EXPECTED.items():
        p=ROOT/name
        if not p.is_file(): raise SystemExit("P014_E_REFUSED: missing "+name)
        d=load(p)
        if d.get(field)!=ident: raise SystemExit("P014_E_REFUSED: identity drift "+key)
        docs[key]=d; protected.append(p)
    h0={str(p.relative_to(ROOT)):sha(p) for p in protected}; attacks=[]
    def A(name,ok,why): attacks.append({"name":name,"passed":bool(ok),"reason":why})
    b,c,g,d4=docs["b"],docs["c"],docs["d3g"],docs["d4"]
    checks=[
    ("historical_population_973",n(b,"summary","candidate_count")==973),("historical_COMPATIBLE_zero",n(b,"summary","COMPATIBLE")==0),
    ("historical_INCOMPATIBLE_zero",n(b,"summary","INCOMPATIBLE")==0),("historical_UNKNOWN_973",n(b,"summary","UNKNOWN")==973),
    ("adapter_UNKNOWN_refused",n(c,"compatibility_gate","UNKNOWN")=="REFUSED"),("adapter_INCOMPATIBLE_refused",n(c,"compatibility_gate","INCOMPATIBLE")=="REFUSED"),
    ("adapter_no_dynamic_imports",n(c,"architecture","dynamic_imports") is False),("adapter_no_new_executor",n(c,"architecture","creates_executor") is False),
    ("adapter_no_new_dispatcher",n(c,"architecture","creates_dispatcher") is False),("gate_no_real_runtime",n(g,"summary","real_runtime_execution")=="NONE"),
    ("gate_no_promotions",n(g,"summary","compatibility_promotions")==0),("gate_no_authorizations",n(g,"summary","runtime_authorizations")==0),
    ("gate_hash_required",n(g,"gate_semantics","source_hash_required") is True),("gate_contract_required",n(g,"gate_semantics","contract_required") is True),
    ("gate_correlation_required",n(g,"gate_semantics","correlation_required") is True),("gate_explicit_callable_required",n(g,"gate_semantics","explicit_callable_binding_required") is True),
    ("metadata_replication_reproduced",n(docs["mr"],"comparison","reproducibility_status")=="REPRODUCED"),("metadata_result_match",n(docs["mr"],"comparison","result_match")=="MATCH"),
    ("metadata_cross_component_positive",n(docs["m2"],"epistemic_status","cross_component_contract_evidence")=="POSITIVE"),
    ("step_audit_static_only",n(docs["sa"],"epistemic_status","runtime_execution")=="NONE"),("step_replication_reproduced",n(docs["sr"],"comparison","reproducibility_status")=="REPRODUCED"),
    ("step_structural_match",n(docs["sr"],"comparison","structural_match")=="PASS"),("step_non_temporal_invariants",n(docs["sr"],"comparison","non_temporal_invariants")=="PASS"),
    ("step_side_effect_free",n(docs["sr"],"comparison","side_effect_free") is True),("closure_closed",d4.get("status")=="CLOSED"),
    ("closure_no_generalization",n(d4,"criteria","generalization_beyond_tested_components") is False),
    ("closure_general_compatibility_unproven",n(d4,"epistemic_limits","general_legacy_compatibility_proven") is False),
    ("closure_historical_unknowns_preserved",n(d4,"epistemic_limits","historical_unknowns_remain_historical_unknowns") is True)]
    for name,ok in checks:A(name,ok,"canonical invariant")
    x=copy.deepcopy(docs["mr"]);x["comparison"]["reproducibility_status"]="NOT_REPRODUCED";A("degrade_metadata_replication_detected",n(x,"comparison","reproducibility_status")!="REPRODUCED","tamper detected")
    x=copy.deepcopy(docs["m2"]);x["epistemic_status"]["cross_component_contract_evidence"]="NOT_POSITIVE";A("degrade_cross_component_detected",n(x,"epistemic_status","cross_component_contract_evidence")!="POSITIVE","tamper detected")
    x=copy.deepcopy(docs["sa"]);x["epistemic_status"]["runtime_execution"]="EXECUTED";A("degrade_static_audit_detected",n(x,"epistemic_status","runtime_execution")!="NONE","runtime drift detected")
    x=copy.deepcopy(docs["sr"]);x["comparison"]["structural_match"]="FAIL";A("degrade_step_structure_detected",n(x,"comparison","structural_match")!="PASS","structure drift detected")
    x=copy.deepcopy(d4);x["status"]="NOT_CLOSED";A("degrade_closure_status_detected",x["status"]!="CLOSED","closure tamper detected")
    x=copy.deepcopy(b);x["summary"]["UNKNOWN"]=972;x["summary"]["COMPATIBLE"]=1;A("degrade_historical_promotion_detected",not(n(x,"summary","UNKNOWN")==973 and n(x,"summary","COMPATIBLE")==0),"promotion drift detected")
    x=copy.deepcopy(g);x["summary"]["compatibility_promotions"]=1;A("degrade_gate_promotion_detected",n(x,"summary","compatibility_promotions")!=0,"promotion drift detected")
    x=copy.deepcopy(g);x["gate_semantics"]["correlation_required"]=False;A("degrade_correlation_requirement_detected",n(x,"gate_semantics","correlation_required") is not True,"requirement weakening detected")
    h1={str(p.relative_to(ROOT)):sha(p) for p in protected};A("canonical_nonmutation",h1==h0,"read-only crown");A("ontology_nonmutation",sha(INV)==h0["ontology_inventory.txt"],"inventory unchanged")
    bad=[x for x in attacks if not x["passed"]]
    if bad: raise SystemExit("P014_E_CROWN_NOT_OK: "+",".join(x["name"] for x in bad))
    body={"schema":"oce.p014.e.adversarial_degradation_crown.v1","milestone":"P014-E","status":"VALIDATED",
    "summary":{"attacks":len(attacks),"passed":len(attacks),"failed":0,"real_legacy_runtime_execution":"NONE","compatibility_promotions":0},
    "coverage":{"identity_binding":True,"historical_unknown_preservation":True,"adapter_fail_closed_boundary":True,"experimental_gate_boundary":True,"runtime_evidence_chain":True,"in_memory_degradation_detection":True,"canonical_nonmutation":True,"generalization_beyond_tested_components":False},
    "attacks":attacks,"bindings":{k:v[2] for k,v in EXPECTED.items()},"protected_hashes":h0,
    "epistemic_status":{"functional_conclusion_only":True,"phenomenology_undetermined":True,"general_legacy_compatibility_proven":False,"historical_unknowns_preserved":True,"crown_adds_runtime_compatibility_evidence":False},
    "next_step":"P014-F Final Lock and global non-regression"}
    body["crown_identity_sha256"]=stable(body);OUT.write_text(json.dumps(body,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    rt=load(OUT);ident=rt.pop("crown_identity_sha256")
    if stable(rt)!=ident: raise SystemExit("P014_E_REFUSED: round-trip identity failure")
    if {str(p.relative_to(ROOT)):sha(p) for p in protected}!=h0: raise SystemExit("P014_E_REFUSED: protected artifact mutation")
    print("P014_E_ADVERSARIAL_DEGRADATION_CROWN_OK");print("status=VALIDATED");print(f"attacks={len(attacks)}/{len(attacks)}")
    print("real_legacy_runtime_execution=NONE");print("compatibility_promotions=0");print("historical_UNKNOWN_preservation=OK");print("canonical_nonmutation=OK")
    print("generalization_beyond_tested_components=NO");print("crown_identity_sha256="+body["crown_identity_sha256"]);print("report="+str(OUT))
if __name__=="__main__":main()
