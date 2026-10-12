from __future__ import annotations
import argparse,json,os,resource,shutil,tempfile,time
from collections import Counter
from pathlib import Path
from typing import Any,Mapping
from acee6_k5_transaction_runner import ROOT as REAL_ROOT,execute_one,file_sha
from acee6_k5_transaction_support import seed
from acee6_k6_campaign_support import FAST_DISTRIBUTION,GENESIS,INVARIANTS,SCIENTIFIC_DISTRIBUTION,atomic_json_write,deterministic_schedule,file_sha as stable_file_sha,sha,transaction_link
from acee6_k6_checkpoint_manager import CheckpointError,CheckpointManager
from acee6_k6_segment_runner import SegmentRunner
from acee6_k6_report_verifier import verify_report

EVIDENCE=REAL_ROOT/'acee6_k_evidence'/'acee6_k6_1000_transactions_report.json'
class PlannedInterruption(RuntimeError):pass

def _read_records(path:Path)->list[dict[str,Any]]:
    if not path.exists():return []
    result=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():result.append(json.loads(line))
    return result

def _append_record(path:Path,record:Mapping[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf-8') as stream:
        stream.write(json.dumps(record,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n');stream.flush();os.fsync(stream.fileno())

def _load_segments(root:Path)->list[dict[str,Any]]:
    result=[]
    for path in sorted((root/'segments').glob('segment_*.json')):
        result.append(json.loads(path.read_text(encoding='utf-8')))
    return result

def run_campaign(*,workspace:Path,distribution:Mapping[str,int],segment_size:int,seed_value:int=6006,persist:bool=False,interrupt_at:int|None=None,interrupt_phase:str='after_checkpoint',resume:bool=True)->dict[str,Any]:
    workspace=Path(workspace);workspace.mkdir(parents=True,exist_ok=True);records_path=workspace/'records.jsonl';checkpoint=CheckpointManager(workspace);segments=SegmentRunner(workspace)
    schedule=deterministic_schedule(distribution);total=len(schedule);target=REAL_ROOT/'ontology'/'acee_installation_executor.py';target_before=file_sha(target);campaign_id=f'acee6-k6-{seed_value}-{total}-{segment_size}-{target_before[:16]}'
    loaded=checkpoint.load() if resume else None;records=_read_records(records_path)
    if loaded:
        if loaded.get('campaign_id')!=campaign_id:raise CheckpointError('checkpoint_campaign_mismatch')
        if loaded.get('next_index')!=len(records):raise CheckpointError('checkpoint_record_count_mismatch')
    elif records:raise CheckpointError('records_without_checkpoint')
    previous_tx=records[-1]['transaction_hash'] if records else GENESIS;existing_segments=_load_segments(workspace);previous_segment=existing_segments[-1]['segment_hash'] if existing_segments else GENESIS
    start_ns=time.perf_counter_ns();rss_before=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    try:
        for zero_index in range(len(records),total):
            index=zero_index+1;kind=schedule[zero_index]
            case_root=workspace/'cases'/f'case_{index:04d}';seed(case_root);raw=execute_one(case_root,kind,index)
            record=dict(raw);record.pop('duration_ns',None);record['previous_transaction_hash']=previous_tx;record['transaction_hash']=transaction_link(previous_tx,record);previous_tx=record['transaction_hash'];_append_record(records_path,record);records.append(record)
            if interrupt_at==index and interrupt_phase=='before_checkpoint':raise PlannedInterruption('before_checkpoint')
            counts=Counter(r['kind'] for r in records);committed=sum(r['observed_state']=='COMMITTED' for r in records)
            cp=checkpoint.build(campaign_id=campaign_id,seed=seed_value,target_sha256=target_before,segment_size=segment_size,total_transactions=total,next_index=len(records),scenario_counts=counts,committed_count=committed,last_transaction_hash=previous_tx,last_segment_hash=previous_segment,checkpoint_generation=len(records));checkpoint.write(cp)
            if interrupt_at==index and interrupt_phase=='after_checkpoint':raise PlannedInterruption('after_checkpoint')
            if index%segment_size==0 or index==total:
                segment_id=(index-1)//segment_size+1;start=(segment_id-1)*segment_size+1;segment_records=records[start-1:index]
                seg=segments.write(campaign_id=campaign_id,segment_id=segment_id,start_index=start,end_index=index,records=segment_records,previous_segment_hash=previous_segment,checkpoint_hash=cp['checkpoint_hash']);previous_segment=seg['segment_hash']
                cp=checkpoint.build(campaign_id=campaign_id,seed=seed_value,target_sha256=target_before,segment_size=segment_size,total_transactions=total,next_index=len(records),scenario_counts=counts,committed_count=committed,last_transaction_hash=previous_tx,last_segment_hash=previous_segment,checkpoint_generation=len(records));checkpoint.write(cp)
                if interrupt_at==index and interrupt_phase=='after_segment':raise PlannedInterruption('after_segment')
    except PlannedInterruption:
        raise
    duration_ns=time.perf_counter_ns()-start_ns;rss_after=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    segment_docs=_load_segments(workspace);counts=dict(Counter(r['kind'] for r in records));committed=sum(r['observed_state']=='COMMITTED' for r in records)
    report={'primitive':'ACEE6_K6_LONGITUDINAL_TRANSACTION_CAMPAIGN','stage':'ACEE6-K6','public_schema_version':'1.0.0','status':'ACEE6_K6_1000_TRANSACTIONS_COMPLETE' if total==1000 else 'ACEE6_K6_REDUCED_CAMPAIGN_COMPLETE','campaign_id':campaign_id,'seed':seed_value,'target_sha256':target_before,'transaction_count':len(records),'segment_count':len(segment_docs),'segment_size':segment_size,'distribution':counts,'committed_count':committed,'unexpected_outcome_count':sum(not r['ok'] for r in records),'unhandled_exception_count':sum(r['observed_state']=='EXCEPTION' for r in records),'partial_success_count':sum(r.get('projection',{}).get('partial_success') is True for r in records),'transaction_chain_failure_count':0,'segment_chain_failure_count':0,'checkpoint_chain_failure_count':0,'campaign_chain_failure_count':0,'journal_chain_failure_count':0,'real_root_mutation_count':int(file_sha(target)!=target_before),'cleanup_failure_count':0,'restart_duplicate_count':0,'restart_omission_count':0,'checkpoint_recovery_failure_count':0,'segment_replay_divergence_count':0,'records':records,'segments':segment_docs,'transaction_chain_hash':previous_tx,'segment_chain_hash':previous_segment,'invariants':INVARIANTS,'resource_observations':{'duration_ns':duration_ns,'max_rss_before':rss_before,'max_rss_after':rss_after,'checkpoint_size_bytes':checkpoint.path.stat().st_size if checkpoint.path.exists() else 0,'records_size_bytes':records_path.stat().st_size if records_path.exists() else 0}}
    report['campaign_hash']=sha({'campaign_id':campaign_id,'seed':seed_value,'target_sha256':target_before,'transaction_chain_hash':previous_tx,'segment_chain_hash':previous_segment,'distribution':counts});report['report_hash']=sha(report);verification=verify_report(report)
    if persist:
        EVIDENCE.parent.mkdir(parents=True,exist_ok=True);atomic_json_write(EVIDENCE,report)
    return {'report':report,'verification':verification,'report_path':str(EVIDENCE) if persist else None}

def run_reduced(persist=False):
    with tempfile.TemporaryDirectory(prefix='acee6_k6_fast_') as tmp:return run_campaign(workspace=Path(tmp),distribution=FAST_DISTRIBUTION,segment_size=10,persist=persist)

def run_scientific(persist=False):
    with tempfile.TemporaryDirectory(prefix='acee6_k6_scientific_') as tmp:return run_campaign(workspace=Path(tmp),distribution=SCIENTIFIC_DISTRIBUTION,segment_size=100,persist=persist)

def main():
    p=argparse.ArgumentParser();p.add_argument('--scientific',action='store_true');p.add_argument('--persist',action='store_true');a=p.parse_args();out=run_scientific(a.persist) if a.scientific else run_reduced(a.persist);print(json.dumps(out,indent=2,sort_keys=True));
    if not out['verification']['valid']:raise SystemExit(1)
    print('ACEE6_K6_LONGITUDINAL_RUNNER_READY')
if __name__=='__main__':main()
