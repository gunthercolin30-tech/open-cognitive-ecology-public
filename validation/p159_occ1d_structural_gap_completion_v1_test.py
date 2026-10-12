from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
ROOT=Path.home()/"open-cognitive-ecology"; sys.path.insert(0,str(ROOT))
from ontology import occ_static_constitutional_checker as c
CNP=ROOT/"validation_artifacts"/"p159"/"occ1c"/"compiled_normative_profile_v1.json"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ph(r,p): return next(x for x in r["findings"] if x["phase"]==p)
p=json.loads(CNP.read_text()); hs=sha(CNP); base=c.check_profile(deepcopy(p),ROOT,hs)
assert base==c.check_profile(deepcopy(p),ROOT,hs); assert ph(base,"S1")["result"]=="PASS" and ph(base,"S6")["result"]=="PASS"
q=deepcopy(p); x=deepcopy(q["rules"][0]); x["norm_id"]=x["norm_id"]+".SPLIT"; q["rules"].append(x)
assert ph(c.check_profile(q,ROOT,hs),"S1")["result"]=="FAIL"; print("P159_OCC1D_SPLIT_RULE_STRUCTURAL_DETECTION_OK")
q=deepcopy(p); x=deepcopy(q["rules"][0]); x["norm_id"]=x["norm_id"].replace("A","А"); q["rules"].append(x)
assert ph(c.check_profile(q,ROOT,hs),"S1")["result"]=="FAIL"; print("P159_OCC1D_UNICODE_CONFUSABLE_STRUCTURAL_DETECTION_OK")
q=deepcopy(p); q["rules"][0]["source_map"]=deepcopy(q["rules"][1]["source_map"]); r=c.check_profile(q,ROOT,hs)
assert ph(r,"S6")["result"]=="FAIL" and ph(r,"S1")["result"]=="FAIL"; print("P159_OCC1D_PROVENANCE_LAUNDERING_STRUCTURAL_DETECTION_OK")
assert all(ph(base,x)["result"]=="UNRESOLVED" for x in ("S7","S8","S10")); print("P159_OCC1D_REAL_UNRESOLVED_PRESERVED_OK")
assert not base["occ1d_closed"] and not base["occ1e_opened"] and not base["p160_opened"] and not base["p159_final_lock"]; print("P159_OCC1D_STAGE_BOUNDARIES_PRESERVED_OK")
