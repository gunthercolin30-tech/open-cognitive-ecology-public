from acee6_k7_longitudinal_runner import run_reduced
c=run_reduced(False)['report']['comparison'];assert c['decision_drift_count']==0 and c['unexpected_numerical_drift_count']==0,c;print('ACEE6_K7_DECISION_NUMERICAL_OK')
