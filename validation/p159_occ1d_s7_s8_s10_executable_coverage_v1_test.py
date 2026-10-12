from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_static_constitutional_checker as s
CNP=ROOT/"validation_artifacts"/"p159"/"occ1c"/"compiled_normative_profile_v1.json"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ph(r,p): return next(x for x in r["findings"] if x["phase"]==p)
def run():
 p=json.loads(CNP.read_text()); a=s.check_profile(p,ROOT,sha(CNP)); b=s.check_profile(p,ROOT,sha(CNP)); assert a==b
 assert a["decision"]=="STATIC_UNRESOLVED"
 assert ph(a,"S7")["evidence"]["reason"]=="SOURCE_CONFLICT_TOPOLOGY_NOT_MATERIALIZED"
 assert ph(a,"S8")["evidence"]["reason"]=="COMPOSITION_GRAPH_NOT_MATERIALIZED"
 assert ph(a,"S10")["evidence"]["reason"]=="RUNTIME_ENFORCEMENT_CONSUMER_GRAPH_NOT_PROVEN"
 for m in ("G0_ARBITRABLE","L0_ARBITRABLE","CCAD_OVERRIDE_GENESIS","CCAD_OVERRIDE_DNA","HIDDEN_FIXED_DNA_H_RANKING","EXCEPTION_AS_PRECEDENT","TRAGIC_CHOICE_AUTO_AUTHORIZE"):
  q=deepcopy(p);q["relations"]=[{"kind":m}];assert ph(s.check_profile(q,ROOT,sha(CNP)),"S7")["result"]=="FAIL"
 for m in ("TENSION_AS_CONTRADICTION","CONTRADICTION_AS_TENSION"):
  q=deepcopy(p);q["relations"]=[{"kind":"CONFLICTS_WITH","classification":m}];assert ph(s.check_profile(q,ROOT,sha(CNP)),"S7")["result"]=="FAIL"
 for m in ("COALITION_AUTHORITY_AMPLIFICATION","SEQUENCE_CIRCUMVENTION","TOXIC_COMBINATION","DELEGATION_CHAIN_AMPLIFICATION"):
  q=deepcopy(p);q["relations"]=[{"kind":m,"from":"A","to":"B"}];assert ph(s.check_profile(q,ROOT,sha(CNP)),"S8")["result"]=="FAIL"
 q=deepcopy(p);q["relations"]=[{"kind":"SAFE","from":str(i),"to":str(i+1)} for i in range(s.BOUND+1)];assert ph(s.check_profile(q,ROOT,sha(CNP)),"S8")["result"]=="UNRESOLVED"
 cases=[{"E5.X":{"critical":True,"consumers":[]}},{"E5.X":{"critical":True,"consumers":["Gate"],"reachable":True,"mode":"DOCUMENTARY_ONLY"}},{"E5.X":{"critical":True,"consumers":["Gate"],"reachable":False}},{"E5.X":{"critical":True,"consumers":["Gate"],"reachable":True,"consumer_reference_valid":False}},{"E5.X":{"critical":True,"consumers":["Gate"],"reachable":True,"flow":"F1->F3"}},{"E5.X":{"critical":True,"consumers":["Gate"],"reachable":True,"flow":"E5->E1"}}]
 for em in cases:
  q=deepcopy(p);q["enforcement_coverage_map"]=em;assert ph(s.check_profile(q,ROOT,sha(CNP)),"S10")["result"]=="FAIL"
 q=deepcopy(p);q["enforcement_coverage_map"]={"E5.X":{"critical":True,"consumers":["Gate"],"reachable":True,"consumer_reference_valid":True,"flow":"E3->E3"}};assert ph(s.check_profile(q,ROOT,sha(CNP)),"S10")["result"]=="PASS"
 assert not a["authorization_created"] and not a["authority_activated"] and not a["execution_performed"] and not a["occ1d_closed"] and not a["occ1e_opened"] and not a["p160_opened"]
 print("P159_OCC1D_S7_EXECUTABLE_COVERAGE_OK");print("P159_OCC1D_S8_BOUNDED_GRAPH_COVERAGE_OK");print("P159_OCC1D_S10_ENFORCEMENT_MAP_COVERAGE_OK");print("P159_OCC1D_REAL_CNP_UNRESOLVED_PRESERVED_OK");print("P159_OCC1D_S7_S8_S10_DETERMINISM_OK");print("P159_OCC1D_STAGE_BOUNDARIES_PRESERVED_OK")
if __name__=="__main__":run()
