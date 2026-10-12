from __future__ import annotations
import math
from typing import Any, Mapping
from acee6_k6_campaign_support import INVARIANTS, atomic_json_write, sha

RESOURCE_RATIO_LIMIT = 2.50
PERFORMANCE_RATIO_LIMIT = 2.50
ABSOLUTE_RSS_SLACK = 64 * 1024 * 1024

FUNCTIONAL_REPORT_KEYS = (
    'seed','target_sha256','transaction_count','segment_count','segment_size',
    'distribution','committed_count','transaction_chain_hash','segment_chain_hash',
    'campaign_hash','invariants',
)
RECORD_KEYS = ('index','kind','expected_state','observed_state','ok','projection')
SEGMENT_KEYS = ('segment_id','start_index','end_index','transaction_count')
HASH_KEYS = ('transaction_chain_hash','segment_chain_hash','campaign_hash','report_hash')
NORMALIZED_HASH_KEYS = ('transaction_chain_hash','segment_chain_hash','campaign_hash')

def normalized_projection(value:Any)->Any:
    if isinstance(value,Mapping):
        excluded={'proposal_id','transaction_id','input_hash','result_hash','transaction_hash','previous_transaction_hash','checkpoint_hash','segment_hash','previous_segment_hash','report_hash','campaign_hash','transaction_chain_hash','segment_chain_hash','resource_observations'}
        return {k:normalized_projection(v) for k,v in sorted(value.items()) if k not in excluded}
    if isinstance(value,list):return [normalized_projection(v) for v in value]
    return value

def functional_projection(report:Mapping[str,Any])->dict[str,Any]:
    return {
        'report':normalized_projection({k:report.get(k) for k in FUNCTIONAL_REPORT_KEYS}),
        'records':[normalized_projection({k:r.get(k) for k in RECORD_KEYS}) for r in report.get('records',[])],
        'segments':[normalized_projection({k:s.get(k) for k in SEGMENT_KEYS}) for s in report.get('segments',[])],
    }

def raw_hashes(report:Mapping[str,Any])->dict[str,str]:
    return {key:str(report.get(key) or '') for key in HASH_KEYS}

def normalized_hashes(report:Mapping[str,Any])->dict[str,str]:
    records=[normalized_projection({k:r.get(k) for k in RECORD_KEYS}) for r in report.get('records',[])]
    chain='0'*64
    for record in records:chain=sha({'previous':chain,'record':record})
    size=int(report.get('segment_size') or 1)
    previous='0'*64
    for i in range(0,len(records),size):
        body={'segment_id':i//size+1,'records':records[i:i+size],'previous':previous}
        previous=sha(body)
    campaign=sha({'records_chain':chain,'segment_chain':previous,'distribution':report.get('distribution'),'seed':report.get('seed'),'target_sha256':report.get('target_sha256')})
    return {'transaction_chain_hash':chain,'segment_chain_hash':previous,'campaign_hash':campaign}

def hash_views(report:Mapping[str,Any])->dict[str,dict[str,str]]:
    return {'raw':raw_hashes(report),'normalized':normalized_hashes(report)}

def decision_projection(report:Mapping[str,Any])->list[dict[str,Any]]:
    return [normalized_projection({k:r.get(k) for k in ('index','kind','expected_state','observed_state','ok','projection')}) for r in report.get('records',[])]

def numerical_projection(value:Any,path:str='$')->list[tuple[str,float]]:
    out=[]
    if isinstance(value,bool) or value is None:return out
    if isinstance(value,(int,float)):
        number=float(value)
        if not math.isfinite(number):raise ValueError(f'non_finite:{path}')
        out.append((path,number));return out
    if isinstance(value,Mapping):
        for key in sorted(value):
            if key in {'duration_ns','max_rss_before','max_rss_after','checkpoint_size_bytes','records_size_bytes'}:continue
            out.extend(numerical_projection(value[key],f'{path}.{key}'))
    elif isinstance(value,list):
        for i,item in enumerate(value):out.extend(numerical_projection(item,f'{path}[{i}]'))
    return out

def safe_ratio(value:int|float,baseline:int|float)->float:
    if baseline<=0:return 1.0 if value<=0 else float('inf')
    return float(value)/float(baseline)

def resource_comparison(a:Mapping[str,Any],b:Mapping[str,Any])->dict[str,Any]:
    ra=dict(a.get('resource_observations') or {});rb=dict(b.get('resource_observations') or {})
    size_keys=('checkpoint_size_bytes','records_size_bytes')
    size_ratios={k:safe_ratio(rb.get(k,0),ra.get(k,0)) for k in size_keys}
    rss_a=max(0,int(ra.get('max_rss_after',0))-int(ra.get('max_rss_before',0)))
    rss_b=max(0,int(rb.get('max_rss_after',0))-int(rb.get('max_rss_before',0)))
    rss_ok=rss_b <= max(int(rss_a*RESOURCE_RATIO_LIMIT),rss_a+ABSOLUTE_RSS_SLACK,ABSOLUTE_RSS_SLACK)
    return {'size_ratios':size_ratios,'rss_delta_a':rss_a,'rss_delta_b':rss_b,'rss_ok':rss_ok,'valid':rss_ok and all(v<=RESOURCE_RATIO_LIMIT for v in size_ratios.values())}

def performance_comparison(a:Mapping[str,Any],b:Mapping[str,Any])->dict[str,Any]:
    da=int((a.get('resource_observations') or {}).get('duration_ns',0));db=int((b.get('resource_observations') or {}).get('duration_ns',0));ratio=safe_ratio(db,da)
    return {'duration_ns_a':da,'duration_ns_b':db,'ratio':ratio,'limit':PERFORMANCE_RATIO_LIMIT,'valid':ratio<=PERFORMANCE_RATIO_LIMIT}
