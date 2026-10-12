from pathlib import Path
import hashlib,json
ROOT=Path.home()/"open-cognitive-ecology";R=ROOT/"ontology"/"p160_normative_decision_sealing.py";P=ROOT/"validation"/"p160g_normative_decision_sealing_mutation_crown_v3_report.json"
E="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R)==E
d=json.loads(P.read_text())
assert d["schema"]=="oce.p160g.mutation_crown.v3" and d["runtime_sha256"]==E and d["runtime_unchanged"] is True
assert d["pytest_import_sentinel"]=="PER_MUTANT"
assert d["mutants_total"]==19 and d["killed"]==19 and d["survived"]==0 and d["inconclusive"]==0 and d["mutation_score"]==1.0
assert all(r.get("pytest_sentinel")=="PASS" for r in d["results"])
print("P160G_MUTATION_CROWN_V3_REPORT_OK");print("mutants_total=19");print("killed=19");print("survived=0");print("inconclusive=0");print("mutation_score=1.000000");print("PYTEST_IMPORT_SENTINEL=PASS_ALL");print("RUNTIME_UNCHANGED=true");print("P160H_OPENED=false");print("P161_OPENED=false")
