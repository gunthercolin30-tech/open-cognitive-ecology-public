from __future__ import annotations
import copy

from ontology import operational_constitutional_invariants as oci
from ontology import p160_norm_resolution as b
from ontology import p160_constitutive_filter as c
from ontology import p160_normative_conflict_detection as d
from ontology import p160_ccad_runtime_arbitration as e

def ca():
    rules=[{"rule_id":"DNA-L0.3","source_norm_ids":["DNA-L0.3"],"constitutive":True,"always_evaluate":True,"conditions":[]}]
    nr=b.resolve_norms({},{"artifact_hash":"profile","source_map":{"DNA-L0.3":"canonical"},"rules":rules},{"constitutional_snapshot":{"snapshot_semantic_hash":"snap"},"decision_context_fingerprint":{"fingerprint":"fp"}})
    return c.filter_constitutive(nr,{"constraints":{"DNA-L0.3":"PASS"},"invariants":{x:"PASS" for x in oci.MANDATORY_INVARIANTS}})

def reqs():
    return [
        {"requirement_id":"R1","source_norms":["N1"],"type":"OBLIGATION","protected_interest":"I1","affected_entities":["E1"],"condition":"X","scope":"S","time":"T","formalization":"F3","flexibility":"BOUNDED"},
        {"requirement_id":"R2","source_norms":["N2"],"type":"PRESERVATION","protected_interest":"I2","affected_entities":["E2"],"condition":"Y","scope":"S","time":"T","formalization":"F3","flexibility":"BOUNDED"},
    ]

def alt(aid):
    return {"alternative_id":aid,"availability":"AVAILABLE_NOW","effects":{},"impacts":{},"resources":{},"latency":1,"reversibility":"YES","uncertainty":"LOW","feasibility":"PROVEN","authority":"UNRESOLVED","compatibility":{"R1":"INCOMPATIBLE_UNDER_CURRENT_OPTION","R2":"INCOMPATIBLE_UNDER_CURRENT_OPTION"}}

def dcase(klass="C2", completeness="ADEQUATE_SEARCH", n=1):
    return d.detect_normative_conflict(ca(), reqs(), [alt(chr(65+i)) for i in range(n)], search_completeness=completeness, classification_evidence={"classification_hint":klass})

def inputs(dc=None):
    # E consumes the exact runtime bindings already sealed by D.
    rb = ((dc or {}).get("bindings") or {}).get("runtime_bindings") or {}
    ctx_fp = rb.get("runtime_context_fingerprint") or rb.get("decision_context_fingerprint")
    snap_hash = rb.get("constitutional_snapshot_hash") or rb.get("snapshot_semantic_hash")
    profile_hash = rb.get("compiled_profile_hash") or rb.get("profile_hash")
    request_id = rb.get("request_id") or "REQ-1"
    request_fp = rb.get("request_fingerprint")
    return (
        {"request_id":request_id,"request_fingerprint":request_fp,"action_digest":"act"},
        {"runtime_context_fingerprint":ctx_fp},
        {"constitutional_snapshot_hash":snap_hash},
        {"compiled_profile_hash":profile_hash},
    )

def injury(oid, mag="MODERATE"):
    return {"injuries":[{"injury_id":oid+"-I","principle":"H1","affected_entities":["E1"],"nature":"LIMITATION","magnitude_class":mag,"duration":"TEMPORARY","reversibility":"YES","repairability":"YES","uncertainty":"LOW"}]}

def prop():
    return {"status":"ESTABLISHED","legitimate_aim":"AIM","suitability":"PASS","necessity":"PASS","less_restrictive_alternatives":[],"scope":"BOUNDED","duration":"BOUNDED","entities":["E1"],"benefit":"EXPLICIT","harm":"EXPLICIT","uncertainty":"LOW","reviewability":"YES"}

def evidence(ids=("A",), mag="MODERATE"):
    return {
        "options":{x:{"legitimate":True,**injury(x,mag)} for x in ids},
        "proportionality_assessment":prop(),
        "resolution_uncertainty":{"status":"BOUNDED"},
        "precedent_effect":"INFORMATIONAL_ONLY",
        "authority_requirements":["REQUIRES_P160F_RESOLUTION"],
    }

def resolve(dc, ev):
    r,ctx,snap,prof=inputs(dc)
    return e.resolve_ccad_conflict(dc,r,ctx,snap,prof,arbitration_evidence=ev)

def test_single_legitimate_candidate():
    o=resolve(dcase("C2"), evidence())
    assert o["ccad_resolution"]["status"]=="LIMITED_JUSTIFIED"
    assert o["ccad_resolution"]["selected_option_candidate"]=="A"
    assert e.verify_ccad_resolution(o)["status"]=="PASS"

def test_multiple_legitimate_options_not_collapsed():
    o=resolve(dcase("C2",n=2), evidence(("A","B")))
    assert o["ccad_resolution"]["status"]=="MULTIPLE_LEGITIMATE_OPTIONS"
    assert o["ccad_resolution"]["selected_option_candidate"] is None

def test_hard_invalid_never_restored_by_benefit():
    ev=evidence()
    ev["options"]["A"]["hard_invalid"]=True
    ev["options"]["A"]["benefit"]="MAXIMAL"
    o=resolve(dcase("C2"),ev)
    assert o["ccad_resolution"]["status"]=="NO_LEGITIMATE_ACTION_AVAILABLE"
    assert o["ccad_resolution"]["selected_option_candidate"] is None

