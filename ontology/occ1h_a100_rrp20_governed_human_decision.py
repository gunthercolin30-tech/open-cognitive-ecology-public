from ontology.occ1h_a100_rrpe_normative_authority_gate import authority_gate

D1 = ("Une transition d'un CIS vers une souveraineté permanente n'est admissible que si elle est "
      "explicitement autorisée par le cadre constitutionnel préexistant. En l'absence d'une telle "
      "autorisation explicite, la transition est interdite et demeure fail-closed.")

D2 = ("L'autorisation d'une transition vers une souveraineté permanente doit provenir d'une autorité "
      "constitutionnelle légitime préexistante et indépendante de l'autorité permanente résultante, "
      "selon une chaîne de provenance vérifiable. L'entité, le collectif ou le mécanisme bénéficiant "
      "de la transition ne peut ni créer, ni étendre, ni ratifier lui-même l'autorité nécessaire à "
      "cette transition. Toute autorité absente, ambiguë, circulaire ou non vérifiable entraîne un "
      "refus fail-closed.")

def governed_decision():
    r=authority_gate()
    assert r["rrp20"]=="NEW_NORMATIVE_DECISION_REQUIRED"
    assert r["normative_dof_count"]==2
    return {**r,
      "human_confirmation":"D1_AND_D2_CONFIRMED_AS_FORMULATED",
      "decision_D1":D1,
      "decision_D2":D2,
      "normative_dof_count":2,
      "additional_implicit_normative_dof":False,
      "decision_scope":"A100_CIS_TO_PERMANENT_SOVEREIGNTY_TRANSITION",
      "authority_source":"HUMAN_GOVERNANCE_CONFIRMATION",
      "rrp20_post_decision":"GOVERNED_NORMATIVE_DECISION_RECORDED",
      "rrp21_authorized":True,
      "rrp21_authorization_scope":"IMPLEMENT_D1_D2_ONLY_WITHOUT_SCOPE_BROADENING",
      "self_certification_forbidden":True,
      "rrp22_independent_requalification_required":True,
      "current_verdict":"INCONCLUSIVE",
      "transition_materialized":False,
      "production_runtime_modified":False,
      "criticality_changed":False,
      "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
