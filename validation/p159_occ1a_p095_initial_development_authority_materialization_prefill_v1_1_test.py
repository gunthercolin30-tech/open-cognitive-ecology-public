from ontology.occ_initial_development_authority_materialization import prepare,validate
def run():
 x=prepare()
 assert x["authority_id"]=="OCE-HUMAN-INITIAL-001"
 assert x["mandate"]
 assert x["provenance"]
 assert x["authority_evidence"]
 assert x["constitution_version"]=="CURRENT_GOVERNED_CONSTITUTION"
 assert x["governance_version"]=="CURRENT_GOVERNED_GOVERNANCE"
 assert x["valid_from"]==0
 assert x["valid_until"]==253402300799
 assert x["authenticated"] is True
 assert x["human_confirmed"] is False
 assert x["root_override_all"] is False
 assert x["dna_l0_ordinary_override"] is False
 assert x["artificial_authority_expansion"] is False
 y=dict(x); y["human_confirmed"]=True; y["confirmation_phrase"]="CONFIRM INITIAL DEVELOPMENT HUMAN AUTHORITY"
 assert validate(y)["status"]=="READY_FOR_INDEPENDENT_VERIFICATION"
 z=dict(y); z["root_override_all"]=True
 assert "ROOT_OVERRIDE_ALL_FORBIDDEN" in validate(z)["blockers"]
 print("P159_OCC1A_P095_AUTHORITY_PREFILL_V1_1_FUNCTIONAL_OK")
 print("P159_OCC1A_P095_AUTHORITY_PREFILL_V1_1_DEGRADATION_OK")
 print("P159_OCC1A_P095_AUTHORITY_PREFILL_V1_1_NONREGRESSION_OK")
 print("human_confirmation_still_required=true")
 print("authority_activated=false")
if __name__=="__main__": run()
