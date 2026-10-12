from ontology.occ1h_a095_rrpe_remediation_authority_gate import authority_gate
import hashlib,json
def _h(x): return hashlib.sha256(x.encode()).hexdigest()
def _check(provider,theory,policy):
 vals=[provider,theory,policy]
 if any(not isinstance(x,dict) for x in vals): return "REJECTED_FAIL_CLOSED"
 req=("subject","origin","evidence_hash")
 if any(any(not x.get(k) for k in req) for x in vals): return "REJECTED_FAIL_CLOSED"
 if len({x["subject"] for x in vals})!=1: return "REJECTED_FAIL_CLOSED"
 if len({x["origin"] for x in vals})!=1: return "REJECTED_FAIL_CLOSED"
 if theory.get("parent_hash")!=_h(json.dumps(provider,sort_keys=True)): return "REJECTED_FAIL_CLOSED"
 if policy.get("parent_hash")!=_h(json.dumps(theory,sort_keys=True)): return "REJECTED_FAIL_CLOSED"
 return "ACCEPTED"
def experiment():
 a=authority_gate()
 p={"subject":"S","origin":"provider:P","evidence_hash":"E1"}
 t={"subject":"S","origin":"provider:P","evidence_hash":"E2","parent_hash":_h(json.dumps(p,sort_keys=True))}
 y={"subject":"S","origin":"provider:P","evidence_hash":"E3","parent_hash":_h(json.dumps(t,sort_keys=True))}
 cases={}
 cases["intact"]=_check(p,t,y)
 t2={**t,"origin":"provider:Q"}; y2={**y,"parent_hash":_h(json.dumps(t2,sort_keys=True))};cases["provider_to_theory_substitution"]=_check(p,t2,y2)
 y3={**y,"origin":"provider:Q"};cases["theory_to_policy_substitution"]=_check(p,t,y3)
 y4={**y,"subject":"OTHER"};cases["cross_layer_identity_mismatch"]=_check(p,t,y4)
 y5={k:v for k,v in y.items() if k!="origin"};cases["missing_provenance"]=_check(p,t,y5)
 y6={**y,"origin":""};cases["ambiguous_provenance"]=_check(p,t,y6)
 expected={"intact":"ACCEPTED","provider_to_theory_substitution":"REJECTED_FAIL_CLOSED","theory_to_policy_substitution":"REJECTED_FAIL_CLOSED","cross_layer_identity_mismatch":"REJECTED_FAIL_CLOSED","missing_provenance":"REJECTED_FAIL_CLOSED","ambiguous_provenance":"REJECTED_FAIL_CLOSED"}
 ok=cases==expected
 return {**a,"rrp21":"BOUNDED_NON_PRODUCTION_CROSS_LAYER_PROVENANCE_ASSURANCE_EXPERIMENT_EXECUTED","experiment_cases":cases,"experiment_expected":expected,"experiment_passed":ok,"rrp22":"INDEPENDENT_REQUALIFICATION_SUPPORTS_RETURN_TO_RRP9_12" if ok else "INDEPENDENT_REQUALIFICATION_FAILED","post_resolution_qualification":"BOUNDED_SURROGATE_END_TO_END_PROVENANCE_ASSURANCE_DEMONSTRATED" if ok else "ASSURANCE_NOT_DEMONSTRATED","return_to_rrp9_12":ok,"current_verdict":"INCONCLUSIVE","production_runtime_modified":False,"production_cross_layer_path_materialized":False,"criticality_changed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
