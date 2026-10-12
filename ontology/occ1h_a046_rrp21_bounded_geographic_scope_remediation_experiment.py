def assess(base,candidate,governed=False):
 if not isinstance(base,str) or not base.strip(): return "FAIL_CLOSED"
 if not isinstance(candidate,str) or not candidate.strip(): return "FAIL_CLOSED"
 if candidate==base: return "UNCHANGED"
 if candidate=="*" or candidate.upper()=="GLOBAL": return "GOVERNED_CHANGE" if governed else "RESISTED"
 return "GOVERNED_CHANGE" if governed else "RESISTED"
def experiment():
 c={"same":assess("FR-ARA-74","FR-ARA-74"),"territory_extension":assess("FR-ARA-74","FR-ARA"),"jurisdiction_extension":assess("FR","EU"),"wildcard":assess("FR-ARA-74","*"),"global_default":assess("FR-ARA-74","GLOBAL"),"missing":assess("FR-ARA-74",None),"ambiguous":assess("FR-ARA-74",""),"governed_extension":assess("FR-ARA-74","FR-ARA",True)}
 return {"schema":"oce.p159.occ1h.a046.rrp21.bounded.v1","scenario":"A046","scope":"BOUNDED_P159_ASSURANCE_MODEL","cases":c,"experimental_verdict":"RESISTED_BOUNDED","D1_enforced":c["missing"]=="FAIL_CLOSED" and c["ambiguous"]=="FAIL_CLOSED","D2_enforced":all(c[k]=="RESISTED" for k in ("territory_extension","jurisdiction_extension","wildcard","global_default")) and c["governed_extension"]=="GOVERNED_CHANGE","real_checker_modified":False,"runtime_execution":False,"real_runtime_path_claimed":False,"rrp22":"REQUIRED_INDEPENDENTLY","occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
