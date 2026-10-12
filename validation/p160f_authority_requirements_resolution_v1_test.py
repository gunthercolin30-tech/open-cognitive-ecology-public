from ontology.p160_authority_requirements_resolution import *
def base():
    r={"request_id":"R1","constitutional_snapshot_hash":"S","compiled_profile_hash":"P"}
    c={"runtime_context_fingerprint":"C"}; s={"snapshot_hash":"S"}; p={"profile_hash":"P"}
    e={"resolution_hash":"E","authority_created":False,"authorization_created":False}
    req={"authority_class":"GOVERNANCE","mode":"ALL_OF","scope":{"action_class":["A"]},
         "purpose":"govern","quorum":{"n":1,"required_roles":["APPROVER"]},"delegability":False}
    h={"holder_id":"H1","kind":"HUMAN","status":"ACTIVE","environment":"PRODUCTION",
       "authority_classes":["GOVERNANCE"],"scope":{"action_class":["A"]},"purposes":["govern"],
       "roles":["APPROVER"],"provenance":["role","mandate","governance","constitution","dna","genesis"]}
    a={"authority_requirement":req,"holders":[h],"environment":"PRODUCTION",
       "authority_context_fingerprint":"AF","separation_of_duties":{"forbidden_role_pairs":[]}}
    return r,c,s,p,e,a
def run(*x): return resolve_authority_requirements(*x)
def test_valid_not_authorized():
    z=run(*base()); assert z["authority_status"]=="VALID"; assert z["authorization_created"] is False; assert z["execution_performed"] is False
def test_unknown_class():
    x=list(base()); x[5]["authority_requirement"]["authority_class"]="UNKNOWN"; assert run(*x)["authority_status"]=="UNDETERMINED"
def test_human_absence_no_ai_fallback():
    x=list(base()); x[5]["authority_requirement"]["authority_class"]="HUMAN_RESERVED"; x[5]["authority_requirement"]["human_reserved"]=True
    x[5]["holders"][0]["kind"]="AI"; x[5]["holders"][0]["authority_classes"]=["HUMAN_RESERVED"]
    assert run(*x)["authority_status"]=="HUMAN_RESERVED_UNAVAILABLE"
def test_preexisting_human_succession():
    x=list(base()); q=x[5]["authority_requirement"]; q["authority_class"]="HUMAN_RESERVED"; q["human_reserved"]=True
    x[5]["holders"][0]["authority_classes"]=["HUMAN_RESERVED"]; x[5]["succession_rule"]={"preexisting":True,"valid":True,"successor_holder_id":"H1"}
    assert run(*x)["authority_status"]=="VALID"
def test_scope_widening_rejected():
    x=list(base()); x[5]["authority_requirement"]["scope"]={"action_class":["A","B"]}
    assert run(*x)["authority_status"]=="QUORUM_UNSATISFIED"
def test_delegation_amplification_rejected():
    x=list(base()); parent=dict(x[5]["holders"][0]); parent["holder_id"]="P"; parent["scope"]={"action_class":["A"]}
    child=dict(x[5]["holders"][0]); child["holder_id"]="H1"; child["parent_authority_id"]="P"; child["scope"]={"action_class":["A","B"]}
    x[5]["holders"]=[parent,child]; x[5]["authority_requirement"]["required_holder_id"]="H1"
    assert run(*x)["authority_status"]!="VALID"
def test_quorum_nonaggregation():
    x=list(base()); x[5]["authority_requirement"]["quorum"]={"n":2,"required_roles":["APPROVER"]}
    assert run(*x)["authority_status"]=="QUORUM_UNSATISFIED"
def test_sod():
    x=list(base()); x[5]["holders"][0]["roles"]=["REQUESTER","APPROVER"]
    x[5]["separation_of_duties"]={"forbidden_role_pairs":[["REQUESTER","APPROVER"]]}
    assert run(*x)["authority_status"]=="SEPARATION_OF_DUTIES_UNSATISFIED"
def test_revoked():
    x=list(base()); x[5]["holders"][0]["status"]="REVOKED"; assert run(*x)["authority_status"]=="QUORUM_UNSATISFIED"
def test_shadow_no_production_leak():
    x=list(base()); x[5]["holders"][0]["environment"]="SHADOW"; assert run(*x)["authority_status"]=="QUORUM_UNSATISFIED"
def test_invalid_break_glass():
    x=list(base()); x[5]["break_glass_authority"]={"recovery_specific":True,"temporary":False,"audited":True,"auto_expiring":True,"dna_override":False}
    assert run(*x)["authority_status"]=="INVALID"
def test_valid_break_glass_descriptive_only():
    x=list(base()); x[5]["break_glass_authority"]={"recovery_specific":True,"temporary":True,"audited":True,"auto_expiring":True,"dna_override":False}
    z=run(*x); assert z["authority_status"]=="VALID" and z["authorization_created"] is False
def test_conflict_recusal():
    x=list(base()); x[5]["conflict_of_interest"]={"outcome":"RECUSAL_REQUIRED","holder_ids":["H1"]}
    assert run(*x)["authority_status"]=="QUORUM_UNSATISFIED"
def test_determinism():
    a=run(*base()); b=run(*base()); assert a["resolution_hash"]==b["resolution_hash"]
