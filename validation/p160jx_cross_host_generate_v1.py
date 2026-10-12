#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,locale,platform,sys
ROOT=Path.home()/"open-cognitive-ecology"
G=ROOT/"ontology"/"p160_normative_decision_sealing.py"
J=ROOT/"ontology"/"p160_normative_decision_persistence.py"
OUT=ROOT/"validation"/"evidence"/"p160jx"
G_EXPECTED="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if not G.is_file() or sha(G)!=G_EXPECTED:raise SystemExit("ERROR:G_DRIFT")
if not J.is_file():raise SystemExit("ERROR:J_MISSING")
sys.path.insert(0,str(ROOT))
from ontology.p160_normative_decision_persistence import canonical_platform_vector,roundtrip
vectors={
 "ordering":{"b":2,"a":1,"nested":{"z":0,"a":9}},
 "unicode":{"status":"UNKNOWN","label":"éligibilité","conflict":"CONTESTED","greek":"Ω","cjk":"開"},
 "temporal":{"instant":"2026-10-25T01:30:00Z","timezone_presentation":"Europe/Paris","expiry":"2030-01-01T00:00:00Z"},
 "numeric":{"zero":0,"one":1,"negative":-7,"ratio":0.125},
 "boundary":{"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p161_opened":False},
 "semantic":{"status":"UNKNOWN","postconditions":[{"id":"p1","status":"UNKNOWN"}],"scope":["alpha","beta"],"conditions":[{"kind":"review","required":True}]},
}
results={}
for name,obj in sorted(vectors.items()):
 rt=roundtrip(obj)
 if rt!=obj:raise SystemExit("ERROR:ROUNDTRIP:"+name)
 results[name]=canonical_platform_vector(rt)
aggregate_payload={k:results[k]["sha256"] for k in sorted(results)}
aggregate_hash=hashlib.sha256(json.dumps(aggregate_payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
doc={
 "schema":"oce.p160jx.cross_host_evidence.v1",
 "host":{"system":platform.system(),"machine":platform.machine(),"python":platform.python_version(),"byteorder":sys.byteorder,"locale":locale.setlocale(locale.LC_ALL,None)},
 "runtime":{"g_sha256":sha(G),"j_sha256":sha(J)},
 "vectors":results,"aggregate_hash":aggregate_hash,
 "boundaries":{"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p160k_opened":False,"p161_opened":False},
}
OUT.mkdir(parents=True,exist_ok=True)
tag=(platform.system()+"-"+platform.machine()).replace("/","_")
p=OUT/("p160jx_"+tag+".json")
p.write_text(json.dumps(doc,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("P160JX_PLATFORM_EVIDENCE_OK")
print("PLATFORM="+tag)
print("EVIDENCE="+str(p))
print("AGGREGATE_HASH="+aggregate_hash)
print("G_SHA256="+sha(G));print("J_SHA256="+sha(J))
print("P160K_OPENED=false");print("P161_OPENED=false")
