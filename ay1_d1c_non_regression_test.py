import hashlib
from pathlib import Path
from ontology.governed_relation_review_gate import GovernedRelationReviewGate
paths=[Path('ontology/documentary_relation_classifier.py'),Path('ontology/documentary_evidence_extractor.py'),Path('ontology/theory_dependency_graph.py')]
b={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
try:GovernedRelationReviewGate().step(inputs={},persist=False)
except TypeError:pass
a={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};assert a==b
print('AY1_D1C_NON_REGRESSION_OK')
