from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for rel in ["validation/p005_functional_test.py","validation/p006_functional_test.py","validation/p151_functional_test.py"]:
 p=ROOT/rel
 if not p.exists(): raise AssertionError("missing "+rel)
 cp=subprocess.run([sys.executable,str(p)],cwd=str(ROOT),capture_output=True,text=True)
 if cp.returncode: raise AssertionError(rel+"\n"+cp.stdout+"\n"+cp.stderr)
print("P154_P005_P006_P151_NON_REGRESSION_OK")
