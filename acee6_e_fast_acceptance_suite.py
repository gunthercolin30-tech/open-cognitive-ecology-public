import subprocess,sys
for name in ['acee6_e_functional_test.py','acee6_e_idempotence_test.py','acee6_e_cycle_rollback_test.py']:
 r=subprocess.run([sys.executable,name],timeout=120); assert r.returncode==0,name
print('ACEE6_E_FAST_ACCEPTANCE_OK')
