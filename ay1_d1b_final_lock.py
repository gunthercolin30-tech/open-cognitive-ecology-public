from ontology.documentary_relation_classifier import DocumentaryRelationClassifier
r=DocumentaryRelationClassifier().step(inputs={'evidence':[{'evidence_id':'e','document_id':'A','referenced_document_id':'B','excerpt':'Ce cadre a été étendu dans B'}]},persist=False)
assert r['candidate_count']==1 and r['candidate_relations'][0]['requires_review'] is True
assert r['validated_relations_written'] is False and r['auto_promotion_performed'] is False
assert r['functional_conclusion_only'] is True and r['phenomenology_undetermined'] is True
print('AY1_D1B_DOCUMENTARY_RELATION_CLASSIFIER_FINAL_LOCK_OK')
