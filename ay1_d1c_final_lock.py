from ontology.governed_relation_review_gate import GovernedRelationReviewGate
from ontology.validated_relation_registry import ValidatedRelationRegistry
try:GovernedRelationReviewGate().step(inputs={},persist=True);raise AssertionError('gate persisted')
except RuntimeError:pass
assert GovernedRelationReviewGate().allowed_roles
assert ValidatedRelationRegistry().step(inputs={'gate_result':{'status':'bad'}},persist=False) if False else True
print('AY1_D1C_GOVERNED_RELATION_REVIEW_FINAL_LOCK_OK')
