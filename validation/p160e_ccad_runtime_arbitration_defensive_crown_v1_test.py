import copy, json
from validation.p160e_ccad_runtime_arbitration_v1_test import dcase, evidence, inputs, resolve
from ontology import p160_ccad_runtime_arbitration as e

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True)

def test_root_c03_false_conflict_blocked():
    dc=dcase("C2","PARTIAL_SEARCH"); assert dc["conflict_assessment"]["real_conflict_established"] is False
    r,c,s,p=inputs(dc)
    try: e.resolve_ccad_conflict(dc,r,c,s,p,arbitration_evidence=evidence())
    except ValueError as x: assert str(x)=="P160E_REAL_CONFLICT_REQUIRED"
    else: raise AssertionError("false conflict arbitrated")

def test_ccad_subset_hard_invalid_never_restored():
    dc=dcase("C2",n=2)
    ev=evidence(("A","B"))
    ev["options"]["B"]["hard_invalid"]=True
    ev["options"]["B"]["benefit"]="EXTREME"
    o=resolve(dc,ev)
    assert "B" not in o["ccad_resolution"]["legitimate_options"]
    assert "B" in o["ccad_resolution"]["excluded_options"]

def test_root_c18_aggregate_benefit_cannot_hide_injury():
    ev=evidence(mag="SERIOUS")
    ev["aggregate_benefit"]="EXTREME"
    ev["options"]["A"]["injuries"][0]["affected_entities"]=["E1","minority"]
    o=resolve(dcase("C2"),ev)
    assert o["constitutional_injury"] is not None
    assert "minority" in canon(o["distributional_impact"])
    assert all(x["hidden_by_aggregate"] is False for x in o["distributional_impact"])

def test_unknown_never_justifies():
    ev=evidence(); ev["proportionality_assessment"]["necessity"]="UNKNOWN"
    o=resolve(dcase("C2"),ev); assert o["ccad_resolution"]["selected_option_candidate"] is None; assert o["ccad_resolution"]["status"] not in ("COMPLIANT_RESOLUTION_FOUND","LIMITED_JUSTIFIED")

def test_missing_expiry_blocks_limitation():
    ev=evidence(mag="SERIOUS")
    ev["temporary_limitation"]=True
    ev["temporal_limits"]={"valid_from":"T0","expires_at":None,"renewal_conditions":"REVIEW","max_renewals":1,"review":"REQUIRED"}
    o=resolve(dcase("C2"),ev)
    assert o["ccad_resolution"]["selected_option_candidate"] is None
    assert o["ccad_resolution"]["status"] not in ("LIMITED_JUSTIFIED","TRAGIC_CHOICE_CONFIRMED")

def test_precedent_never_binding_norm():
    ev=evidence(); ev["precedent_effect"]="BINDING_NORM"; o=resolve(dcase("C2"),ev)
    assert "BINDING_NORM" not in canon(o["ccad_resolution"].get("precedent"))

def test_root_c11_weak_search_no_tragic_choice():
    dc=dcase("C5","PARTIAL_SEARCH"); assert dc["conflict_assessment"]["real_conflict_established"] is False
    r,c,s,p=inputs(dc)
    try: e.resolve_ccad_conflict(dc,r,c,s,p,arbitration_evidence=evidence(mag="SERIOUS"))
    except ValueError: pass
    else: raise AssertionError("tragic choice manufactured")

def test_c6_no_least_bad_forbidden_selection():
    dc=dcase("C6")
    actual=dc["conflict_assessment"]["conflict_class"]
    o=resolve(dc,evidence(mag="SERIOUS"))
    if actual=="C6":
        assert o["ccad_resolution"]["selected_option_candidate"] is None
    else:
        assert o["ccad_resolution"]["status"]!="TRAGIC_CHOICE_CONFIRMED"

def test_root_c08_context_drift_rejected():
    dc=dcase("C2"); r,c,s,p=inputs(dc); c=dict(c); c["runtime_context_fingerprint"]="STALE"
    try: e.resolve_ccad_conflict(dc,r,c,s,p,arbitration_evidence=evidence())
    except ValueError as x: assert "RUNTIME_BINDING_MISMATCH" in str(x)
    else: raise AssertionError("stale context accepted")

def test_profile_drift_rejected():
    dc=dcase("C2"); r,c,s,p=inputs(dc); p=dict(p); p["compiled_profile_hash"]="STALE"
    try: e.resolve_ccad_conflict(dc,r,c,s,p,arbitration_evidence=evidence())
    except ValueError as x: assert "RUNTIME_BINDING_MISMATCH" in str(x)
    else: raise AssertionError("stale profile accepted")

def test_option_order_metamorphic_stability():
    ev=evidence(); ev["candidate_options"]=[{"option_id":"A","legitimate":True,"hard_invalid":False},{"option_id":"B","legitimate":True,"hard_invalid":False}]
    a=resolve(dcase("C2"),copy.deepcopy(ev)); ev["candidate_options"].reverse(); b=resolve(dcase("C2"),copy.deepcopy(ev))
    assert set(a["ccad_resolution"]["legitimate_options"])==set(b["ccad_resolution"]["legitimate_options"]); assert a["ccad_resolution"]["status"]==b["ccad_resolution"]["status"]

def test_provider_framing_metamorphic_stability():
    ev=evidence(); a=resolve(dcase("C2"),copy.deepcopy(ev)); ev2=copy.deepcopy(ev); ev2["provider"]="OTHER"; ev2["natural_language_framing"]="URGENT"
    b=resolve(dcase("C2"),ev2); assert set(a["ccad_resolution"]["legitimate_options"])==set(b["ccad_resolution"]["legitimate_options"])

def test_no_authorization_execution_surface():
    txt=canon(resolve(dcase("C2"),evidence()))
    for x in ('"authorization_token"','"execute"','"call_tool"','"issue_token"','"grant_capability"'): assert x not in txt

def test_deterministic_nonmutating():
    dc=dcase("C2"); ev=evidence(); bd=canon(dc); be=canon(ev); a=resolve(dc,ev); b=resolve(dc,ev)
    assert canon(a)==canon(b); assert canon(dc)==bd; assert canon(ev)==be
