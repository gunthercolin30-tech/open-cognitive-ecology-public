import hashlib
from pathlib import Path
from acee6_k5_transaction_runner import run
p=Path.home()/'open-cognitive-ecology'/'ontology'/'acee_installation_executor.py';b=hashlib.sha256(p.read_bytes()).hexdigest();o=run(False);a=hashlib.sha256(p.read_bytes()).hexdigest();assert b==a;assert o['report']['real_root_mutation_count']==0;print('ACEE6_K5_NON_REGRESSION_OK')
