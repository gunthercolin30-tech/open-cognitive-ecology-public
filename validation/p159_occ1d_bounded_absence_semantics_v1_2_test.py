from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_static_constitutional_checker as s
CNP=ROOT/"validation_artifacts"/"p159"/"occ1c"/"compiled_normative_profile_v1.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=json.loads(CNP.read_text(encoding="utf-8"))
a=s.check_profile(p,ROOT,sha(CNP));b=s.check_profile(p,ROOT,sha(CNP))
assert a==b and a["decision"]=="STATIC_UNRESOLVED"
m={x["phase"]:x["result"] for x in a["findings"]}
assert m["S3"]=="PASS" and m["S4"]=="PASS"
assert m["S7"]=="UNRESOLVED" and m["S8"]=="UNRESOLVED" and m["S10"]=="UNRESOLVED"
assert not a["root_checks_disableable"] and not a["unresolved_promoted_to_pass"]
assert not a["authorization_created"] and not a["authority_activated"] and not a["execution_performed"]
print("P159_OCC1D_S3_BOUNDED_SCOPE_ABSENCE_PROVEN_OK")
print("P159_OCC1D_S4_BOUNDED_TEMPORAL_ABSENCE_PROVEN_OK")
print("P159_OCC1D_S7_S8_S10_UNRESOLVED_PRESERVED_OK")
print("P159_OCC1D_BOUNDED_ABSENCE_DETERMINISM_OK")
