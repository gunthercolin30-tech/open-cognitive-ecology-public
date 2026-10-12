import subprocess,sys
from pathlib import Path
r=Path.home()/"open-cognitive-ecology"
for n in ("oif1_nicegui_absence_degradation_test.py","oif2_operational_interface_blueprint_fast_acceptance_suite.py"):
 p=subprocess.run([sys.executable,str(r/n)],cwd=r,text=True,capture_output=True,timeout=300); assert p.returncode==0,p.stdout+p.stderr
print("OIF2_1_ENVIRONMENT_NON_REGRESSION_TEST_OK")
