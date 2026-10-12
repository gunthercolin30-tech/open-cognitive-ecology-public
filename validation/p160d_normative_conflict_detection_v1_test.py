import copy
from ontology import p160_normative_conflict_detection as d
from ontology import p160_constitutive_filter as c
from ontology import p160_norm_resolution as b
from ontology import operational_constitutional_invariants as oci
def ca(state="PASS"):
    rules=[{"rule_id":"DNA-L0.3","source_norm_ids":["DNA-L0.3"],"constitutive":True,"always_evaluate":True,"conditions":[]}]
    nr=b.resolve_norms({},{"artifact_hash":"p159-profile","source_map":{"DNA-L0.3":"canonical"},"rules":rules},{"constitutional_snapshot":{"snapshot_semantic_hash":"snap"},"decision_context_fingerprint":{"fingerprint":"fp"}})
    return c.filter_constitutive(nr,{"constraints":{"DNA-L0.3":state},"invariants":{x:"PASS" for x in oci.MANDATORY_INVARIANTS}})
def reqs():
    return [{"requirement_id":"R1","source_norms":["N1"],"type":"OBLIGATION","protected_interest":"I1","affected_entities":["E1"],"condition":"X","scope":"S","time":"T","formalization":"F3","flexibility":"BOUNDED"},{"requirement_id":"R2","source_norms":["N2"],"type":"PRESERVATION","protected_interest":"I2","affected_entities":["E2"],"condition":"Y","scope":"S","time":"T","formalization":"F3","flexibility":"BOUNDED"}]
def alt(aid,c1,c2):
    return {"alternative_id":aid,"availability":"AVAILABLE_NOW","effects":{},"impacts":{},"resources":{},"latency":1,"reversibility":"YES","uncertainty":"LOW","feasibility":"PROVEN","authority":"UNRESOLVED","compatibility":{"R1":c1,"R2":c2}}
def test_real_conflict_after_adequate_search():
    o=d.detect_normative_conflict(ca(),reqs(),[alt("A","INCOMPATIBLE_UNDER_CURRENT_OPTION","INCOMPATIBLE_UNDER_CURRENT_OPTION")],search_completeness="ADEQUATE_SEARCH"); assert o["conflict_assessment"]["real_conflict_established"] and o["conflict_assessment"]["conflict_class"]=="C2"
def test_compliant_alternative_prevents_real_conflict():
    o=d.detect_normative_conflict(ca(),reqs(),[alt("A","INCOMPATIBLE_UNDER_CURRENT_OPTION","INCOMPATIBLE_UNDER_CURRENT_OPTION"),alt("B","COMPATIBLE","COMPATIBLE")],search_completeness="ADEQUATE_SEARCH"); assert not o["conflict_assessment"]["real_conflict_established"] and o["conflict_assessment"]["conflict_class"]=="C1"
def test_partial_search_never_means_no_alternative():
    o=d.detect_normative_conflict(ca(),reqs(),[alt("A","INCOMPATIBLE_UNDER_CURRENT_OPTION","INCOMPATIBLE_UNDER_CURRENT_OPTION")],search_completeness="PARTIAL_SEARCH"); assert o["conflict_assessment"]["certainty"]=="UNRESOLVED" and not o["conflict_assessment"]["real_conflict_established"]
def test_constitutive_nonpass_rejected():
    try: d.detect_normative_conflict(ca("FAIL"),reqs(),[],search_completeness="ADEQUATE_SEARCH"); assert False
    except ValueError: pass
def test_unknown_not_conflict():
    bad=reqs(); bad[0]["protected_interest"]="UNKNOWN"
    o=d.detect_normative_conflict(ca(),bad,[alt("A","COMPATIBLE","COMPATIBLE")],search_completeness="ADEQUATE_SEARCH"); assert o["conflict_assessment"]["certainty"]=="UNRESOLVED" and not o["conflict_assessment"]["real_conflict_established"]
def test_nary_graph():
    r=reqs()+[{"requirement_id":"R3","source_norms":["N3"],"type":"CONTINUITY","protected_interest":"I3","affected_entities":["E3"],"condition":"Z","scope":"S","time":"T","formalization":"F3","flexibility":"BOUNDED"}]
    a=alt("A","INCOMPATIBLE_UNDER_CURRENT_OPTION","INCOMPATIBLE_UNDER_CURRENT_OPTION"); a["compatibility"]["R3"]="INCOMPATIBLE_UNDER_CURRENT_OPTION"
    o=d.detect_normative_conflict(ca(),r,[a],search_completeness="ADEQUATE_SEARCH"); assert len(o["normative_conflict_graph"]["nary_conflict_sets"][0]["requirements"])==3 and not o["normative_conflict_graph"]["pairwise_only"]
def test_tamper_detected():
    o=d.detect_normative_conflict(ca(),reqs(),[alt("A","COMPATIBLE","COMPATIBLE")],search_completeness="ADEQUATE_SEARCH"); o["winner_selected"]=True; assert d.verify_conflict_assessment(o)["status"]=="FAIL"
def test_determinism_nonmutation():
    r=reqs(); a=[alt("A","COMPATIBLE","COMPATIBLE")]; r0=copy.deepcopy(r); a0=copy.deepcopy(a)
    x=d.detect_normative_conflict(ca(),r,a,search_completeness="ADEQUATE_SEARCH"); y=d.detect_normative_conflict(ca(),r,a,search_completeness="ADEQUATE_SEARCH"); assert x==y and r==r0 and a==a0
def test_boundaries():
    m=d.manifest(); assert m["scope"]=="P160-D_ONLY" and "normative_conflict_resolution.resolve_conflict" in m["does_not_call"]; assert not m["boundaries"]["conflict_arbitration_performed"] and not m["boundaries"]["winner_selected"] and not m["boundaries"]["p160e_opened"] and not m["boundaries"]["p161_opened"]
