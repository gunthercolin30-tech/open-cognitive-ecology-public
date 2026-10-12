from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_static_constitutional_checker as s
CNP=ROOT/"validation_artifacts"/"p159"/"occ1c"/"compiled_normative_profile_v1.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
 p=json.loads(CNP.read_text()); a=s.check_profile(p,ROOT,sha(CNP)); b=s.check_profile(p,ROOT,sha(CNP))
 assert a==b and a["scan_complete"] and len(a["phases"])==12 and len(a["scci_registry"])==16 and len(a["adversarial_case_registry"])==24
 assert a["decision"]=="STATIC_UNRESOLVED" and not a["root_checks_disableable"] and not a["unresolved_promoted_to_pass"]
 assert not a["authorization_created"] and not a["authority_activated"] and not a["execution_performed"] and not a["occ1d_closed"] and not a["occ1e_opened"] and not a["p160_opened"]
 assert s.check_profile(p,ROOT,sha(CNP),{"S1":False})["decision"]=="STATIC_FAIL"
 for mut in ("scope","unknown","emergency","duplicate","ccad","coalition","continuity","orphan"):
  q=deepcopy(p)
  if mut=="scope":q["rules"][0]["scope_constraints"]={"resource":"*"}
  elif mut=="unknown":q["rules"][0]["uncertainty_semantics"]="UNKNOWN_TO_ALLOW"
  elif mut=="emergency":q["rules"][0]["temporal_constraints"]={"renewal":"UNLIMITED_RENEWAL"}
  elif mut=="duplicate":q["rules"].append(deepcopy(q["rules"][0]))
  elif mut=="ccad":q["relations"]=[{"kind":"CCAD_OVERRIDE_DNA"}]
  elif mut=="coalition":q["relations"]=[{"kind":"COALITION_AUTHORITY_AMPLIFICATION"}]
  elif mut=="continuity":q["candidate_change_set"]={"kind":"GENESIS_BREAK"}
  elif mut=="orphan":q["enforcement_coverage_map"]={"E5.X":{"critical":True,"consumers":[]}}
  assert s.check_profile(q,ROOT,sha(CNP))["decision"]=="STATIC_FAIL",mut
 q=deepcopy(p);q["relations"]=[{"kind":"SAFE"}]*(s.BOUND+1);z=s.check_profile(q,ROOT,sha(CNP))
 assert any(x["finding_id"]=="S8.COMPOSITION" and x["result"]=="UNRESOLVED" for x in z["findings"])
 print("P159_OCC1D_STATIC_CHECKER_FUNCTIONAL_OK");print("P159_OCC1D_PHASES_S0_S11_DEFINED_OK");print("P159_OCC1D_SCCI_16_REGISTERED_OK");print("P159_OCC1D_ADVERSARIAL_24_REGISTERED_OK");print("P159_OCC1D_ROOT_CHECKS_NON_DISABLEABLE_OK");print("P159_OCC1D_UNRESOLVED_PRESERVED_OK");print("P159_OCC1D_SCOPE_UNKNOWN_TEMPORAL_ATTACKS_DETECTED");print("P159_OCC1D_DUPLICATE_CCAD_COALITION_ATTACKS_DETECTED");print("P159_OCC1D_COMPOSITION_BOUND_UNRESOLVED_OK");print("P159_OCC1D_CONTINUITY_ORPHAN_ENFORCEMENT_DETECTED");print("P159_OCC1D_DETERMINISM_OK");print("P159_OCC1D_STAGE_BOUNDARY_OK")
if __name__=="__main__":run()
