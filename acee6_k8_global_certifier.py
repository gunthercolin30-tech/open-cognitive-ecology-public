from __future__ import annotations
import importlib,json,re,zipfile
from pathlib import Path
from typing import Any
from acee6_k8_certification_support import ROOT,EVIDENCE,REPORT_PATH,MANIFEST_PATH,BUNDLE_PATH,atomic_bytes,atomic_json,canonical_bytes,deterministic_zip,file_sha,sha
REPORTS={
 'K0':('acee6_k0_baseline_report.json','acee6_k0_support','verify_report'),
 'K1':('acee6_k1_property_report.json','acee6_k1_property_runner','verify_report'),
 'K2':('acee6_k2_fuzz_report.json','acee6_k2_fuzz_runner','verify_report'),
 'K3':('acee6_k3_mutation_report.json','acee6_k3_mutation_runner','verify'),
 'K4':('acee6_k4_resource_report.json','acee6_k4_resource_runner','verify_report'),
 'K5':('acee6_k5_100_transactions_report.json','acee6_k5_transaction_runner','verify'),
 'K6':('acee6_k6_1000_transactions_report.json','acee6_k6_report_verifier','verify_report'),
 'K7':('acee6_k7_longitudinal_drift_report.json','acee6_k7_report_verifier','verify_k7_report'),}
LOCK_MARKERS={f'K{i}':f'ACEE6_K{i}_FINAL_LOCK_OK' for i in range(8)}
INVARIANTS={'consciousness_proven':False,'subjectivity_proven':False,'qualia_proven':False,'phenomenology_proven':False,'functional_conclusion_only':True,'phenomenology_undetermined':True}
def _load(path:Path)->dict[str,Any]:return json.loads(path.read_text(encoding='utf-8'))
def _valid(v:Any)->bool:return bool(v.get('valid')) if isinstance(v,dict) else bool(v)
def audit()->dict[str,Any]:
 reasons=[];reports={};locks={}
 for stage,(name,module,func) in REPORTS.items():
  path=EVIDENCE/name
  if not path.is_file():reasons.append(f'missing_report:{stage}');continue
  try:
   data=_load(path)
   if stage=='K5':
    body={k:v for k,v in data.items() if k!='report_hash'};rs=[]
    if data.get('report_hash')!=sha(body):rs.append('report_hash_invalid')
    if data.get('transaction_count')!=100:rs.append('transaction_count')
    if data.get('committed_count')!=50:rs.append('committed_count')
    for key in ('unexpected_outcome_count','unhandled_exception_count','partial_success_count','journal_chain_failure_count','real_root_mutation_count','cleanup_failure_count'):
     if data.get(key)!=0:rs.append(key)
    verification={'valid':not rs,'reasons':rs}
   else:verification=getattr(importlib.import_module(module),func)(data)
  except Exception as exc:reasons.append(f'verifier_exception:{stage}:{type(exc).__name__}');continue
  ok=_valid(verification)
  if not ok:reasons.append(f'invalid_report:{stage}')
  reports[stage]={'filename':name,'sha256':file_sha(path),'report_hash':data.get('report_hash'),'verification':verification,'valid':ok,'stage':data.get('stage'),'status':data.get('status')}
 for i in range(8):
  stage=f'K{i}';path=ROOT/f'acee6_k{i}_final_lock.py';marker=LOCK_MARKERS[stage]
  exists=path.is_file();source=path.read_text(encoding='utf-8') if exists else ''
  ok=exists and marker in source
  if not ok:reasons.append(f'invalid_final_lock:{stage}')
  locks[stage]={'filename':path.name,'sha256':file_sha(path) if exists else None,'marker':marker,'valid':ok}
 k3=_load(EVIDENCE/REPORTS['K3'][0]) if (EVIDENCE/REPORTS['K3'][0]).is_file() else {}
 k5=_load(EVIDENCE/REPORTS['K5'][0]) if (EVIDENCE/REPORTS['K5'][0]).is_file() else {}
 k6=_load(EVIDENCE/REPORTS['K6'][0]) if (EVIDENCE/REPORTS['K6'][0]).is_file() else {}
 k7=_load(EVIDENCE/REPORTS['K7'][0]) if (EVIDENCE/REPORTS['K7'][0]).is_file() else {}
 criteria={'k0_k7_valid':len(reports)==8 and all(x['valid'] for x in reports.values()),'mutation_score_at_least_095':float(k3.get('mutation_score',0))>=.95,'transactions_100_valid':k5.get('transaction_count')==100 and k5.get('unexpected_outcome_count')==0,'transactions_1000_valid':k6.get('transaction_count')==1000 and k6.get('segment_count')==10 and k6.get('unexpected_outcome_count')==0,'longitudinal_drift_valid':bool(k7.get('comparison',{}).get('valid')),'all_final_locks_valid':len(locks)==8 and all(x['valid'] for x in locks.values())}
 for key,val in criteria.items():
  if not val:reasons.append(f'criterion_failed:{key}')
 return {'reports':reports,'final_locks':locks,'criteria':criteria,'reasons':reasons,'valid':not reasons}
