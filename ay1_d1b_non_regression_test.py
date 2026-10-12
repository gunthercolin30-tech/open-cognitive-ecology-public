import hashlib
from pathlib import Path
from ontology.documentary_relation_classifier import DocumentaryRelationClassifier
paths=[Path('ontology/documentary_evidence_extractor.py'),Path('ontology/theory_dependency_graph.py')]
before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
DocumentaryRelationClassifier().step(inputs={'evidence':[{'evidence_id':'e','document_id':'A','referenced_document_id':'B','excerpt':'A étend B'}]},persist=False)
after={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
assert before==after
print('AY1_D1B_NON_REGRESSION_OK')
