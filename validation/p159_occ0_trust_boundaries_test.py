from __future__ import annotations
import copy,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_trust_boundaries as o
def ck(v,n): assert v,n; print(n)
def base(): return {"norm_id":"DNA.L0.6","strength":"MUST_NOT","authority":"HUMAN_RESERVED","scope":{"population":"humans"},"temporal":{"expiry":"2027-01-01"},"uncertainty":"UNKNOWN","provenance":["GENESIS.G0","DNA.L0.6"]}
def main():
 ck(o.STATUS=="IMPLEMENTED_NOT_LOCKED","P159_OCC0_NOT_PREMATURELY_LOCKED_OK")
 ck(o.ROLES==("SOURCE","COMPILER","VERIFIER","AUTHORITY","EXECUTION"),"P159_OCC0_ROLE_SEPARATION_OK")
 ck(all(v is False for k,v in o.BOUNDARIES.items() if k not in ("functional_conclusion_only","phenomenology_undetermined")),"P159_OCC0_NON_SOVEREIGN_BOUNDARIES_OK")
 ck(o.classify_compilability(deterministic=True)=="C1" and o.classify_compilability(deterministic=True,runtime_facts_required=True)=="C2" and o.classify_compilability(deterministic=False,human_judgment_required=True)=="C3","P159_OCC0_COMPILABILITY_CLASSES_OK")
 s=base(); c=copy.deepcopy(s); ck(o.evaluate_preservation(s,c)["profile_state"]=="UNVERIFIED_COMPILED_PROFILE","P159_OCC0_CONSERVATIVE_SUCCESS_OK")
 for field,value,reason in [("strength","SHOULD","SEMANTIC_DELTA"),("authority","AUTOMATED","HUMAN_RESERVED_AUTOMATION"),("scope",{"population":"all"},"SCOPE_WIDENING"),("temporal",{"expiry":None},"TEMPORAL_WEAKENING"),("uncertainty","TRUE","UNKNOWN_REQUIRED_PRECONDITION"),("provenance",[],"PROVENANCE_LOSS")]:
  x=copy.deepcopy(c); x[field]=value; rr=o.evaluate_preservation(s,x)
  ck(rr["status"]=="FAIL" and rr["reason"]==reason and rr["authorization"] is False and rr["execution"] is False and rr["relaxed_rule"] is False,"P159_OCC0_FAIL_CLOSED_"+field.upper()+"_OK")
 x=copy.deepcopy(c); del x["strength"]; ck(o.evaluate_preservation(s,x)["status"]=="FAIL","P159_OCC0_NO_SILENT_LOSS_OK")
 ck(o.fail_closed("UNSUPPORTED")["profile_state"]=="UNSUPPORTED","P159_OCC0_UNSUPPORTED_NOT_RELAXED_OK")
 ck(len(o.THREAT_CLASSES)==17,"P159_OCC0_THREAT_MODEL_OK")
 code="import json; from ontology.occ_trust_boundaries import manifest; print(json.dumps(manifest(),sort_keys=True))"
 env=dict(os.environ); env["PYTHONPATH"]=str(ROOT)
 a=subprocess.check_output([sys.executable,"-c",code],cwd=str(ROOT),env=env,text=True); b=subprocess.check_output([sys.executable,"-c",code],cwd="/tmp",env=env,text=True)
 ck(a==b,"P159_OCC0_CWD_INDEPENDENCE_OK")
 print("P159_OCC0_TRUST_BOUNDARIES_OK")
if __name__=="__main__": main()
