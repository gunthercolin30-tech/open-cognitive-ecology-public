from pathlib import Path
import hashlib
from acee6_k2_fuzz_runner import run
p=Path.home()/"open-cognitive-ecology"/"ontology"/"acee_installation_executor.py"
b=hashlib.sha256(p.read_bytes()).hexdigest(); out=run(62002,8,False,reduce_failures=False); a=hashlib.sha256(p.read_bytes()).hexdigest()
assert b==a and out["verification"]["valid"] and not out["persistence_performed"]
print("ACEE6_K2_NON_REGRESSION_OK")
