from pathlib import Path
import hashlib, json
ROOT=Path.home()/"open-cognitive-ecology"
R=ROOT/"ontology"/"p160_normative_decision_sealing.py"
P=ROOT/"validation"/"p160g_normative_decision_sealing_mutation_crown_v1_report.json"
EXPECTED="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R)==EXPECTED,(sha(R),EXPECTED)
d=json.loads(P.read_text(encoding="utf-8"))
assert d["runtime_sha256"]==EXPECTED
assert d["runtime_unchanged"] is True
assert d["mutants_total"]==19
assert d["killed"]==19
assert d["survived"]==0
assert d["inconclusive"]==0
assert d["mutation_score"]==1.0
for k in ("authorization_created","authorization_token_created","execution_performed","p160h_opened","p161_opened"): assert d[k] is False
print("P160G_MUTATION_CROWN_REPORT_OK")
print("mutants_total=19"); print("killed=19"); print("survived=0"); print("inconclusive=0"); print("mutation_score=1.000000")
print("RUNTIME_UNCHANGED=true"); print("P160H_OPENED=false"); print("P161_OPENED=false")
