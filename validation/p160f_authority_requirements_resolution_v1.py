from pathlib import Path
import ast
from ontology import p160_authority_requirements_resolution as m
p=Path(m.__file__)
src=p.read_text(encoding="utf-8")
tree=ast.parse(src)
funcs={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
forbidden={"authorize","issue_token","grant_capability","execute","call_tool"}
assert not (funcs & forbidden), funcs & forbidden
man=m.manifest()
assert man["boundaries"]=={"authority_created":False,"authorization_created":False,"execution_performed":False,"p160g_opened":False,"p161_opened":False}
assert "P095.authorize" in man["does_not_call"]
assert "P098.resolve_conflict" in man["does_not_call"]
for token in ("AUTHORITY_CLASSES","AUTHORITY_STATUSES","REQUIREMENT_MODES","DOCTRINES","resolve_authority_requirements","verify_authority_resolution"):
    assert token in src
print("P160F_AUTHORITY_REQUIREMENTS_RESOLUTION_CONTRACT_OK")
print("AUTHORITY_CREATED=false")
print("AUTHORIZATION_CREATED=false")
print("EXECUTION_PERFORMED=false")
print("P160G_OPENED=false")
print("P161_OPENED=false")
