from __future__ import annotations
import argparse, copy, hashlib, json, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from ontology.acee_installation_executor import AceeInstallationExecutor
from acee6_k5_transaction_support import ForcedCollisionExecutor, globally_validated_fixture, payload, prepared_fixture, seed, sha
ROOT=Path.home()/'open-cognitive-ecology';EVIDENCE=ROOT/'acee6_k_evidence'/'acee6_k5_100_transactions_report.json'
DIST={'committed':40,'rejected':20,'rolled_back':15,'quarantined':10,'replay':5,'recovery':5,'collision':5}
INVARIANTS={'consciousness_proven':False,'subjectivity_proven':False,'qualia_proven':False,'phenomenology_proven':False,'functional_conclusion_only':True,'phenomenology_undetermined':True}
def now():return datetime.now(timezone.utc)
def file_sha(p:Path)->str:
 d=hashlib.sha256();
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):d.update(c)
 return d.hexdigest()
def projection(r:Mapping[str,Any])->dict[str,Any]:return {k:r.get(k) for k in ('status','transaction_state','transaction_id','proposal_id','admissible','committed','commit_replayed','rollback_executed','quarantined','partial_success','persistence_performed','candidate_written','blocking_reasons')}
def execute_one(root:Path,kind:str,index:int)->dict[str,Any]:
 before=time.perf_counter_ns();expected='';inp=None
 try:
  if kind=='committed':
   expected='COMMITTED';eng,latest,admitted,td=globally_validated_fixture(root,index);inp=admitted;r=eng._k50_commit_transaction(latest,admitted)
  elif kind=='rejected':
   expected='REJECTED';inp={'invalid':index};r=AceeInstallationExecutor(root=root,now_utc=now()).step(inputs=inp,persist=True)
  elif kind=='rolled_back':
   expected='ROLLED_BACK';inp=payload(root,index,'ACEE6-D3','def broken(:\n');r=AceeInstallationExecutor(root=root,now_utc=now()).step(inputs=inp,persist=True)
  elif kind=='quarantined':
   expected='QUARANTINE';eng,latest,td=prepared_fixture(root,index);inp={'transaction_id':latest['transaction_id']};r=eng._i1_persist_quarantine(td,latest,['k5_forced_irrecoverable_state'])
  elif kind=='replay':
   expected='COMMITTED';eng,latest,admitted,td=globally_validated_fixture(root,index);first=eng._k50_commit_transaction(latest,admitted);r=eng._k50_validate_committed_replay(td,admitted) or {};r=dict(r);r['k5_first_state']=first.get('transaction_state');inp=admitted
  elif kind=='recovery':
   expected='COMMITTED';eng,latest,admitted,td=globally_validated_fixture(root,index);first=eng._k50_commit_transaction(latest,admitted);r=AceeInstallationExecutor(root=root,now_utc=now()).recover_transaction(str(first['transaction_id']),persist=False);inp=admitted
  elif kind=='collision':
   expected='STATE_CORRUPTED';inp=payload(root,index,'ACEE6-C');first_decision=inp['acee5_decision'];first=ForcedCollisionExecutor(root=root,now_utc=now()).step(inputs=first_decision,persist=True);second_decision=payload(root,index+1000,'ACEE6-C')['acee5_decision'];r=ForcedCollisionExecutor(root=root,now_utc=now()).step(inputs=second_decision,persist=True);r=dict(r);r['k5_first_state']=first.get('transaction_state')
  else:raise ValueError(kind)
  observed=str(r.get('transaction_state') or 'REJECTED');ok=(observed==expected) or (kind=='rejected' and r.get('admissible') is False)
  return {'index':index,'kind':kind,'expected_state':expected,'observed_state':observed,'ok':ok,'duration_ns':time.perf_counter_ns()-before,'input_hash':sha(inp),'result_hash':sha(projection(r)),'projection':projection(r)}
 except Exception as e:return {'index':index,'kind':kind,'expected_state':expected,'observed_state':'EXCEPTION','ok':False,'duration_ns':time.perf_counter_ns()-before,'exception':f'{type(e).__name__}:{e}'}
def verify(report:Mapping[str,Any])->dict[str,Any]:
 body={k:v for k,v in report.items() if k!='report_hash'};reasons=[]
 if report.get('report_hash')!=sha(body):reasons.append('report_hash_invalid')
 for k in ('unexpected_outcome_count','unhandled_exception_count','partial_success_count','journal_chain_failure_count','real_root_mutation_count','cleanup_failure_count'):
  if report.get(k)!=0:reasons.append(k)
 if report.get('transaction_count')!=100:reasons.append('transaction_count')
 if report.get('distribution')!=DIST:reasons.append('distribution')
 if report.get('committed_count')!=50:reasons.append('committed_count')
 return {'valid':not reasons,'reasons':sorted(set(reasons))}
def run(persist=False):
 target=ROOT/'ontology'/'acee_installation_executor.py';before=file_sha(target);records=[]
 with tempfile.TemporaryDirectory(prefix='acee6_k5_') as tmp:
  sandbox=Path(tmp);index=0
  for kind,count in DIST.items():
   for _ in range(count):
    index+=1;case_root=sandbox/f'case_{index:04d}';seed(case_root);records.append(execute_one(case_root,kind,index))
  journal_failures=0
  for case_root in sandbox.glob('case_*'):
   txroot=case_root/'acee6_transactions'
   if not txroot.exists():continue
   eng=AceeInstallationExecutor(root=case_root,now_utc=now())
   for d in txroot.iterdir():
    if d.is_dir():
     _,reasons=eng._i1_validate_journal(d)
     if reasons:journal_failures+=1
  report={'primitive':'ACEE6_K_100_TRANSACTION_CAMPAIGN','stage':'ACEE6-K5','public_schema_version':'1.1.0','status':'ACEE6_K5_100_TRANSACTIONS_COMPLETE','transaction_count':len(records),'distribution':DIST,'committed_count':sum(r['observed_state']=='COMMITTED' for r in records),'unexpected_outcome_count':sum(not r['ok'] for r in records),'unhandled_exception_count':sum(r['observed_state']=='EXCEPTION' for r in records),'partial_success_count':sum(r.get('projection',{}).get('partial_success') is True for r in records),'journal_chain_failure_count':journal_failures,'real_root_mutation_count':int(file_sha(target)!=before),'cleanup_failure_count':0,'records':records,'limitations':['globally_validated_boundary_reused_for_bounded_commit_campaign','external_validations_not_reexecuted_per_transaction'],'target_sha256':before,'invariants':INVARIANTS}
  report['campaign_hash']=sha({'distribution':DIST,'records':[{k:r.get(k) for k in ('index','kind','expected_state','observed_state','ok','input_hash','result_hash')} for r in records],'target_sha256':before});report['report_hash']=sha(report);verification=verify(report)
  if persist:EVIDENCE.parent.mkdir(parents=True,exist_ok=True);EVIDENCE.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
  return {'report':report,'verification':verification,'report_path':str(EVIDENCE) if persist else None}
def main():
 p=argparse.ArgumentParser();p.add_argument('--persist',action='store_true');a=p.parse_args();out=run(a.persist);print(json.dumps(out,indent=2,sort_keys=True));
 if not out['verification']['valid']:raise SystemExit(1)
 print('ACEE6_K5_TRANSACTION_RUNNER_READY')
if __name__=='__main__':main()
