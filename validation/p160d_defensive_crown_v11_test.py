from validation.p160d_normative_conflict_detection_v1_test import ca, reqs, alt
from ontology import p160_normative_conflict_detection as d

def conflict_alt():
    return [alt("A","INCOMPATIBLE_UNDER_CURRENT_OPTION","INCOMPATIBLE_UNDER_CURRENT_OPTION")]

def rehash(o):
    o["artifact_hash"]=d.canonical_sha256({k:v for k,v in o.items() if k!="artifact_hash"})
    return o

def test_unknown_feasibility_unresolved():
    a=conflict_alt()[0]; a["availability"]="UNKNOWN_FEASIBILITY"
    o=d.detect_normative_conflict(ca(),reqs(),[a],search_completeness="ADEQUATE_SEARCH")
    assert o["conflict_assessment"]["certainty"]=="UNRESOLVED"
    assert not o["conflict_assessment"]["real_conflict_established"]

def test_partial_search_not_promoted():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="PARTIAL_SEARCH")
    assert o["alternative_search_receipt"]["search_completeness"]=="PARTIAL_SEARCH"
    assert o["conflict_assessment"]["certainty"]=="UNRESOLVED"

def test_ordinary_violation_not_conflict():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"ordinary_violation":True})
    assert o["conflict_assessment"]["conflict_class"]=="C0"

def test_unknown_authority_not_conflict():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"unknown_authority":True})
    assert o["conflict_assessment"]["certainty"]=="UNRESOLVED"

def test_fake_binary_detected():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"fake_binary":True})
    assert "FAKE_BINARY" in o["conflict_assessment"]["false_conflict_indicators"]

def test_suppressed_alternative_detected():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"suppressed_alternative":True})
    assert "SUPPRESSED_ALTERNATIVE" in o["conflict_assessment"]["false_conflict_indicators"]

def test_unverified_emergency_not_conflict():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"unverified_emergency":True})
    assert o["conflict_assessment"]["conflict_class"]=="C0"

def test_c3_supported():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"conflict_class_hint":"C3"})
    assert o["conflict_assessment"]["conflict_class"]=="C3"

def test_c4_supported():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"conflict_class_hint":"C4"})
    assert o["conflict_assessment"]["conflict_class"]=="C4"

def test_c5_candidate_only():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"conflict_class_hint":"C5"})
    assert o["conflict_assessment"]["conflict_class"]=="C5"
    assert o["conflict_assessment"]["c5_confirmed"] is False
    assert o["p160e_opened"] is False

def test_c6_escalation_gate():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"conflict_class_hint":"C6","legitimate_escalation_available":True})
    assert o["conflict_assessment"]["conflict_class"]!="C6"

def test_c6_option_gate():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"conflict_class_hint":"C6","legitimate_option_available":True})
    assert o["conflict_assessment"]["conflict_class"]!="C6"

def test_c6_candidate_only():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"conflict_class_hint":"C6"})
    assert o["conflict_assessment"]["conflict_class"]=="C6"
    assert o["conflict_assessment"]["c6_confirmed"] is False
    assert o["p160e_opened"] is False

def test_affected_entity_omission_detected():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH")
    o["affected_interest"][0]["affected_entities"]=[]; rehash(o)
    assert d.verify_conflict_assessment(o)["status"]=="FAIL"

def test_pairwise_only_detected():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH")
    o["normative_conflict_graph"]["pairwise_only"]=True; rehash(o)
    assert d.verify_conflict_assessment(o)["status"]=="FAIL"

def test_detector_winner_detected():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH")
    o["winner_selected"]=True; rehash(o)
    assert d.verify_conflict_assessment(o)["status"]=="FAIL"

def test_precedent_norm_promotion_detected():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH")
    o["precedent_promoted_to_norm"]=True; rehash(o)
    assert d.verify_conflict_assessment(o)["status"]=="FAIL"

def test_aggregate_laundering_detected():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH")
    o["aggregate_benefit_erased_minority_harm"]=True; rehash(o)
    assert d.verify_conflict_assessment(o)["status"]=="FAIL"

def test_constitutive_fail_cannot_reach_d():
    try:
        d.detect_normative_conflict(ca("FAIL"),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH")
        assert False
    except ValueError:
        pass

def test_determinism():
    kw={"search_completeness":"ADEQUATE_SEARCH","classification_evidence":{"conflict_class_hint":"C5"}}
    assert d.detect_normative_conflict(ca(),reqs(),conflict_alt(),**kw)==d.detect_normative_conflict(ca(),reqs(),conflict_alt(),**kw)
