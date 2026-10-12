import ast, hashlib
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
p=ROOT/"acee6_a_contract_snapshot.py"
source=p.read_text(encoding="utf-8")
def digest(text): return hashlib.sha256(ast.dump(ast.parse(text),include_attributes=False).encode()).hexdigest()
original=digest(source); corrupted=digest(source.replace('PUBLIC_SCHEMA_VERSION = "1.0.0"','PUBLIC_SCHEMA_VERSION = "9.9.9"'))
assert original!=corrupted
assert 'acee6_a_contract_snapshot.py' in (ROOT/'acee6_a_contract_integrity_test.py').read_text(encoding='utf-8')
assert 'PUBLIC_CONTRACT' in (ROOT/'acee6_a_schema_backward_compatibility_test.py').read_text(encoding='utf-8')
print("ACEE6_A_SNAPSHOT_CORRUPTION_OK")
