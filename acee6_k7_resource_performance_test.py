from acee6_k7_longitudinal_runner import run_reduced
c=run_reduced(False)['report']['comparison'];assert c['resource_drift_threshold_breach_count']==0 and c['performance_drift_threshold_breach_count']==0,c;print('ACEE6_K7_RESOURCE_PERFORMANCE_OK')
