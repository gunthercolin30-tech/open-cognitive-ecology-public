from __future__ import annotations
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PKG=ROOT/"normative/occ1a"
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_canonical_normative_sources as o
def ck(v,n): assert v,n; print(n)
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def main():
 m=load(PKG/"manifest.yaml")
 ck(m["package_state"]=="DRAFT" and m["shadow_test_only"] is True,"P159_OCC1A_DRAFT_ONLY_OK")
 ck(m["kernel_target"]["principal_object_count"]==48 and len(m["kernel_target"]["ids"])==48 and len(set(m["kernel_target"]["ids"]))==48,"P159_OCC1A_48_STABLE_IDS_OK")
 ck(m["kernel_population_status"].startswith("UNRESOLVED"),"P159_OCC1A_NO_INVENTED_BINDING_OK")
 ck(m["canonicalization"]["comments_normative"] is False and m["canonicalization"]["executable_code_allowed"] is False,"P159_OCC1A_NON_EXECUTABLE_SOURCE_OK")
 ck("ROOT_OVERRIDE_ALL" in o.FORBIDDEN_AUTHORITY and len(o.NSI)==12,"P159_OCC1A_VOCABULARY_NSI_OK")
 for s in m["source_artifacts"]:
  p=ROOT/s["path"]; ck(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==s["sha256"],"P159_OCC1A_SOURCE_HASH_"+s["source_id"]+"_OK")
 h=load(PKG/"hash_manifest.json")
 for e in h["entries"]:
  p=PKG/e["path"]; ck(hashlib.sha256(p.read_bytes()).hexdigest()==e["sha256"],"P159_OCC1A_PACKAGE_HASH_"+e["path"].replace("/","_")+"_OK")
 bad={"id":"DNA.L0.6","version":"1.0.0","level":"DNA_L0","strength":"MUST","formalization":"F1_STRUCTURED","text":"x","structure":{},"executable_semantics":None,"status":"ACTIVE","provenance":[]}
 ck(o.validate_norm_record(bad)["reason"]=="BROKEN_LINEAGE","P159_OCC1A_BROKEN_LINEAGE_FAIL_CLOSED_OK")
 bad["provenance"]=["GENESIS.G0"]; bad["text"]="ROOT_OVERRIDE_ALL"
 ck(o.validate_norm_record(bad)["reason"]=="FORBIDDEN_ROOT_OVERRIDE","P159_OCC1A_ROOT_OVERRIDE_FORBIDDEN_OK")
 ck(o.validate_reference({"type":"semantic_reference","target":"DNA.H99"},{"GENESIS.G0"})["reason"]=="BROKEN_NORM_REFERENCE","P159_OCC1A_DANGLING_REFERENCE_FAIL_CLOSED_OK")
 code="import json; from ontology.occ_canonical_normative_sources import manifest; print(json.dumps(manifest(),sort_keys=True,separators=(',',':')))"
 env=dict(os.environ); env["PYTHONPATH"]=str(ROOT)
 a=subprocess.check_output([sys.executable,"-c",code],cwd=str(ROOT),env=env,text=True); b=subprocess.check_output([sys.executable,"-c",code],cwd="/tmp",env=env,text=True)
 ck(a==b,"P159_OCC1A_CWD_INDEPENDENCE_OK")
 ck(m["occ1b_opened"] is False and m["p160_opened"] is False,"P159_OCC1A_SCOPE_BOUNDARY_OK")
 print("P159_OCC1A_CANONICAL_SOURCES_FOUNDATION_OK")
if __name__=="__main__": main()
