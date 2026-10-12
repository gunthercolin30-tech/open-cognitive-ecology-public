from acee6_k7_longitudinal_runner import run_reduced
c=run_reduced(False)['report']['comparison'];assert c['restart_drift_count']==0,c;print('ACEE6_K7_RESTART_DRIFT_OK')
