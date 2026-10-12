from pathlib import Path
import ast, hashlib
from ontology import p160_normative_decision_sealing as m

EXPECTED_RUNTIME_SHA="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
p=Path(m.__file__)
actual=hashlib.sha256(p.read_bytes()).hexdigest()
assert actual==EXPECTED_RUNTIME_SHA,(actual,EXPECTED_RUNTIME_SHA)

src=p.read_text(encoding="utf-8")
tree=ast.parse(src)
forbidden_defs={"authorize","issue_token","grant_capability","execute","call_tool","authorization_token"}
defs={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
assert not (defs & forbidden_defs), sorted(defs & forbidden_defs)

mf=m.manifest()
for key in ("authority_created","authorization_created","authorization_token_created","execution_performed","p161_opened"):
    assert mf[key] is False,(key,mf[key])
assert "AUTHORITY_VALID != AUTHORIZATION" in mf["doctrines"]
assert "SEALED != AUTHORIZED" in mf["doctrines"]
assert "DECISION_VALIDITY_IS_INTERSECTION_NOT_UNION" in mf["doctrines"]

print("P160G_DEFENSIVE_CROWN_CONTRACT_OK")
print("RUNTIME_SHA256="+actual)
print("AUTHORITY_CREATED=false")
print("AUTHORIZATION_CREATED=false")
print("AUTHORIZATION_TOKEN_CREATED=false")
print("EXECUTION_PERFORMED=false")
print("P160H_OPENED=false")
print("P161_OPENED=false")
