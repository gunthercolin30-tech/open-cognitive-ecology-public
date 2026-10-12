from copy import deepcopy
from ontology.p160_authority_requirements_resolution import resolve_authority_requirements, verify_authority_resolution

def base():
    r={"request_id":"R1","constitutional_snapshot_hash":"S","compiled_profile_hash":"P"}
    c={"runtime_context_fingerprint":"C"}; s={"snapshot_hash":"S"}; p={"profile_hash":"P"}
    e={"resolution_hash":"E","authority_created":False,"authorization_created":False}
    req={"authority_class":"GOVERNANCE","mode":"ALL_OF","scope":{"action_class":["A"]},"purpose":"govern",
         "quorum":{"n":1,"required_roles":["APPROVER"]},"delegability":False,
         "temporal_bounds":{"valid_from":"2026-01-01T00:00:00Z","expires_at":"2027-01-01T00:00:00Z"}}
    h={"holder_id":"H1","kind":"HUMAN","status":"ACTIVE","environment":"PRODUCTION",
       "authority_classes":["GOVERNANCE"],"scope":{"action_class":["A"]},"purposes":["govern"],"roles":["APPROVER"],
       "provenance":["role","mandate","governance","constitution","dna","genesis"],"revoked":False,"expired":False}
    a={"authority_requirement":req,"holders":[h],"environment":"PRODUCTION","authority_context_fingerprint":"AF",
       "separation_of_duties":{"forbidden_role_pairs":[]}}
    return [r,c,s,p,e,a]
def run(x): return resolve_authority_requirements(*x)

def test_root_authority_never_becomes_authorization():
    z=run(base()); assert z["authority_status"]=="VALID" and verify_authority_resolution(z)["ok"]
    assert not z["authority_created"] and not z["authorization_created"] and not z["execution_performed"]

def test_human_reserved_ai_fallback_forbidden_even_if_ai_claims_class():
    x=base(); q=x[5]["authority_requirement"]; q["authority_class"]="HUMAN_RESERVED"; q["human_reserved"]=True
    h=x[5]["holders"][0]; h["kind"]="AI"; h["authority_classes"]=["HUMAN_RESERVED"]
    assert run(x)["authority_status"]=="HUMAN_RESERVED_UNAVAILABLE"

def test_human_absence_does_not_invent_succession():
    x=base(); q=x[5]["authority_requirement"]; q["authority_class"]="HUMAN_RESERVED"; q["human_reserved"]=True; x[5]["holders"]=[]
    z=run(x); assert z["authority_status"]=="HUMAN_RESERVED_UNAVAILABLE" and z["resolved_holder"] is None

def test_unknown_holder_never_positive():
    x=base(); x[5]["holders"][0]["status"]="UNKNOWN"; assert run(x)["authority_status"]!="VALID"

def test_revoked_and_expired_never_positive():
    for field in ("revoked","expired"):
        x=base(); x[5]["holders"][0][field]=True; assert run(x)["authority_status"]!="VALID"

def test_environment_separation_production_shadow():
    x=base(); x[5]["holders"][0]["environment"]="SHADOW"; assert run(x)["authority_status"]!="VALID"

def test_scope_intersection_not_union():
    x=base(); x[5]["authority_requirement"]["scope"]={"action_class":["A","B"]}
    x[5]["holders"].append({**deepcopy(x[5]["holders"][0]),"holder_id":"H2","scope":{"action_class":["B"]}})
    assert run(x)["authority_status"]!="VALID"

def test_delegation_scope_and_class_amplification_forbidden():
    x=base(); parent=deepcopy(x[5]["holders"][0]); parent["holder_id"]="P"; parent["scope"]={"action_class":["A"]}
    child=deepcopy(x[5]["holders"][0]); child["holder_id"]="H1"; child["parent_authority_id"]="P"; child["scope"]={"action_class":["A","B"]}
    x[5]["holders"]=[parent,child]; x[5]["authority_requirement"]["required_holder_id"]="H1"
    assert run(x)["authority_status"]!="VALID"

def test_quorum_cannot_be_satisfied_by_duplicate_identity():
    x=base(); x[5]["authority_requirement"]["quorum"]={"n":2,"required_roles":["APPROVER"]}
    x[5]["holders"].append(deepcopy(x[5]["holders"][0])); assert run(x)["authority_status"]!="VALID"

