import subprocess,sys
for n in ["acee6_d3_fast_acceptance_suite.py","acee6_d3_second_crown_suite.py","acee6_e_fast_acceptance_suite.py","acee6_e_five_priorities_suite.py"]:
 r=subprocess.run([sys.executable,n],timeout=180);assert r.returncode==0,n
print("ACEE6_F1_NON_REGRESSION_OK")
