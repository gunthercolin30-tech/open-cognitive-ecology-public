from __future__ import annotations
from collections import Counter
from pathlib import Path
from typing import Any,Mapping
from acee6_k6_campaign_support import GENESIS,deterministic_record,sha,transaction_link

def verify_report(report:Mapping[str,Any])->dict[str,Any]:
    reasons=[];records=list(report.get('records') or []);segments=list(report.get('segments') or [])
    body={k:v for k,v in report.items() if k!='report_hash'}
    if report.get('report_hash')!=sha(body):reasons.append('report_hash_invalid')
    previous=GENESIS
    for expected_index,record in enumerate(records,1):
        if record.get('index')!=expected_index:reasons.append('transaction_index_invalid')
        computed=transaction_link(previous,record)
        if record.get('previous_transaction_hash')!=previous or record.get('transaction_hash')!=computed:reasons.append('transaction_chain_invalid')
        previous=computed
    if previous!=report.get('transaction_chain_hash'):reasons.append('transaction_chain_terminal_invalid')
    previous_segment=GENESIS;covered=[]
    for expected_id,segment in enumerate(segments,1):
        if segment.get('segment_id')!=expected_id:reasons.append('segment_order_invalid')
        sb={k:v for k,v in segment.items() if k not in ('segment_hash','report_hash')}
        computed=sha(sb)
        if segment.get('previous_segment_hash')!=previous_segment or segment.get('segment_hash')!=computed:reasons.append('segment_chain_invalid')
        if segment.get('report_hash')!=sha({k:v for k,v in segment.items() if k!='report_hash'}):reasons.append('segment_report_hash_invalid')
        covered.extend(range(int(segment.get('start_index',0)),int(segment.get('end_index',-1))+1));previous_segment=computed
    if previous_segment!=report.get('segment_chain_hash'):reasons.append('segment_chain_terminal_invalid')
    expected=list(range(1,len(records)+1))
    if covered!=expected:reasons.append('segment_coverage_invalid')
    if report.get('transaction_count')!=len(records):reasons.append('transaction_count_invalid')
    if report.get('segment_count')!=len(segments):reasons.append('segment_count_invalid')
    counts=dict(Counter(r.get('kind') for r in records))
    if counts!=report.get('distribution'):reasons.append('distribution_invalid')
    if any(not r.get('ok') for r in records):reasons.append('unexpected_outcome')
    if report.get('campaign_hash')!=sha({'campaign_id':report.get('campaign_id'),'seed':report.get('seed'),'target_sha256':report.get('target_sha256'),'transaction_chain_hash':report.get('transaction_chain_hash'),'segment_chain_hash':report.get('segment_chain_hash'),'distribution':report.get('distribution')}):reasons.append('campaign_hash_invalid')
    for key in ('unexpected_outcome_count','unhandled_exception_count','partial_success_count','transaction_chain_failure_count','segment_chain_failure_count','checkpoint_chain_failure_count','campaign_chain_failure_count','journal_chain_failure_count','real_root_mutation_count','cleanup_failure_count','restart_duplicate_count','restart_omission_count','checkpoint_recovery_failure_count','segment_replay_divergence_count'):
        if report.get(key)!=0:reasons.append(key)
    if report.get('invariants',{}).get('functional_conclusion_only') is not True:reasons.append('functional_guard_missing')
    return {'valid':not reasons,'reasons':sorted(set(reasons))}
