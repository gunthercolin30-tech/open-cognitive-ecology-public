import subprocess,sys
for f,m in [('acee6_k8_functional_test.py','ACEE6_K8_FUNCTIONAL_OK'),('acee6_k8_tamper_test.py','ACEE6_K8_TAMPER_OK')]:
 p=subprocess.run([sys.executable,f],capture_output=True,text=True,timeout=180);print(p.stdout,end='');assert p.returncode==0,(f,p.stderr);assert m in p.stdout
print('ACEE6_K8_FAST_ACCEPTANCE_OK')
