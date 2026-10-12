from pathlib import Path
import ast
from ontology import p160_normative_decision_sealing as m
src=Path(m.__file__).read_text(encoding="utf-8"); tree=ast.parse(src)
forbidden={"authorize","issue_token","grant_capability","execute","call_tool","authorization_token"}
defs={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
assert not (defs & forbidden), sorted(defs & forbidden)
mf=m.manifest()
for k in ("authority_created","authorization_created","authorization_token_created","execution_performed","p161_opened"): assert mf[k] is False
assert "ELIGIBLE_CANDIDATE" in mf["eligibility_domain"]; assert "SEALED" in mf["lifecycle_domain"]
assert "AUTHORITY_VALID != AUTHORIZATION" in mf["doctrines"]; assert "SEALED != AUTHORIZED" in mf["doctrines"]
print("P160G_NORMATIVE_DECISION_SEALING_CONTRACT_OK")
print("AUTHORITY_CREATED=false"); print("AUTHORIZATION_CREATED=false"); print("AUTHORIZATION_TOKEN_CREATED=false"); print("EXECUTION_PERFORMED=false"); print("P161_OPENED=false")
