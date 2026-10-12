import hashlib
from acee6_k3_mutation_runner import run,TARGET
b=hashlib.sha256(TARGET.read_bytes()).hexdigest(); r=run(limit=3); a=hashlib.sha256(TARGET.read_bytes()).hexdigest(); assert a==b and r["report"]["real_root_mutation_count"]==0
print("ACEE6_K3_NON_REGRESSION_OK")
