from pathlib import Path
import hashlib, tempfile
from ontology.acee_installation_executor import AceeInstallationExecutor

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    target=Path.home()/"open-cognitive-ecology"/"ontology"/"acee_installation_executor.py"; before=sha(target)
    with tempfile.TemporaryDirectory() as tmp:
        result=AceeInstallationExecutor(root=Path(tmp)).step(inputs=None,persist=False)
        assert result.get("committed") is not True
    assert sha(target)==before
    print("ACEE6_K50_NON_REGRESSION_OK")
if __name__=="__main__": main()
