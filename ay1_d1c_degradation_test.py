from ontology.governed_relation_review_gate import GovernedRelationReviewGate,candidate_payload_hash,evidence_payload_hash
c={'candidate_id':'candidate:x','source':'A','target':'B','relation':'extends','confidence':.9,'evidence':['e1'],'requires_review':True,'validated':False,'auto_promotion_forbidden':True};e=[{'evidence_id':'e1'}]
base={'decision_id':'d','candidate_id':'candidate:x','decision':'approve','reviewer_id':'h','reviewer_role':'scientific_reviewer','rationale':'ok','confirmed_source':'A','confirmed_target':'B','confirmed_relation':'extends','candidate_payload_hash':candidate_payload_hash(c),'evidence_payload_hash':evidence_payload_hash(e)}
for mutation in ({'reviewer_role':'unauthorized'},{'rationale':''},{'confirmed_target':'C'},{'candidate_payload_hash':'bad'}):
 d=dict(base);d.update(mutation)
 try:GovernedRelationReviewGate().step(inputs={'candidate':c,'decision':d,'evidence_records':e});raise AssertionError('unsafe decision accepted')
 except (ValueError,PermissionError):pass
print('AY1_D1C_DEGRADATION_OK')
