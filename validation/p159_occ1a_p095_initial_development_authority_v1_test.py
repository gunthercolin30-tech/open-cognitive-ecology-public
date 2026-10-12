from ontology.human_reserved_authority_registry import (P095Canonical,InitialDevelopmentAuthoritySpec,ReservedEntry,RESERVED_CLASSES,INITIAL_DEVELOPMENT_HOLDER,ROOT_OVERRIDE_ALL,PASS,FAIL,ActionManifest)
def spec(**kw):
 d=dict(authority_id="OCE-HUMAN-INITIAL-001",provenance="human_constituent_development_provenance",mandate="Initial human authority over currently reserved human functions until governed change",valid_from=1,valid_until=4102444800,constitution_version="development-current",governance_version="development-current",context="DEVELOPMENT",authenticated=True); d.update(kw); return InitialDevelopmentAuthoritySpec(**d)
def run():
 p=P095Canonical(); r=p.initialize_development_authority(spec()); assert r["status"]==PASS
 a=p.authorities["OCE-HUMAN-INITIAL-001"]; assert a.human_identity==INITIAL_DEVELOPMENT_HOLDER; assert set(a.scope)==set(RESERVED_CLASSES); assert "*" not in a.scope; assert ROOT_OVERRIDE_ALL is False; assert r["dna_l0_override"] is False; assert r["artificial_authority_expansion"] is False
 assert p.initialize_development_authority(spec(authority_id="OTHER"))["status"]==FAIL
 q=P095Canonical(); assert q.initialize_development_authority(spec(provenance=""))["status"]==FAIL; assert q.initialize_development_authority(spec(authenticated=False))["status"]==FAIL
 p.register_reserved(ReservedEntry("cc","CONSTITUTIONAL_CHANGE",("x",),("CONSTITUTIONAL_AUTHORITY",),1,1,False,4102444800))
 m=ActionManifest("a","CONSTITUTIONAL_CHANGE","o","DEVELOPMENT","DNA-L0",False,False,"risk",("objection",),("e1","e2"),"n1",2)
 x=p.authorize(m,("OCE-HUMAN-INITIAL-001",),("founder-domain",),2,"rationale",True,out_of_band=True); assert x["status"]==FAIL and x["reason"]=="dna_l0_requires_fork_refounding"
 print("P159_OCC1A_P095_INITIAL_DEVELOPMENT_AUTHORITY_FUNCTIONAL_OK"); print("P159_OCC1A_P095_INITIAL_DEVELOPMENT_AUTHORITY_DEGRADATION_OK"); print("P159_OCC1A_P095_INITIAL_DEVELOPMENT_AUTHORITY_NONREGRESSION_OK")
if __name__=="__main__": run()
