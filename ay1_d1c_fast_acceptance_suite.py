from ontology.governed_relation_review_gate import GovernedRelationReviewGate,candidate_payload_hash,evidence_payload_hash
c={'candidate_id':'candidate:x','source':'A','target':'B','relation':'extends','confidence':.94,'evidence':['e1'],'requires_review':True,'validated':False,'auto_promotion_forbidden':True,'provenance':'test'}
e=[{'evidence_id':'e1','excerpt':'A étend B'}]
d={'decision_id':'d1','candidate_id':'candidate:x','decision':'approve','reviewer_id':'human-1','reviewer_role':'scientific_reviewer','rationale':'The excerpt explicitly states extension.','confirmed_source':'A','confirmed_target':'B','confirmed_relation':'extends','candidate_payload_hash':candidate_payload_hash(c),'evidence_payload_hash':evidence_payload_hash(e)}
r=GovernedRelationReviewGate().step(inputs={'candidate':c,'decision':d,'evidence_records':e},persist=False)
assert r['approval_authorized'] is True and r['registry_write_performed'] is False
print('AY1_D1C_FAST_ACCEPTANCE_ALL_OK')
