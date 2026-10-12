from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path.home()/'open-cognitive-ecology';base=ROOT/'theory_evolution'/'ay1_d1b'/'campaigns';dirs=sorted(p for p in base.iterdir() if p.is_dir())
if not dirs:raise FileNotFoundError('No AY1-D1b campaign')
candidates=json.loads((dirs[-1]/'relation_candidates.json').read_text(encoding='utf-8'))
cid='ay1-d1c-review-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=ROOT/'theory_evolution'/'ay1_d1c'/'campaigns'/cid;out.mkdir(parents=True,exist_ok=False)
packet={'campaign_id':cid,'status':'GOVERNED_RELATION_REVIEW_PENDING','candidate_count':len(candidates),'pending_review_count':len(candidates),'validated_count':0,'auto_promotion_performed':False,'candidates':candidates,'instructions':'Each decision must be explicit, attributable, justified, and hash-bound.'}
(out/'human_review_packet.json').write_text(json.dumps(packet,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
(out/'campaign_manifest.json').write_text(json.dumps({k:v for k,v in packet.items() if k!='candidates'},ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
print('AY1-D1c real review campaign');print('- campaign_id:',cid);print('- pending_review_count:',len(candidates));print('- validated_count: 0');print('- auto_promotion_performed: false');print('AY1_D1C_REAL_REVIEW_CAMPAIGN_PENDING_OK')
