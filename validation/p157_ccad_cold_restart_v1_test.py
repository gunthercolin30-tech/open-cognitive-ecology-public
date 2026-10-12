from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/"ontology/ccad_adversarial_crown.py"
BASE=ROOT/"ontology/ccad/adversarial"; FIX=BASE/"fixtures"
MATRIX=BASE/"ccad_adv_36_matrix.json"; CORPUS=BASE/"counterexample_corpus.json"
ADV=ROOT/"validation/p157_ccad_adv_36_v1_test.py"
MUT=ROOT/"validation/p157_ccad_meta_mutation_v1_test.py"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(v,n): assert v,n; print(n)
def run_fresh(script):
    return subprocess.run([sys.executable,"-I",str(script)],cwd=str(ROOT),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
def snapshot():
    ps=[MOD,MATRIX,CORPUS,ADV,MUT]+sorted(FIX.glob('a*.json'))
    return {str(p.relative_to(ROOT)):sha(p) for p in ps}
def main():
    before=snapshot()
    r1=run_fresh(ADV)
    check(r1.returncode==0 and "P157_ADV36_36_OF_36_OK" in r1.stdout and "P157_CCAD_ADV_36_V1_OK" in r1.stdout,"P157_COLD_FRESH_ADV36_OK")
    mid=snapshot()
    check(before==mid,"P157_COLD_FRESH_NONMUTATION_OK")
    r2=run_fresh(MUT)
    check(r2.returncode==0 and "P157_META_MUTATION_SCORE_6_OF_6_OK" in r2.stdout and "P157_CCAD_META_MUTATION_V1_OK" in r2.stdout,"P157_COLD_FRESH_META_MUTATION_OK")
    after_mut=snapshot()
    check(before==after_mut,"P157_COLD_META_NONMUTATION_OK")
    r3=run_fresh(ADV)
    check(r3.returncode==0 and r3.stdout==r1.stdout,"P157_RESTART_ADV36_REPRODUCIBLE_OK")
    r4=run_fresh(MUT)
    check(r4.returncode==0 and r4.stdout==r2.stdout,"P157_RESTART_META_REPRODUCIBLE_OK")
    final=snapshot()
    check(before==final,"P157_RESTART_PROTECTED_HASHES_STABLE_OK")
    m=json.loads(MATRIX.read_text())
    check(m["p158_opened"] is False,"P157_RESTART_P158_NOT_OPENED_OK")
    print("P157_CCAD_COLD_RESTART_V1_OK")
if __name__=="__main__": main()
