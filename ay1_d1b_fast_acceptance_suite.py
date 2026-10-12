from ontology.documentary_relation_classifier import DocumentaryRelationClassifier
E=[
{'evidence_id':'e1','document_id':'A','referenced_document_id':'B','excerpt':'Ce cadre a été étendu dans B.'},
{'evidence_id':'e2','document_id':'A','referenced_document_id':'C','excerpt':'Gunther, C. (2026). C. Zenodo. DOI: 10.x'},
]
r=DocumentaryRelationClassifier().step(inputs={'evidence':E},persist=False)
assert r['candidate_count']==1 and r['candidate_relations'][0]['relation']=='extends'
assert r['rejected_count']==1 and not r['validated_relations_written'] and not r['auto_promotion_performed']
print('AY1_D1B_FAST_ACCEPTANCE_ALL_OK')
