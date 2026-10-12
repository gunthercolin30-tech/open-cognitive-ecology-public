from __future__ import annotations
import hashlib
CONSUMERS=("NormResolver","CCAD","AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine")
def _valid_hash(x): return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)
def verify_binding(registry,consumer_type,expected_cnp_hash):
    if consumer_type not in CONSUMERS:return {"accepted":False,"reason":"UNKNOWN_CONSUMER_FAIL_CLOSED"}
    if not _valid_hash(expected_cnp_hash):return {"accepted":False,"reason":"INVALID_EXPECTED_HASH_FAIL_CLOSED"}
    if not isinstance(registry,dict):return {"accepted":False,"reason":"MALFORMED_REGISTRY_FAIL_CLOSED"}
    entry=registry.get(consumer_type)
    if not isinstance(entry,dict):return {"accepted":False,"reason":"MISSING_OR_AMBIGUOUS_BINDING_FAIL_CLOSED"}
    if set(entry)!={"cnp_artifact_hash"}:return {"accepted":False,"reason":"AMBIGUOUS_BINDING_FAIL_CLOSED"}
    bound=entry.get("cnp_artifact_hash")
    if not _valid_hash(bound):return {"accepted":False,"reason":"INVALID_BOUND_HASH_FAIL_CLOSED"}
    if bound!=expected_cnp_hash:return {"accepted":False,"reason":"REGISTRY_SUBSTITUTION_REJECTED"}
    return {"accepted":True,"reason":"EXACT_CONTENT_ADDRESS_BINDING_ACCEPTED"}
def run():
    h=hashlib.sha256(b"canonical-cnp-fixture").hexdigest(); other=hashlib.sha256(b"substituted-cnp-fixture").hexdigest()
    good={c:{"cnp_artifact_hash":h} for c in CONSUMERS}
    cases={"canonical":verify_binding(good,"NormResolver",h)}
    bad={**good,"NormResolver":{"cnp_artifact_hash":other}}
    cases["registry_substitution"]=verify_binding(bad,"NormResolver",h)
    cases["cnp_substitution"]=verify_binding(good,"NormResolver",other)
    cases["unknown_consumer"]=verify_binding(good,"UnknownConsumer",h)
    missing=dict(good); missing.pop("NormResolver"); cases["missing_binding"]=verify_binding(missing,"NormResolver",h)
    ambiguous={**good,"NormResolver":{"cnp_artifact_hash":h,"fallback_hash":other}}
    cases["ambiguous_binding"]=verify_binding(ambiguous,"NormResolver",h)
    expected={"canonical":True,"registry_substitution":False,"cnp_substitution":False,"unknown_consumer":False,"missing_binding":False,"ambiguous_binding":False}
    ok=all(cases[k]["accepted"] is v for k,v in expected.items())
    return {"schema":"oce.p159.occ1h.a081.rrp21.bounded_registry_assurance_experiment.v1","scenario_id":"A081","scope":"BOUNDED_P159_ASSURANCE_FIXTURE","cases":cases,"all_required_discriminations_passed":ok,"experimental_verdict":"RESISTED_BOUNDED" if ok else "INCONCLUSIVE","real_runtime_consumer_graph_materialized":False,"real_runtime_binding_claimed":False,"canonical_source_modified":False,"authorization_created":False,"execution_capability":False,"rrp22":"REQUIRED_INDEPENDENTLY","occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