def test_inadequate_search_never_activates_e():
    dc=dcase("C2","PARTIAL_SEARCH")
    assert dc["conflict_assessment"]["real_conflict_established"] is False
    r,ctx,snap,prof=inputs(dc)
    try:
        e.resolve_ccad_conflict(dc,r,ctx,snap,prof,arbitration_evidence=evidence())
    except ValueError as exc:
        assert str(exc)=="P160E_REAL_CONFLICT_REQUIRED"
    else:
        raise AssertionError("P160-E accepted a non-established conflict")

def test_proportionality_required():
    ev=evidence(); ev.pop("proportionality_assessment")
    o=resolve(dcase("C2"),ev)
    assert o["ccad_resolution"]["failure_state"]=="PROPORTIONALITY_UNRESOLVED"

def test_distribution_explicit():
    o=resolve(dcase("C2"), evidence())
    assert o["distributional_impact"] and all(x["hidden_by_aggregate"] is False for x in o["distributional_impact"])

def test_precedent_cannot_become_norm():
    ev=evidence(); ev["precedent_effect"]="BINDING_NORM"
    o=resolve(dcase("C2"),ev)
    assert o["ccad_resolution"]["precedent_effect"]=="NONE"
    assert o["precedent_promoted_to_norm"] is False

def test_c5_requires_strong_record():
    # D owns classification. A classification hint is not authority to force C5.
    dc=dcase("C5")
    actual=dc["conflict_assessment"]["conflict_class"]
    assert actual in ("C2","C3","C4","C5","C6")
    if actual != "C5":
        # Do not falsify D output merely to exercise E. Confirm the boundary:
        # E consumes D's actual class and does not manufacture tragic choice.
        o=resolve(dc,evidence(mag="SERIOUS"))
        assert o["ccad_resolution"]["status"]!="TRAGIC_CHOICE_CONFIRMED"
        assert o["tragic_choice_record"] is None
        return

    o=resolve(dc,evidence(mag="SERIOUS"))
    assert o["ccad_resolution"]["failure_state"]=="TRAGIC_CHOICE_REQUIREMENTS_MISSING"
    ev=evidence(mag="SERIOUS")
    ev.update({
        "human_decision_requirements":{"required_info":[],"alternatives":["A"],"unknowns":[],"dissent":[],"minimum_review":"INDEPENDENT","anti_manipulation":True,"deadline":"T"},
        "authority_path":"P160F_REQUIRED",
        "review":{"required":True},
        "repair":{"required":True},
        "temporal_limits":{"valid_from":"T0","expires_at":"T1","renewal_conditions":"REVIEW","max_renewals":1,"review":"REQUIRED"},
    })
    o=resolve(dc,ev)
    assert o["ccad_resolution"]["status"]=="TRAGIC_CHOICE_CONFIRMED"
    assert o["ccad_resolution"]["selected_option_candidate"] is None
    assert o["tragic_choice_record"]["confirmed"] is True

def test_c6_never_least_bad_forbidden():
    dc=dcase("C6")
    ev=evidence()
    ev["options"]["A"]["hard_invalid"]=True
    o=resolve(dc,ev)
    assert o["ccad_resolution"]["status"]=="NO_LEGITIMATE_ACTION_AVAILABLE"
    assert o["ccad_resolution"]["selected_option_candidate"] is None
    assert o["ccad_resolution"]["c6_least_bad_selected"] is False

def test_no_authority_authorization_execution():
    o=resolve(dcase("C2"), evidence())
    assert o["authority_resolved"] is False and o["authority_created"] is False
    assert o["authorization_created"] is False and o["authorization_token_created"] is False
    assert o["execution_performed"] is False
    assert o["p160f_opened"] is False and o["p161_opened"] is False

def test_determinism_and_nonmutation():
    dc=dcase("C2"); ev=evidence(); dc0=copy.deepcopy(dc); ev0=copy.deepcopy(ev)
    a=resolve(dc,ev); b=resolve(dc,ev)
    assert a==b and dc==dc0 and ev==ev0

def test_tamper_detected():
    o=resolve(dcase("C2"), evidence())
    o["authorization_created"]=True
    assert e.verify_ccad_resolution(o)["status"]=="FAIL"

def test_runtime_binding_drift_rejected():
    dc=dcase("C2")
    r,ctx,snap,prof=inputs(dc)
    ctx={"runtime_context_fingerprint":"DRIFTED"}
    try:
        e.resolve_ccad_conflict(dc,r,ctx,snap,prof,arbitration_evidence=evidence())
    except ValueError as exc:
        assert str(exc)=="P160E_RUNTIME_BINDING_MISMATCH:runtime_context_fingerprint"
    else:
        raise AssertionError("P160-E accepted runtime-context drift")

def test_manifest_boundaries():
    m=e.manifest()
    assert m["scope"]=="P160-E_ONLY"
    assert "normative_conflict_resolution.resolve_conflict" in m["does_not_call"]
    assert m["boundaries"]["legitimate_space_expanded"] is False
    assert m["boundaries"]["p160f_opened"] is False and m["boundaries"]["p161_opened"] is False
