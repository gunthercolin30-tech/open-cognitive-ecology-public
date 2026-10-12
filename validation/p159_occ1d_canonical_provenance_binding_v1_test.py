from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
ROOT=Path.home()/"open-cognitive-ecology"; sys.path.insert(0,str(ROOT))
from ontology import occ_static_constitutional_checker as c
CNP=ROOT/"validation_artifacts"/"p159"/"occ1c"/"compiled_normative_profile_v1.json"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ph(r,p): return next(x for x in r["findings"] if x["phase"]==p)
p=json.loads(CNP.read_text()); hs=sha(CNP); base=c.check_profile(deepcopy(p),ROOT,hs)
assert ph(base,"S6")["result"]=="PASS"; print("P159_OCC1D_CANONICAL_CNP_S6_PASS_OK")
q=deepcopy(p); a=q["rules"][0]; asm=a["source_map"]; donor=None
for x in q["rules"][1:]:
 b=x.get("source_map") or {}
 if b.get("source_path")!=asm.get("source_path") and b.get("source_sha256")!=asm.get("source_sha256"): donor=b; break
assert donor is not None
a["source_map"]["source_path"]=donor["source_path"]; a["source_map"]["source_sha256"]=donor["source_sha256"]
assert ph(c.check_profile(q,ROOT,hs),"S6")["result"]=="FAIL"; print("P159_OCC1D_CROSS_PARTITION_PROVENANCE_LAUNDERING_DETECTED_OK")
q=deepcopy(p); q["rules"][0]["source_map"]["source_path"]="normative/occ1a/unknown/forged.yaml"; q["rules"][0]["source_map"]["source_sha256"]="0"*64
assert ph(c.check_profile(q,ROOT,hs),"S6")["result"]=="FAIL"; print("P159_OCC1D_UNKNOWN_PARTITION_PROVENANCE_FAIL_CLOSED_OK")
q=deepcopy(p); q["rules"][0]["source_map"]["source_sha256"]="f"*64
assert ph(c.check_profile(q,ROOT,hs),"S6")["result"]=="FAIL"; print("P159_OCC1D_CANONICAL_PARTITION_HASH_MISMATCH_DETECTED_OK")
assert base==c.check_profile(deepcopy(p),ROOT,hs); print("P159_OCC1D_CANONICAL_PROVENANCE_DETERMINISM_OK")
assert all(ph(base,x)["result"]=="UNRESOLVED" for x in ("S7","S8","S10")); print("P159_OCC1D_REAL_S7_S8_S10_UNRESOLVED_PRESERVED_OK")
assert not base["occ1d_closed"] and not base["occ1e_opened"] and not base["p160_opened"] and not base["p159_final_lock"]; print("P159_OCC1D_STAGE_BOUNDARIES_PRESERVED_OK")
