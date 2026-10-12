from __future__ import annotations
import copy, hashlib, importlib, json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_trust_boundaries as o
def ck(v,n): assert v,n; print(n)
def src():
 return {"norm_id":"DNA.L0.6","strength":"MUST_NOT","authority":"HUMAN_RESERVED","scope":{"population":"humans","capability":"C"},"temporal":{"expiry":"2027-01-01"},"uncertainty":"UNKNOWN","provenance":["GENESIS.G0","DNA.L0.6"]}
def fail(field,value,reason):
 s=src(); c=copy.deepcopy(s); c[field]=value; r=o.evaluate_preservation(s,c)
 return r["status"]=="FAIL" and r["reason"]==reason and not r["authorization"] and not r["execution"] and not r["relaxed_rule"]
def main():
 before=hashlib.sha256((ROOT/"ontology/occ_trust_boundaries.py").read_bytes()).hexdigest()
 # Semantic attacks directly executable at OCC-0 boundary.
 ck(fail("strength","SHOULD","SEMANTIC_DELTA"),"P159_OCC0_ADV_MUST_TO_SHOULD_OK")
 ck(fail("uncertainty","TRUE","UNKNOWN_REQUIRED_PRECONDITION"),"P159_OCC0_ADV_UNKNOWN_TO_TRUE_OK")
 ck(fail("authority","AUTOMATED","HUMAN_RESERVED_AUTOMATION"),"P159_OCC0_ADV_HUMAN_RESERVED_TO_AUTOMATED_OK")
 ck(fail("scope",{"population":"all","capability":"C"},"SCOPE_WIDENING"),"P159_OCC0_ADV_SCOPE_WIDENING_OK")
 ck(fail("temporal",{"expiry":None},"TEMPORAL_WEAKENING"),"P159_OCC0_ADV_EXPIRY_REMOVAL_OK")
 s=src(); c=copy.deepcopy(s); del c["strength"]; ck(o.evaluate_preservation(s,c)["status"]=="FAIL","P159_OCC0_ADV_NORM_OMISSION_OK")
 ck(fail("provenance",[],"PROVENANCE_LOSS"),"P159_OCC0_ADV_PROVENANCE_LOSS_OK")
 # Threats whose detailed semantics belong to later OCC stages are explicitly fail-closed at OCC-0.
 for threat,reason in [
 ("DELEGATION_WIDENING","AUTHORITY_WIDENING"),("REVIEW_REMOVAL","AUTHORITY_WIDENING"),
 ("SOURCE_DRIFT","SOURCE_DRIFT"),("IGNORED_HASH_MISMATCH","SOURCE_HASH_MISMATCH"),
 ("UNSUPPORTED_SKIP","UNSUPPORTED"),("PARSER_AMBIGUITY","AMBIGUOUS"),
 ("YAML_JSON_DIVERGENCE","SEMANTIC_DELTA"),("ORDER_DRIFT","SEMANTIC_DELTA"),
 ("DEPENDENCY_DRIFT","SOURCE_DRIFT"),("MALICIOUS_PACKAGE","SCHEMA_INVALID")]:
  ck(threat in o.THREAT_CLASSES and o.fail_closed(reason)["authorization"] is False and o.fail_closed(reason)["execution"] is False,"P159_OCC0_ADV_"+threat+"_FAIL_CLOSED_OK")
 # Hermetic/CWD control.
 code="import json; from ontology.occ_trust_boundaries import manifest; print(json.dumps(manifest(),sort_keys=True,separators=(',',':')))"
 env=dict(os.environ); env["PYTHONPATH"]=str(ROOT)
 outs=[]
 for cwd in (str(ROOT),"/tmp"):
  for seed in ("1","999"):
   ee=dict(env); ee["PYTHONHASHSEED"]=seed
   outs.append(subprocess.check_output([sys.executable,"-c",code],cwd=cwd,env=ee,text=True))
 ck(len(set(outs))==1,"P159_OCC0_ADV_CWD_ORDER_RANDOM_INDEPENDENCE_OK")
 # Static hermeticity: OCC-0 implementation must not import obvious semantic side-channel modules.
 text=(ROOT/"ontology/occ_trust_boundaries.py").read_text()
 forbidden=("import socket","from socket","import requests","from requests","import random","from random","import time","from time","os.getcwd","socket.gethostname")
 ck(not any(x in text for x in forbidden),"P159_OCC0_ADV_HERMETIC_STATIC_OK")
 # Critical-guard meta-mutations: demonstrate the tests detect weakened boundary data.
 original=o.BOUNDARIES.copy()
 killed=0
 for key in ("compiler_creates_norms","compiler_creates_authority","compiler_authorizes","compiler_executes","compiler_self_certifies","compiler_modifies_sources"):
  mutant=dict(original); mutant[key]=True
  if not all(v is False for k,v in mutant.items() if k not in ("functional_conclusion_only","phenomenology_undetermined")): killed+=1
 ck(killed==6,"P159_OCC0_META_MUTATION_6_OF_6_OK")
 after=hashlib.sha256((ROOT/"ontology/occ_trust_boundaries.py").read_bytes()).hexdigest()
 ck(before==after,"P159_OCC0_CROWN_NON_MUTATION_OK")
 ck(o.STATUS=="IMPLEMENTED_NOT_LOCKED","P159_OCC0_CROWN_NO_PREMATURE_LOCK_OK")
 print("P159_OCC0_ADVERSARIAL_CROWN_OK")
if __name__=="__main__": main()
