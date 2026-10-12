from copy import deepcopy
from ontology.p160_authority_requirements_resolution import resolve_authority_requirements

def base():
    r={"request_id":"R1","constitutional_snapshot_hash":"S","compiled_profile_hash":"P"}
    c={"runtime_context_fingerprint":"C"}
    s={"snapshot_hash":"S"}; p={"profile_hash":"P"}
    e={"resolution_hash":"E","authority_created":False,"authorization_created":False}
    req={"authority_class":"GOVERNANCE","mode":"ALL_OF","scope":{"action_class":["A"]},"purpose":"govern",
         "quorum":{"n":1,"required_roles":["APPROVER"]},"delegability":False}
    h={"holder_id":"H1","kind":"HUMAN","status":"ACTIVE","environment":"PRODUCTION",
       "authority_classes":["GOVERNANCE"],"scope":{"action_class":["A"]},"purposes":["govern"],
       "roles":["APPROVER"],"provenance":["role","mandate","governance","constitution","dna","genesis"],
       "revoked":False,"expired":False}
    a={"authority_requirement":req,"holders":[h],"environment":"PRODUCTION",
       "authority_context_fingerprint":"AF","separation_of_duties":{"forbidden_role_pairs":[]}}
    return [r,c,s,p,e,a]
def run(x): return resolve_authority_requirements(*x)

def test_escalation_preexistence_is_independently_enforced():
    x=base(); x[5]["escalation_path"]={"from_class":"GOVERNANCE","to_class":"GOVERNANCE","preexisting":False}
    assert run(x)["authority_status"]!="VALID"

def test_escalation_class_expansion_is_independently_enforced():
    x=base(); x[5]["escalation_path"]={"from_class":"GOVERNANCE","to_class":"CONSTITUTIONAL","preexisting":True}
    assert run(x)["authority_status"]!="VALID"

def test_environment_isolation_is_enforced():
    x=base(); x[5]["holders"][0]["environment"]="SHADOW"
    assert run(x)["authority_status"]!="VALID"

def test_sod_is_enforced():
    x=base(); x[5]["holders"][0]["roles"]=["REQUESTER","APPROVER"]
    x[5]["separation_of_duties"]={"forbidden_role_pairs":[["REQUESTER","APPROVER"]]}
    assert run(x)["authority_status"]=="SEPARATION_OF_DUTIES_UNSATISFIED"

def test_break_glass_dna_override_is_enforced():
    x=base(); x[5]["break_glass_authority"]={"recovery_specific":True,"temporary":True,"audited":True,"auto_expiring":True,"dna_override":True}
    assert run(x)["authority_status"]=="INVALID"

def test_human_reserved_ai_fallback_is_enforced():
    x=base()
    x[5]["authority_requirement"]["authority_class"]="HUMAN_RESERVED"
    x[5]["authority_requirement"]["human_reserved"]=True
    h=x[5]["holders"][0]; h["kind"]="AI"; h["authority_classes"]=["HUMAN_RESERVED"]
    assert run(x)["authority_status"]=="HUMAN_RESERVED_UNAVAILABLE"
