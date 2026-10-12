import hashlib,subprocess,sys
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
TARGET=ROOT/"ontology"/"minimal_dna.py"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    before=sha(TARGET)
    p=subprocess.run([sys.executable,"-m","validation.p016_dna_stack"],cwd=ROOT,text=True,capture_output=True)
    assert p.returncode==0,(p.stdout,p.stderr)
    assert sha(TARGET)==before
    print("P016_NON_MUTATION_TEST_OK")
if __name__=="__main__": main()
