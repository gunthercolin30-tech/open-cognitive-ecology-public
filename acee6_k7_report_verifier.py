from __future__ import annotations
import re
from typing import Any,Mapping
from acee6_k6_campaign_support import sha

HEX64=re.compile(r'^[0-9a-f]{64}$')
RAW_KEYS=('transaction_chain_hash','segment_chain_hash','campaign_hash','report_hash')
NORMALIZED_KEYS=('transaction_chain_hash','segment_chain_hash','campaign_hash')

def _valid_hash_map(value:Any,keys:tuple[str,...])->bool:
    return isinstance(value,Mapping) and set(value.keys())==set(keys) and all(isinstance(value[k],str) and HEX64.fullmatch(value[k]) for k in keys)

def verify_k7_report(report:Mapping[str,Any])->dict[str,Any]:
    reasons=[];body={k:v for k,v in report.items() if k!='report_hash'}
    if report.get('report_hash')!=sha(body):reasons.append('report_hash_invalid')
    comparison=report.get('comparison') or {}
    for key in ('hash_drift_count','decision_drift_count','restart_drift_count','unexpected_numerical_drift_count','resource_drift_threshold_breach_count','performance_drift_threshold_breach_count'):
        if comparison.get(key)!=0:reasons.append(key)
    if comparison.get('valid') is not True:reasons.append('comparison_invalid')
    if report.get('invariants',{}).get('functional_conclusion_only') is not True:reasons.append('functional_guard_missing')
    campaigns=report.get('campaigns') or {}
    if sorted(campaigns.keys())!=['A','B','C']:reasons.append('campaign_set_invalid')
    normalized_reference=None
    for name in ('A','B','C'):
        campaign=campaigns.get(name) or {}
        if not _valid_hash_map(campaign.get('raw_hashes'),RAW_KEYS):reasons.append(f'{name}:raw_hashes_invalid')
        if not _valid_hash_map(campaign.get('normalized_hashes'),NORMALIZED_KEYS):reasons.append(f'{name}:normalized_hashes_invalid')
        normalized=campaign.get('normalized_hashes')
        if normalized_reference is None:normalized_reference=normalized
        elif normalized!=normalized_reference:reasons.append(f'{name}:normalized_hash_drift')
    declared=(comparison.get('normalized_hashes') or {})
    for name in ('A','B','C'):
        if declared.get(name)!=(campaigns.get(name) or {}).get('normalized_hashes'):reasons.append(f'{name}:normalized_hash_view_mismatch')
    return {'valid':not reasons,'reasons':sorted(set(reasons))}
