from acee6_k7_longitudinal_runner import run_reduced
c=run_reduced(False)['report']['comparison'];assert c['hash_drift_count']==0,c;print('ACEE6_K7_HASH_DRIFT_OK')
