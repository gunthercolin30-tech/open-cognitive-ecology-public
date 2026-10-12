from acee6_k5_transaction_runner import DIST,verify,sha
r={'transaction_count':100,'distribution':DIST,'committed_count':50,'unexpected_outcome_count':1,'unhandled_exception_count':0,'partial_success_count':0,'journal_chain_failure_count':0,'real_root_mutation_count':0,'cleanup_failure_count':0};r['report_hash']=sha(r);assert not verify(r)['valid'];print('ACEE6_K5_DEGRADATION_OK')
