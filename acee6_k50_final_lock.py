from pathlib import Path
import subprocess, sys
ROOT=Path.home()/"open-cognitive-ecology"
def main():
    prior=ROOT/"acee6_k4_final_lock.py"
    if prior.is_file(): subprocess.run([sys.executable,str(prior)],cwd=ROOT,check=True,timeout=300)
    subprocess.run([sys.executable,str(ROOT/"acee6_k50_fast_acceptance_suite.py")],cwd=ROOT,check=True,timeout=180)
    print("ACEE6_K50_FINAL_LOCK_OK")
if __name__=="__main__": main()
