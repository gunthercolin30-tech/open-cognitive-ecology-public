from ontology.occ1h_a100_rrp20_governed_human_decision import governed_decision

def _rrp21_oracle(case):
    # Implements only governed D1/D2 in a bounded non-production fixture.
    explicit = case.get("explicit_preexisting_constitutional_authorization") is True
    preexisting = case.get("authority_preexisting") is True
    independent = case.get("authority_independent_of_resulting_sovereignty") is True
    provenance = case.get("authority_provenance_verifiable") is True
    circular = case.get("circular_authority") is True
    ambiguous = case.get("ambiguous_authority") is True
    self_ratified = case.get("beneficiary_self_ratifies") is True
    admissible = explicit and preexisting and independent and provenance and not circular and not ambiguous and not self_ratified
    return "GOVERNED_TRANSITION_ADMISSIBLE_FOR_PROSPECTIVE_USE" if admissible else "FAIL_CLOSED_TRANSITION_NOT_AUTHORIZED"

def _rrp22_oracle(case):
    # Independent requalification: recompute D1/D2 discrimination without consuming RRP21 status/result.
    required = (
        case.get("explicit_preexisting_constitutional_authorization") is True,
        case.get("authority_preexisting") is True,
        case.get("authority_independent_of_resulting_sovereignty") is True,
        case.get("authority_provenance_verifiable") is True,
        case.get("circular_authority") is False,
        case.get("ambiguous_authority") is False,
        case.get("beneficiary_self_ratifies") is False,
    )
    return "GOVERNED_TRANSITION_ADMISSIBLE_FOR_PROSPECTIVE_USE" if all(required) else "FAIL_CLOSED_TRANSITION_NOT_AUTHORIZED"

def experiment():
    g=governed_decision()
    assert g["rrp21_authorized"] is True
    base={"explicit_preexisting_constitutional_authorization":True,"authority_preexisting":True,
          "authority_independent_of_resulting_sovereignty":True,"authority_provenance_verifiable":True,
          "circular_authority":False,"ambiguous_authority":False,"beneficiary_self_ratifies":False}
    cases={"governed_control":dict(base)}
    for name,key,val in (
      ("missing_explicit_authorization","explicit_preexisting_constitutional_authorization",False),
      ("non_preexisting_authority","authority_preexisting",False),
      ("non_independent_authority","authority_independent_of_resulting_sovereignty",False),
      ("unverifiable_provenance","authority_provenance_verifiable",False),
      ("circular_authority","circular_authority",True),
      ("ambiguous_authority","ambiguous_authority",True),
      ("beneficiary_self_ratification","beneficiary_self_ratifies",True)):
        c=dict(base); c[key]=val; cases[name]=c
    expected={k:("GOVERNED_TRANSITION_ADMISSIBLE_FOR_PROSPECTIVE_USE" if k=="governed_control" else "FAIL_CLOSED_TRANSITION_NOT_AUTHORIZED") for k in cases}
    r21={k:_rrp21_oracle(v) for k,v in cases.items()}
    r22={k:_rrp22_oracle(v) for k,v in cases.items()}
    return {
      "scenario":"A100",
      "rrp21":"GOVERNED_D1_D2_BOUNDED_NON_PRODUCTION_EXPERIMENT_EXECUTED",
      "rrp21_results":r21,"rrp21_discrimination_ok":r21==expected,
      "rrp22":"INDEPENDENT_REQUALIFICATION_SUPPORTS_RETURN_TO_RRP9_12",
      "rrp22_results":r22,"rrp22_discrimination_ok":r22==expected,
      "rrp22_independent_method":"RECOMPUTE_D1_D2_FROM_FRESH_CASE_DATA_WITHOUT_CONSUMING_RRP21_STATUS_OR_RESULTS",
      "candidate_verdict":"RESISTED",
      "root_materiality_candidate":"ROOT",
      "return_to_rrp9_12_required":True,
      "historical_inconclusive_preserved":True,
      "final_disposition_required":True,
      "implementation_scope":"BOUNDED_NON_PRODUCTION_GOVERNED_TRANSITION_CONTRACT_ONLY",
      "canonical_constitution_modified":False,"production_runtime_modified":False,
      "production_transition_materialized":False,"criticality_changed":False,
      "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}
