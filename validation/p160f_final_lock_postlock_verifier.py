from pathlib import Path
import hashlib,json,ast
ROOT=Path.home()/"open-cognitive-ecology"
R=ROOT/"ontology/p160_authority_requirements_resolution.py"
REP=ROOT/"validation/p160f_final_lock_report.json"
MAN=ROOT/"validation/p160f_final_lock_manifest.json"
EXPECTED_RUNTIME="6c9959a1e413af550e61b82e71e16cb684bf92a07f5b6fe784e3579beb86c60c"
def sh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads(MAN.read_text()); r=json.loads(REP.read_text())
assert sh(R)==EXPECTED_RUNTIME==m["runtime_sha256"]==r["runtime_sha256"]
assert sh(REP)==m["report_sha256"]
assert m["status"]=="LOCKED" and r["status"]=="LOCKED"
assert r["mutation_crown"]=={"mutants":17,"killed":17,"survived":0,"inconclusive":0,"score":1.0}
assert r["baseline"]=={"passed":14,"total":14}
assert r["defensive_crown"]=={"passed":22,"total":22}
assert r["discriminants"]=={"passed":6,"total":6}
assert r["p160e_nonregression"]=={"passed":28,"total":28}
for k in ("authority_created","authorization_created","execution_performed","p160g_opened","p161_opened"):
    assert m[k] is False and r[k] is False
for rel,h in m["evidence_sha256"].items(): assert sh(ROOT/rel)==h
src=R.read_text(); tree=ast.parse(src)
funcs={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
assert not funcs.intersection({"authorize","issue_token","grant_capability","execute","call_tool"})
assert "p160_authority_requirements_resolution" in (ROOT/"ontology_inventory.txt").read_text()
print("P160F_FINAL_LOCK_POSTLOCK_VERIFIED")
print("STATUS=LOCKED")
print("RUNTIME_SHA256="+EXPECTED_RUNTIME)
print("REPORT_SHA256="+sh(REP))
print("MANIFEST_SHA256="+sh(MAN))
print("AUTHORITY_CREATED=false")
print("AUTHORIZATION_CREATED=false")
print("EXECUTION_PERFORMED=false")
print("P160G_OPENED=false")
print("P161_OPENED=false")