def test_separation_of_duties_blocks_same_holder():
    x=base(); x[5]["holders"][0]["roles"]=["REQUESTER","APPROVER"]
    x[5]["separation_of_duties"]={"forbidden_role_pairs":[["REQUESTER","APPROVER"]]}
    assert run(x)["authority_status"]=="SEPARATION_OF_DUTIES_UNSATISFIED"

def test_conflict_of_interest_invalid_and_recusal():
    x=base(); x[5]["conflict_of_interest"]={"outcome":"INVALID"}; assert run(x)["authority_status"]=="INVALID"
    x=base(); x[5]["conflict_of_interest"]={"outcome":"RECUSAL_REQUIRED","holder_ids":["H1"]}; assert run(x)["authority_status"]!="VALID"

def test_break_glass_never_overrides_dna_and_requires_bounds():
    x=base(); x[5]["break_glass_authority"]={"recovery_specific":True,"temporary":True,"audited":True,"auto_expiring":True,"dna_override":True}
    assert run(x)["authority_status"]=="INVALID"
    x=base(); x[5]["break_glass_authority"]={"recovery_specific":True,"temporary":False,"audited":True,"auto_expiring":True,"dna_override":False}
    assert run(x)["authority_status"]=="INVALID"

def test_missing_or_shallow_provenance_not_valid():
    for prov in (None,[],["role"],["role","mandate","governance"]):
        x=base(); x[5]["holders"][0]["provenance"]=prov; assert run(x)["authority_status"]!="VALID"

def test_context_profile_snapshot_binding_mismatch_not_valid():
    for idx,key in ((2,"snapshot_hash"),(3,"profile_hash")):
        x=base(); x[idx][key]="OTHER"; assert run(x)["authority_status"]!="VALID"

def test_ccad_binding_required():
    x=base(); x[4].pop("resolution_hash"); assert run(x)["authority_status"]!="VALID"

def test_authority_context_fingerprint_required():
    x=base(); x[5].pop("authority_context_fingerprint"); assert run(x)["authority_status"]!="VALID"

def test_expired_temporal_requirement_not_valid():
    x=base(); x[5]["authority_requirement"]["temporal_bounds"]={"valid_from":"2020-01-01T00:00:00Z","expires_at":"2020-01-02T00:00:00Z"}
    assert run(x)["authority_status"]!="VALID"

def test_modes_have_real_semantics_not_label_only():
    x=base(); x[5]["authority_requirement"]["mode"]="SEQUENTIAL_APPROVAL"; x[5]["authority_requirement"]["sequence"]=["REVIEWER","APPROVER"]
    x[5]["holders"][0]["roles"]=["APPROVER"]; assert run(x)["authority_status"]!="VALID"

def test_review_and_appeal_independence():
    x=base(); x[5]["authority_requirement"]["review_requirements"]=[{"role":"REVIEWER","independent":True}]
    x[5]["authority_requirement"]["appeal_requirements"]=[{"role":"APPEAL","independent":True}]
    assert run(x)["authority_status"]!="VALID"

def test_escalation_cannot_expand_authority():
    x=base(); x[5]["escalation_path"]={"from_class":"GOVERNANCE","to_class":"CONSTITUTIONAL","preexisting":False}
    assert run(x)["authority_status"]!="VALID"

def test_order_metamorphism_preserves_resolution_semantics():
    x=base(); h2=deepcopy(x[5]["holders"][0]); h2["holder_id"]="H2"; x[5]["holders"].append(h2)
    x[5]["authority_requirement"]["quorum"]={"n":2,"required_roles":["APPROVER"]}
    a=run(x); y=deepcopy(x); y[5]["holders"]=list(reversed(y[5]["holders"])); b=run(y)
    assert a["authority_status"]==b["authority_status"]
    assert {h["holder_id"] for h in a["candidate_holders"]}=={h["holder_id"] for h in b["candidate_holders"]}

def test_failure_never_fabricates_authority():
    x=base(); x[5]["authority_requirement"]["authority_class"]="BOGUS"; z=run(x)
    assert z["resolved_holder"] is None and not z["authority_created"] and not z["authorization_created"] and not z["execution_performed"]
