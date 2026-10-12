from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.governed_relation_review_gate import GovernedRelationReviewGate,candidate_payload_hash,evidence_payload_hash
from ontology.validated_relation_registry import ValidatedRelationRegistry
c={'candidate_id':'candidate:x','source':'A','target':'B','relation':'requires','confidence':.93,'evidence':['e1'],'requires_review':True,'validated':False,'auto_promotion_forbidden':True,'provenance':'test'};e=[{'evidence_id':'e1','excerpt':'A nécessite B'}]
def decision(kind,did):return {'decision_id':did,'candidate_id':'candidate:x','decision':kind,'reviewer_id':'h','reviewer_role':'scientific_reviewer','rationale':'Explicit governed review.','confirmed_source':'A','confirmed_target':'B','confirmed_relation':'requires','candidate_payload_hash':candidate_payload_hash(c),'evidence_payload_hash':evidence_payload_hash(e)}
for kind in ['approve','reject','request_revision','abstain']:
 r=GovernedRelationReviewGate().step(inputs={'candidate':c,'decision':decision(kind,'d-'+kind),'evidence_records':e});assert r['review_record']['decision']==kind
with TemporaryDirectory() as td:
 g=GovernedRelationReviewGate().step(inputs={'candidate':c,'decision':decision('approve','d1'),'evidence_records':e})
 out=ValidatedRelationRegistry(Path(td)).step(inputs={'gate_result':g},persist=True);assert out['validated_count']==1
 import json
 p=json.loads((Path(td)/'theory_evolution/ay1_d1c/latest/validated_relations.json').read_text());assert p['count']==1
 try:ValidatedRelationRegistry(Path(td)).step(inputs={'gate_result':g},persist=True);raise AssertionError('duplicate accepted')
 except RuntimeError:pass
print('AY1_D1C_SPECIALIZED_TESTS_OK')
