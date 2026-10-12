import tempfile,time,tracemalloc
from pathlib import Path
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate,_canonical,_sha
def rec(i,p):
 v={'primitive':'ACEE_GOVERNED_CODE_GENERATION_GATE','public_schema_version':'1.2.0','timestamp_utc':'2026-07-15T08:00:00Z','proposal_id':f'p{i}','decision_index':i,'status':'ACEE_CODE_GENERATION_BLOCKED','generation_governed':False,'installation_authorized':False,'authorization_scope':'none','preconditions_complete':False,'blocking_reasons':['x'],'warnings':[],'installation_manifest':None,'previous_decision_hash':p,'history_corrupted':False};v['result_hash']=_sha(v);return v
def run(root,n):
 g=AceeGovernedCodeGenerationGate(root=root);_,h,_=g._paths();h.parent.mkdir(parents=True,exist_ok=True);p=None
 with h.open('w') as f:
  for i in range(n):v=rec(i,p);f.write(_canonical(v)+'\n');p=v['result_hash']
 tracemalloc.start();s=time.perf_counter();r,c,e=g._load_history(h);t=time.perf_counter()-s;_,peak=tracemalloc.get_traced_memory();tracemalloc.stop();assert not c and len(r)==n;return t,peak
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);a=run(root,100);b=run(root,1000);c=run(root,10000);assert c[0]<20 and c[1]<256*1024*1024 and c[0]<max(.5,b[0]*25)
print('ACEE5_HISTORY_SCALABILITY_OK')
