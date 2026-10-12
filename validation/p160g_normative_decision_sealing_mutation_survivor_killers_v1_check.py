from pathlib import Path
import hashlib,json
ROOT=Path.home()/"open-cognitive-ecology";R=ROOT/"ontology"/"p160_normative_decision_sealing.py";P=ROOT/"validation"/"p160g_normative_decision_sealing_mutation_survivor_killers_v1_report.json"
E="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c";sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R)==E
d=json.loads(P.read_text())
assert d["runtime_sha256"]==E and d["runtime_unchanged"] is True
assert d["mutants_total"]==3 and d["killed"]==3 and d["survived"]==0 and d["inconclusive"]==0 and d["mutation_score"]==1.0
assert all(x["pytest_import"]=="PASS" for x in d["results"])
print("P160G_MUTATION_SURVIVOR_KILLERS_REPORT_OK");print("killed=3");print("survived=0");print("inconclusive=0");print("mutation_score=1.000000");print("RUNTIME_UNCHANGED=true");print("P160H_OPENED=false");print("P161_OPENED=false")
