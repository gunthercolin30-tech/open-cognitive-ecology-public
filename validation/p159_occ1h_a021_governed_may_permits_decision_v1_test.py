from ontology.occ1h_a021_governed_may_permits_decision import evaluate
def test_identity():
 r=evaluate(); assert r['decision']['source_modality']=='MAY' and r['decision']['canonical_nir_representation']=='PERMITS'
def test_non_escalation():
 s=evaluate()['decision']['semantic_contract']; assert s['preserves_permissive_character'] and not any((s['is_must'],s['is_must_not'],s['is_recommendation'],s['is_preference'],s['is_execution_authorization'],s['is_activation_authorization']))
def test_governance():
 r=evaluate(); assert r['authority_holder']=='OCE-HUMAN-INITIAL-001' and r['decision']['semantic_contract']['ambiguity_policy']=='FAIL_CLOSED'
def test_boundary():
 r=evaluate(); assert r['rrp21']=='AUTHORIZED_FOR_BOUNDED_REMEDIATION_EXPERIMENT' and r['rrp22']=='REQUIRED_INDEPENDENTLY' and not r['builder_change_performed'] and not r['p160_opened']
