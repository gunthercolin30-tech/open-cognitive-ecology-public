import copy,json,tempfile
from pathlib import Path
from acee6_k8_global_certifier import certify,verify_report
x=certify(False)['report'];y=copy.deepcopy(x);y['audit']['criteria']['k0_k7_valid']=False
assert not verify_report(y)['valid']
print('ACEE6_K8_TAMPER_OK')
