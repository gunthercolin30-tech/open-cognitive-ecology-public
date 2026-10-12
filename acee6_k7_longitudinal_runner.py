from __future__ import annotations
import argparse,json,tempfile
from pathlib import Path
from typing import Any,Mapping
from acee6_k5_transaction_runner import ROOT
from acee6_k6_campaign_support import FAST_DISTRIBUTION,INVARIANTS,SCIENTIFIC_DISTRIBUTION,atomic_json_write,sha
from acee6_k6_longitudinal_runner import PlannedInterruption,run_campaign
from acee6_k7_campaign_comparator import compare_campaigns
from acee6_k7_drift_support import hash_views
from acee6_k7_report_verifier import verify_k7_report

EVIDENCE=ROOT/'acee6_k_evidence'/'acee6_k7_longitudinal_drift_report.json'

def _campaign_summary(report:Mapping[str,Any])->dict[str,Any]:
    views=hash_views(report)
    return {
        'campaign_id':report['campaign_id'],
        'transaction_count':report['transaction_count'],
        'segment_count':report['segment_count'],
        'raw_hashes':views['raw'],
        'normalized_hashes':views['normalized'],
        'resource_observations':report['resource_observations'],
    }

def _run_triplet(*,root:Path,distribution:Mapping[str,int],segment_size:int,seed_value:int,interrupt_at:int)->dict[str,Any]:
    a=run_campaign(workspace=root/'A',distribution=distribution,segment_size=segment_size,seed_value=seed_value)['report']
    b=run_campaign(workspace=root/'B',distribution=distribution,segment_size=segment_size,seed_value=seed_value)['report']
    try:run_campaign(workspace=root/'C',distribution=distribution,segment_size=segment_size,seed_value=seed_value,interrupt_at=interrupt_at,interrupt_phase='after_checkpoint')
    except PlannedInterruption:pass
    c=run_campaign(workspace=root/'C',distribution=distribution,segment_size=segment_size,seed_value=seed_value,resume=True)['report']
    comparison=compare_campaigns(a,b,c)
    campaigns={name:_campaign_summary(r) for name,r in {'A':a,'B':b,'C':c}.items()}
    report={'primitive':'ACEE6_K7_LONGITUDINAL_DRIFT_VALIDATION','stage':'ACEE6-K7','public_schema_version':'1.1.0','status':'ACEE6_K7_DRIFT_VALIDATION_COMPLETE','campaigns':campaigns,'comparison':comparison,'invariants':INVARIANTS}
    report['report_hash']=sha(report);return {'report':report,'verification':verify_k7_report(report)}

def run_reduced(persist:bool=False)->dict[str,Any]:
    with tempfile.TemporaryDirectory(prefix='acee6_k7_fast_') as tmp:out=_run_triplet(root=Path(tmp),distribution=FAST_DISTRIBUTION,segment_size=10,seed_value=6006,interrupt_at=7)
    if persist:atomic_json_write(EVIDENCE,out['report'])
    return out

def run_scientific(persist:bool=False)->dict[str,Any]:
    with tempfile.TemporaryDirectory(prefix='acee6_k7_scientific_') as tmp:out=_run_triplet(root=Path(tmp),distribution=SCIENTIFIC_DISTRIBUTION,segment_size=100,seed_value=6006,interrupt_at=537)
    if persist:atomic_json_write(EVIDENCE,out['report'])
    return out

def main()->None:
    p=argparse.ArgumentParser();p.add_argument('--scientific',action='store_true');p.add_argument('--persist',action='store_true');a=p.parse_args();out=run_scientific(a.persist) if a.scientific else run_reduced(a.persist);print(json.dumps(out,indent=2,sort_keys=True));
    if not out['verification']['valid']:raise SystemExit(1)
    print('ACEE6_K7_LONGITUDINAL_RUNNER_READY')
if __name__=='__main__':main()
