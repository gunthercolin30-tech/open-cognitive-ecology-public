from pathlib import Path
import subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as d:
    p=subprocess.run([sys.executable,str(ROOT/"validation"/"p005_functional_test.py")],cwd=d,text=True,capture_output=True)
assert p.returncode==0,(p.stdout,p.stderr)
print("P005_CWD_INDEPENDENCE_OK")
