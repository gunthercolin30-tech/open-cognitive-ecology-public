import subprocess,sys
for name in ['acee6_d1_fast_acceptance_suite.py','acee6_d2_fast_acceptance_suite.py','acee6_d3_fast_acceptance_suite.py','acee6_d3_second_crown_suite.py']:
 r=subprocess.run([sys.executable,name],timeout=120); assert r.returncode==0,name
print('ACEE6_E_NON_REGRESSION_OK')
