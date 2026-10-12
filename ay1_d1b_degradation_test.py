from ontology.documentary_relation_classifier import DocumentaryRelationClassifier
r=DocumentaryRelationClassifier().step(inputs={'evidence':[]},persist=False)
assert r['status']=='DOCUMENTARY_RELATION_CLASSIFICATION_DEGRADED'
r=DocumentaryRelationClassifier().step(inputs={'evidence':[{'evidence_id':'x','document_id':'A','referenced_document_id':'A','excerpt':'A étend A'}]},persist=False)
assert r['rejected_evidence'][0]['reason']=='self_reference'
print('AY1_D1B_DEGRADATION_OK')
