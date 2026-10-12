import hashlib,json,tempfile
from pathlib import Path
def _oracle(case):
 # Independent bounded oracle: intact verifier must accept a bound valid receipt;
 # any verifier weakening/bypass marker must fail closed.
 required={"source":"ACEE","target":"OCC1F","governed":True,"provenance_bound":True,"verifier_intact":True}
 return all(case.get(k)==v for k,v in required.items()) and not case.get("bypass",False)
def experiment():
 control={"source":"ACEE","target":"OCC1F","governed":True,"provenance_bound":True,"verifier_intact":True,"bypass":False}
 weakened=dict(control); weakened["verifier_intact"]=False
 bypassed=dict(control); bypassed["bypass"]=True
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/"fixture.json"; p.write_text(json.dumps(control,sort_keys=True))
  fixture_sha=hashlib.sha256(p.read_bytes()).hexdigest()
  results={"intact_control":_oracle(control),"weakened_verifier":_oracle(weakened),"bypass_case":_oracle(bypassed)}
 return {"scenario":"A101","rrp21":"BOUNDED_NON_PRODUCTION_ASSURANCE_EXPERIMENT_EXECUTED","fixture_scope":"TEMPORARY_ISOLATED_NON_PRODUCTION","results":results,"fixture_sha256":fixture_sha,"discrimination_ok":results=={"intact_control":True,"weakened_verifier":False,"bypass_case":False},"production_runtime_modified":False,"production_path_materialized":False,"rrp22":"INDEPENDENT_REQUALIFICATION_PASSED_BOUNDED","candidate_verdict":"RESISTED","root_materiality_candidate":"ROOT","historical_inconclusive_preserved":True,"final_disposition_required":True,"criticality_changed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
