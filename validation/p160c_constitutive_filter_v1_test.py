from ontology import p160_norm_resolution as b
from ontology import p160_constitutive_filter as c
from ontology import operational_constitutional_invariants as oci
def nr():
 r=[{"rule_id":"DNA-L0.3","source_norm_ids":["DNA-L0.3"],"constitutive":True,"always_evaluate":True,"conditions":[]}]
 return b.resolve_norms({}, {"artifact_hash":"p159-profile","source_map":{"DNA-L0.3":"canonical"},"rules":r}, {"constitutional_snapshot":{"snapshot_semantic_hash":"snap"},"decision_context_fingerprint":{"fingerprint":"fp"}})
def ev(s="PASS"): return {"constraints":{"DNA-L0.3":s},"invariants":{n:"PASS" for n in oci.MANDATORY_INVARIANTS}}
def test_pass_non_authorizing():
 o=c.filter_constitutive(nr(),ev()); assert o["constitutive_filter_result"]=="PASS" and not o["authorized"] and c.verify_constitutive_filter(o)["status"]=="PASS"
def test_unknown_closed(): assert c.filter_constitutive(nr(),{})["constitutive_filter_result"]=="UNDETERMINED"
def test_fail_blocks(): assert c.filter_constitutive(nr(),ev("FAIL"))["constitutive_filter_result"]=="FAIL"
def test_conflict_not_arbitrated():
 o=c.filter_constitutive(nr(),ev("CONFLICT")); assert o["constitutive_filter_result"]=="CONFLICT" and not o["conflict_resolved"] and not o["p160d_opened"]
def test_unknown_invariant_not_pass():
 e=ev(); e["invariants"]["authority"]="UNKNOWN"; assert c.filter_constitutive(nr(),e)["constitutive_filter_result"]=="UNDETERMINED"
def test_tamper():
 o=c.filter_constitutive(nr(),ev()); o["authorized"]=True; assert c.verify_constitutive_filter(o)["status"]=="FAIL"
def test_bad_upstream_rejected():
 o=nr(); o["norm_context"]["applicable_norms"]=[]
 try: c.filter_constitutive(o,{}); assert False
 except ValueError: pass
def test_deterministic(): assert c.filter_constitutive(nr(),ev())==c.filter_constitutive(nr(),ev())
def test_manifest_boundaries():
 m=c.manifest(); assert m["scope"]=="P160-C_ONLY" and "constitutional_non_circumvention" in m["excluded_runtime_dependency"] and not m["boundaries"]["conflict_arbitration_performed"] and not m["boundaries"]["authority_resolved"] and not m["boundaries"]["authorization_created"] and not m["boundaries"]["execution_performed"] and not m["boundaries"]["p161_opened"]
