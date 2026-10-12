from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"validation_artifacts"/"p159"/"occ1d"/"s10_enforcement_evidence_v1.json"
CNP=ROOT/"validation_artifacts"/"p159"/"occ1c"/"compiled_normative_profile_v1.json"
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_static_constitutional_checker as s
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
e=json.loads(ART.read_text(encoding="utf-8"))
assert e["declarative_compilation_coverage_proven"] is True
assert e["transformation_ledger_entries"]==48 and e["unique_rule_ids"]==48
assert e["compiler_classes_are_not_runtime_consumers"] is True
assert e["runtime_enforcement_consumer_graph_present"] is False
assert e["runtime_reachability_proven"] is False
assert e["decision"]=="UNRESOLVED" and e["unresolved_promoted_to_pass"] is False
p=json.loads(CNP.read_text(encoding="utf-8"));r=s.check_profile(p,ROOT,sha(CNP))
m={x["phase"]:x["result"] for x in r["findings"]}
assert m["S7"]=="UNRESOLVED" and m["S8"]=="UNRESOLVED" and m["S10"]=="UNRESOLVED"
assert r["decision"]=="STATIC_UNRESOLVED"
print("P159_OCC1D_S10_OCC1C_DECLARATIVE_COVERAGE_48_48_OK")
print("P159_OCC1D_S10_RUNTIME_CONSUMER_GRAPH_ABSENCE_PRESERVED_OK")
print("P159_OCC1D_S10_UNRESOLVED_NOT_PROMOTED_OK")
print("P159_OCC1D_S7_S8_UNRESOLVED_PRESERVED_OK")
