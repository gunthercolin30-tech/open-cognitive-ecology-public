import json
from acee6_k8_global_certifier import certify
x=certify(True);print(json.dumps(x,indent=2,sort_keys=True));print('ACEE6_K8_CERTIFICATION_READY');raise SystemExit(0 if x['verification']['valid'] else 1)
