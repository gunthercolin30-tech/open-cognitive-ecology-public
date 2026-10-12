from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
from ontology.documentary_relation_classifier import DocumentaryRelationClassifier
ROOT=Path.home()/'open-cognitive-ecology'
base=ROOT/'theory_evolution'/'ay1_d1'/'campaigns'
dirs=sorted([p for p in base.iterdir() if p.is_dir()])
if not dirs: raise FileNotFoundError('No AY1-D1 campaign found')
evidence=json.loads((dirs[-1]/'documentary_evidence.json').read_text(encoding='utf-8'))
engine=DocumentaryRelationClassifier(ROOT)
a=engine.step(inputs={'evidence':evidence},persist=False)
b=engine.step(inputs={'evidence':list(reversed(evidence))},persist=False)
assert a['classification_hash']==b['classification_hash']
cid='ay1-d1b-real-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=ROOT/'theory_evolution'/'ay1_d1b'/'campaigns'/cid
out.mkdir(parents=True,exist_ok=False)
for name,value in [('relation_candidates.json',a['candidate_relations']),('review_queue.json',a['review_queue']),('rejected_evidence.json',a['rejected_evidence']),('classification_manifest.json',a)]:
 (out/name).write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
print('AY1-D1b real classification campaign')
print('- campaign_id:',cid)
print('- status:',a['status'])
print('- candidate_count:',a['candidate_count'])
print('- review_count:',a['review_count'])
print('- rejected_count:',a['rejected_count'])
print('- deterministic_hash: true')
print('AY1_D1B_REAL_CLASSIFICATION_CAMPAIGN_OK')
