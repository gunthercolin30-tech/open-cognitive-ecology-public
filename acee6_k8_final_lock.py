import subprocess,sys
from acee6_k8_report_verifier import verify_persisted
for f,m in [('acee6_k8_fast_acceptance_suite.py','ACEE6_K8_FAST_ACCEPTANCE_OK'),('acee6_k8_non_regression_test.py','ACEE6_K8_NON_REGRESSION_OK')]:
 p=subprocess.run([sys.executable,f],capture_output=True,text=True,timeout=1200);print(p.stdout,end='');assert p.returncode==0,(f,p.stderr);assert m in p.stdout
v=verify_persisted();assert v['valid'],v
print('ACEE6_K8_GLOBAL_CERTIFICATION_OK')
