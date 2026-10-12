from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.documentary_relation_classifier import DocumentaryRelationClassifier
cases=[
('repose sur','requires'),('généralise','generalizes'),('cas particulier de','specializes'),('contredit','contradicts'),('confirme','supports')]
for phrase,rel in cases:
 r=DocumentaryRelationClassifier().step(inputs={'evidence':[{'evidence_id':rel,'document_id':'A','referenced_document_id':'B','excerpt':f"Ce travail {phrase} B"}]},persist=False)
 assert r['candidate_relations'][0]['relation']==rel
with TemporaryDirectory() as td:
 root=Path(td); r=DocumentaryRelationClassifier(root).step(inputs={'evidence':[{'evidence_id':'e','document_id':'A','referenced_document_id':'B','excerpt':'Ce cadre a été étendu dans B'}]},persist=True)
 assert not (root/'theory_evolution/ay1_d1b/latest/validated_relations.json').exists()
 assert (root/'theory_evolution/ay1_d1b/latest/relation_candidates.json').exists()
print('AY1_D1B_SPECIALIZED_TESTS_OK')
