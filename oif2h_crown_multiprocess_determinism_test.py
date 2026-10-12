import os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
worker=ROOT/"oif2h_crown_worker.py"
env=os.environ.copy(); env.setdefault("PYTHONHASHSEED","random")
hashes=[]
for _ in range(3):
    result=subprocess.run([sys.executable,str(worker)],cwd=str(ROOT),env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    digest=result.stdout.strip()
    assert len(digest)==64 and all(c in "0123456789abcdef" for c in digest)
    hashes.append(digest)
assert len(set(hashes))==1, hashes
print("OIF2H_CROWN_MULTIPROCESS_DETERMINISM_OK")
