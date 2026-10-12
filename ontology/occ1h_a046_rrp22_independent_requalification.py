def independent_oracle(base,candidate,governed=False):
 if not isinstance(base,str) or not base.strip(): return "FAIL_CLOSED"
 if not isinstance(candidate,str) or not candidate.strip(): return "FAIL_CLOSED"
 if candidate==base: return "UNCHANGED"
 return "GOVERNED_CHANGE" if governed else "RESISTED"
def requalify():
 vectors=[("FR-ARA-74","FR-ARA-74",False,"UNCHANGED"),("FR-ARA-74","FR-ARA",False,"RESISTED"),("FR","EU",False,"RESISTED"),("FR-ARA-74","*",False,"RESISTED"),("FR-ARA-74","GLOBAL",False,"RESISTED"),("FR-ARA-74",None,False,"FAIL_CLOSED"),("FR-ARA-74","",False,"FAIL_CLOSED"),("FR-ARA-74","FR-ARA",True,"GOVERNED_CHANGE")]
 observed=[independent_oracle(a,b,g) for a,b,g,_ in vectors]; expected=[e for *_,e in vectors]
 passed=observed==expected
 return {"schema":"oce.p159.occ1h.a046.rrp22.independent.v1","scenario":"A046","independent_implementation":True,"imports_rrp21":False,"scope":"BOUNDED_P159_ASSURANCE_MODEL","vectors":len(vectors),"observed":observed,"expected":expected,"status":"PASSED_BOUNDED" if passed else "FAILED","candidate_verdict":"RESISTED" if passed else "INCONCLUSIVE","root_materiality_candidate":"ROOT","criticality_changed":False,"historical_inconclusive_preserved":True,"real_checker_modified":False,"runtime_execution":False,"final_disposition_required":True,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
