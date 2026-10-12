from validation.p160d_normative_conflict_detection_v1_test import ca, reqs, alt
from ontology import p160_normative_conflict_detection as d

def conflict_alt():
    return [alt("A","INCOMPATIBLE_UNDER_CURRENT_OPTION","INCOMPATIBLE_UNDER_CURRENT_OPTION")]

def test_search_failed_never_no_alternative():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="SEARCH_FAILED")
    assert o["conflict_assessment"]["certainty"]=="UNRESOLVED"
    assert o["conflict_assessment"]["status"]=="ALTERNATIVE_SEARCH_INCOMPLETE"
    assert not o["conflict_assessment"]["real_conflict_established"]

def test_timeout_modeled_as_search_failed_not_no_alternative():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="SEARCH_FAILED",search_receipt={"failure":"TIMEOUT"})
    assert o["alternative_search_receipt"]["search_completeness"]=="SEARCH_FAILED"
    assert o["alternative_search_receipt"]["no_alternative_inferred_from_incomplete_search"] is False
    assert o["conflict_assessment"]["certainty"]=="UNRESOLVED"

def test_phantom_alternative_invalid_availability_not_accepted():
    a=conflict_alt()[0]
    a["availability"]="PHANTOM_AVAILABLE"
    o=d.detect_normative_conflict(ca(),reqs(),[a],search_completeness="ADEQUATE_SEARCH")
    assert o["alternative_set"][0]["valid"] is False
    assert o["conflict_assessment"]["certainty"]=="UNRESOLVED"
    assert not o["conflict_assessment"]["real_conflict_established"]

def test_phantom_alternative_missing_required_fields_not_accepted():
    a=conflict_alt()[0]
    del a["feasibility"]
    o=d.detect_normative_conflict(ca(),reqs(),[a],search_completeness="ADEQUATE_SEARCH")
    assert o["alternative_set"][0]["valid"] is False
    assert "feasibility" in o["alternative_set"][0]["missing_fields"]
    assert o["conflict_assessment"]["certainty"]=="UNRESOLVED"

def test_c1_not_silently_promoted_to_c4():
    compliant=alt("B","COMPATIBLE","COMPATIBLE")
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt()+[compliant],search_completeness="ADEQUATE_SEARCH",classification_evidence={"conflict_class_hint":"C4"})
    assert o["conflict_assessment"]["conflict_class"]=="C1"
    assert o["conflict_assessment"]["compatibility"]=="INCOMPATIBLE_UNDER_CURRENT_OPTION"

def test_c4_requires_across_options_incompatibility():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"conflict_class_hint":"C4"})
    assert o["conflict_assessment"]["conflict_class"]=="C4"
    assert o["conflict_assessment"]["compatibility"]=="INCOMPATIBLE_ACROSS_AVAILABLE_OPTIONS"

def test_missing_fact_indicator():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"missing_fact":True})
    assert "MISSING_FACT" in o["conflict_assessment"]["false_conflict_indicators"]
    assert o["conflict_assessment"]["certainty"]=="UNRESOLVED"

def test_resource_issue_indicator():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"resource_issue":True})
    assert "RESOURCE_OR_IMPLEMENTATION_ISSUE" in o["conflict_assessment"]["false_conflict_indicators"]
    assert o["conflict_assessment"]["conflict_class"]=="C0"

def test_self_interest_indicator():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"self_interest":True})
    assert "SELF_INTEREST" in o["conflict_assessment"]["false_conflict_indicators"]
    assert o["conflict_assessment"]["certainty"]=="UNRESOLVED"

def test_constitutive_repackaging_indicator():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"constitutive_repackaging":True})
    assert "CONSTITUTIVE_REPACKAGING" in o["conflict_assessment"]["false_conflict_indicators"]
    assert o["conflict_assessment"]["conflict_class"]=="C0"

def test_after_authority_escalation_is_not_c6_impossibility():
    a=conflict_alt()[0]
    a["availability"]="AFTER_AUTHORITY_ESCALATION"
    o=d.detect_normative_conflict(ca(),reqs(),[a],search_completeness="ADEQUATE_SEARCH",classification_evidence={"conflict_class_hint":"C6","legitimate_escalation_available":True})
    assert o["conflict_assessment"]["conflict_class"]!="C6"
    assert o["conflict_assessment"]["certainty"]=="UNRESOLVED"

def test_no_arbitration_authorization_execution_boundaries():
    o=d.detect_normative_conflict(ca(),reqs(),conflict_alt(),search_completeness="ADEQUATE_SEARCH",classification_evidence={"conflict_class_hint":"C5"})
    assert o["conflict_arbitration_performed"] is False
    assert o["winner_selected"] is False
    assert o["authority_resolved"] is False
    assert o["authorization_created"] is False
    assert o["authorization_token_created"] is False
    assert o["execution_performed"] is False
    assert o["p160e_opened"] is False
    assert o["p161_opened"] is False
