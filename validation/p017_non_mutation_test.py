import hashlib,subprocess,sys
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
TARGETS=(ROOT/"ontology"/"minimal_dna.py",ROOT/"ontology"/"dna_stack.py")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    before={str(p):sha(p) for p in TARGETS}
    proc=subprocess.run([sys.executable,"-m","validation.p017_dna_registry"],cwd=ROOT,text=True,capture_output=True)
    assert proc.returncode==0,(proc.stdout,proc.stderr)
    assert {str(p):sha(p) for p in TARGETS}==before
    print("P017_NON_MUTATION_TEST_OK")
if __name__=="__main__": main()
