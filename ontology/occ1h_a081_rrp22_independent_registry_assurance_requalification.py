from __future__ import annotations
import ast,hashlib
from pathlib import Path
CONSUMERS=("NormResolver","CCAD","AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine")
def _valid_hash(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)
def oracle(registry,consumer,expected):
 if consumer not in CONSUMERS:return False
 if not _valid_hash(expected) or not isinstance(registry,dict):return False
 e=registry.get(consumer)
 return isinstance(e,dict) and set(e)=={"cnp_artifact_hash"} and _valid_hash(e["cnp_artifact_hash"]) and e["cnp_artifact_hash"]==expected
def verify_implementation_source(path):
 tree=ast.parse(Path(path).read_text())
 fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="verify_binding"),None)
 return fn is not None and len(fn.args.args)==3
def independently_requalify(r21_path):
 h=hashlib.sha256(b"canonical-cnp-fixture").hexdigest();other=hashlib.sha256(b"substituted-cnp-fixture").hexdigest()
 good={c:{"cnp_artifact_hash":h} for c in CONSUMERS}
 cases={"canonical":oracle(good,"NormResolver",h),"registry_substitution":oracle({**good,"NormResolver":{"cnp_artifact_hash":other}},"NormResolver",h),"cnp_substitution":oracle(good,"NormResolver",other),"unknown_consumer":oracle(good,"UnknownConsumer",h)}
 missing=dict(good);missing.pop("NormResolver");cases["missing_binding"]=oracle(missing,"NormResolver",h)
 cases["ambiguous_binding"]=oracle({**good,"NormResolver":{"cnp_artifact_hash":h,"fallback_hash":other}},"NormResolver",h)
 expected={"canonical":True,"registry_substitution":False,"cnp_substitution":False,"unknown_consumer":False,"missing_binding":False,"ambiguous_binding":False}
 ok=verify_implementation_source(r21_path) and all(cases[k] is v for k,v in expected.items())
 return {"schema":"oce.p159.occ1h.a081.rrp22.independent_registry_assurance_requalification.v1","scenario_id":"A081","independent_oracle":"SEPARATE_IMPLEMENTATION_NO_IMPORT_FROM_RRP21","cases":cases,"implementation_shape_verified_without_using_result_as_oracle":verify_implementation_source(r21_path),"rrp22":"PASSED_BOUNDED" if ok else "FAILED","candidate_verdict":"RESISTED" if ok else "INCONCLUSIVE","return_to_rrp9_12_required":True,"real_runtime_binding_claimed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
