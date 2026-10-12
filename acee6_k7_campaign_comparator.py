from __future__ import annotations
from typing import Any,Mapping
from acee6_k6_report_verifier import verify_report
from acee6_k7_drift_support import decision_projection,functional_projection,normalized_hashes,numerical_projection,performance_comparison,resource_comparison

def compare_campaigns(a:Mapping[str,Any],b:Mapping[str,Any],c:Mapping[str,Any])->dict[str,Any]:
    verifications={'A':verify_report(a),'B':verify_report(b),'C':verify_report(c)}
    normalized={'A':normalized_hashes(a),'B':normalized_hashes(b),'C':normalized_hashes(c)}
    hash_drift=[]
    for name,left,right in (('A_B','A','B'),('A_C','A','C')):
        for key in ('transaction_chain_hash','segment_chain_hash','campaign_hash'):
            if normalized[left].get(key)!=normalized[right].get(key):hash_drift.append(f'{name}:{key}')
        x={'A':a,'B':b,'C':c}[left];y={'A':a,'B':b,'C':c}[right]
        if functional_projection(x)!=functional_projection(y):hash_drift.append(f'{name}:functional_projection')
    decision_drift=[]
    if decision_projection(a)!=decision_projection(b):decision_drift.append('A_B')
    if decision_projection(a)!=decision_projection(c):decision_drift.append('A_C')
    numerical_drift=[]
    try:
        na=numerical_projection(functional_projection(a));nb=numerical_projection(functional_projection(b));nc=numerical_projection(functional_projection(c))
        if na!=nb:numerical_drift.append('A_B')
        if na!=nc:numerical_drift.append('A_C')
    except ValueError as exc:numerical_drift.append(str(exc))
    resources={'A_B':resource_comparison(a,b),'A_C':resource_comparison(a,c)}
    performance={'A_B':performance_comparison(a,b),'A_C':performance_comparison(a,c)}
    restart_drift=[] if functional_projection(a)==functional_projection(c) else ['A_C']
    result={
      'verification_inputs_valid':all(v['valid'] for v in verifications.values()),'input_verifications':verifications,
      'normalized_hashes':normalized,
      'hash_drift_count':len(hash_drift),'hash_drift':hash_drift,
      'decision_drift_count':len(decision_drift),'decision_drift':decision_drift,
      'restart_drift_count':len(restart_drift),'restart_drift':restart_drift,
      'unexpected_numerical_drift_count':len(numerical_drift),'numerical_drift':numerical_drift,
      'resource_drift_threshold_breach_count':sum(not v['valid'] for v in resources.values()),'resource_comparisons':resources,
      'performance_drift_threshold_breach_count':sum(not v['valid'] for v in performance.values()),'performance_comparisons':performance,
    }
    result['valid']=result['verification_inputs_valid'] and all(result[k]==0 for k in ('hash_drift_count','decision_drift_count','restart_drift_count','unexpected_numerical_drift_count','resource_drift_threshold_breach_count','performance_drift_threshold_breach_count'))
    return result
