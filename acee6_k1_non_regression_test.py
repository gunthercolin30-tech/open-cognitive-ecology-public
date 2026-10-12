from pathlib import Path
import hashlib
from acee6_k1_property_runner import run
path=Path.home()/"open-cognitive-ecology"/"ontology"/"acee_installation_executor.py"
before=hashlib.sha256(path.read_bytes()).hexdigest(); result=run(limit=64,persist=False); after=hashlib.sha256(path.read_bytes()).hexdigest()
assert before==after and result["verification"]["valid"] and not result["persistence_performed"]
print("ACEE6_K1_NON_REGRESSION_OK")
