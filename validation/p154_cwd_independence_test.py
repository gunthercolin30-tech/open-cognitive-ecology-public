from pathlib import Path
import subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as d:
 cp=subprocess.run([sys.executable,str(ROOT/"validation/p154_functional_test.py")],cwd=d,capture_output=True,text=True)
 assert cp.returncode==0,(cp.stdout,cp.stderr)
print("P154_CWD_INDEPENDENCE_OK")
