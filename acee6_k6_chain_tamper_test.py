import copy
from acee6_k6_longitudinal_runner import run_reduced
from acee6_k6_report_verifier import verify_report
o=run_reduced(False);r=copy.deepcopy(o['report']);r['records'][3]['kind']='collision';assert not verify_report(r)['valid'];r=copy.deepcopy(o['report']);r['segments']=r['segments'][::-1];assert not verify_report(r)['valid'];r=copy.deepcopy(o['report']);r['segments']=r['segments'][:-1];assert not verify_report(r)['valid'];r=copy.deepcopy(o['report']);r['segments'].append(copy.deepcopy(r['segments'][-1]));assert not verify_report(r)['valid'];print('ACEE6_K6_CHAIN_TAMPER_OK')
