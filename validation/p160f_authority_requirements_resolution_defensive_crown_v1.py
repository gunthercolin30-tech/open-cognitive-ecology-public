from pathlib import Path
import ast
from ontology import p160_authority_requirements_resolution as m
src=Path(m.__file__).read_text(encoding="utf-8")
tree=ast.parse(src)
funcs={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
assert not funcs.intersection({"authorize","issue_token","grant_capability","execute","call_tool"})
man=m.manifest()
for k in ("authority_created","authorization_created","execution_performed","p160g_opened","p161_opened"):
    assert man["boundaries"][k] is False
for d in ("authority_authorization_separation","authority_dimensionality","human_absence_non_succession","authority_non_aggregation","separation_of_duties","authority_freshness"):
    assert man["doctrines"].get(d) is True
print("P160F_DEFENSIVE_CROWN_CONTRACT_OK")
print("AUTHORITY_CREATED=false")
print("AUTHORIZATION_CREATED=false")
print("EXECUTION_PERFORMED=false")
print("P160G_OPENED=false")
print("P161_OPENED=false")