def certify(persist:bool=True)->dict[str,Any]:
 result=audit();payload={}
 for stage,(name,_,_) in REPORTS.items():
  p=EVIDENCE/name
  if p.is_file():payload[f'evidence/{name}']=p.read_bytes()
 for i in range(8):
  p=ROOT/f'acee6_k{i}_final_lock.py'
  if p.is_file():payload[f'final_locks/{p.name}']=p.read_bytes()
 for name in ('ontology_inventory.txt','dependency_registry.py','ontology_integration_report.txt'):
  p=ROOT/name
  if p.is_file():payload[f'repository/{name}']=p.read_bytes()
 manifest_lines=[f"{sha(payload[n])}  {n}" for n in sorted(payload)]
 manifest=('\n'.join(manifest_lines)+'\n').encode();manifest_hash=sha(manifest)
 report={'primitive':'ACEE6_K8_GLOBAL_CERTIFICATION','stage':'ACEE6-K8','status':'ACEE6_K8_GLOBAL_CERTIFICATION_COMPLETE','public_schema_version':'1.0.0','audit':result,'evidence_manifest_hash':manifest_hash,'evidence_file_count':len(payload),'invariants':INVARIANTS}
 report['report_hash']=sha(report)
 payload['acee6_k8_global_certification_report.json']=json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False).encode()+b'\n'
 payload['sha256_manifest.txt']=manifest
 deterministic_zip(BUNDLE_PATH,payload)
 bundle_verification=verify_bundle(BUNDLE_PATH)
 if persist:
  atomic_json(REPORT_PATH,report);atomic_bytes(MANIFEST_PATH,manifest)
 verification=verify_report(report)
 if not bundle_verification['valid']:
  verification={'valid':False,'reasons':verification['reasons']+bundle_verification['reasons']}
 return {'report':report,'verification':verification,'bundle_verification':bundle_verification,'bundle_sha256':file_sha(BUNDLE_PATH),'report_path':str(REPORT_PATH) if persist else None,'manifest_path':str(MANIFEST_PATH) if persist else None,'bundle_path':str(BUNDLE_PATH) if persist else None}
def verify_bundle(path:Path)->dict[str,Any]:
 reasons=[]
 try:
  with zipfile.ZipFile(path) as z:
   names=z.namelist()
   if names!=sorted(names):reasons.append('bundle_order_not_canonical')
   manifest=z.read('sha256_manifest.txt').decode().splitlines()
   for line in manifest:
    digest,name=line.split('  ',1)
    if sha(z.read(name))!=digest:reasons.append(f'bundle_hash_mismatch:{name}')
 except Exception as exc:reasons.append(f'bundle_exception:{type(exc).__name__}')
 return {'valid':not reasons,'reasons':reasons}
def verify_report(report:dict[str,Any])->dict[str,Any]:
 reasons=[]
 clone=dict(report);stored=clone.pop('report_hash',None)
 if stored!=sha(clone):reasons.append('report_hash_mismatch')
 if report.get('stage')!='ACEE6-K8':reasons.append('stage_invalid')
 if not report.get('audit',{}).get('valid'):reasons.append('audit_invalid')
 if report.get('invariants')!=INVARIANTS:reasons.append('invariants_invalid')
 return {'valid':not reasons,'reasons':reasons}
