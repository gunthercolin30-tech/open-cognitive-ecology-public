import copy
from acee6_k7_longitudinal_runner import run_reduced
from acee6_k7_report_verifier import verify_k7_report
r=copy.deepcopy(run_reduced(False)['report']);r['comparison']['hash_drift_count']=1;assert not verify_k7_report(r)['valid']
r=copy.deepcopy(run_reduced(False)['report']);r['campaigns']['B']['normalized_hashes']['campaign_hash']='0'*64;assert not verify_k7_report(r)['valid']
print('ACEE6_K7_TAMPER_OK')
