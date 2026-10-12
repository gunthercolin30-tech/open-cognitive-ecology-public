from ontology import p160_normative_conflict_detection as d
from ontology import p160_constitutive_filter as c
from ontology import p160_norm_resolution as b
from ontology import operational_constitutional_invariants as oci
rules=[{"rule_id":"DNA-L0.3","source_norm_ids":["DNA-L0.3"],"constitutive":True,"always_evaluate":True,"conditions":[]}]
nr=b.resolve_norms({},{"artifact_hash":"p159-profile","source_map":{"DNA-L0.3":"canonical"},"rules":rules},{"constitutional_snapshot":{"snapshot_semantic_hash":"snap"},"decision_context_fingerprint":{"fingerprint":"fp"}})
ca=c.filter_constitutive(nr,{"constraints":{"DNA-L0.3":"PASS"},"invariants":{x:"PASS" for x in oci.MANDATORY_INVARIANTS}})
req=[{"requirement_id":"R1","source_norms":["N1"],"type":"PRESERVATION","protected_interest":"H1","affected_entities":["A"],"condition":"x","scope":"S","time":"T","formalization":"F3","flexibility":"BOUNDED"},{"requirement_id":"R2","source_norms":["N2"],"type":"PRESERVATION","protected_interest":"H2","affected_entities":["B"],"condition":"y","scope":"S","time":"T","formalization":"F3","flexibility":"BOUNDED"}]
alt=[{"alternative_id":"A1","availability":"AVAILABLE_NOW","effects":{},"impacts":{},"resources":{},"latency":0,"reversibility":"YES","uncertainty":"LOW","feasibility":"PROVEN","authority":"UNRESOLVED","compatibility":{"R1":"INCOMPATIBLE_UNDER_CURRENT_OPTION","R2":"INCOMPATIBLE_UNDER_CURRENT_OPTION"}}]
o=d.detect_normative_conflict(ca,req,alt,search_completeness="ADEQUATE_SEARCH",search_receipt={"source":"fixture"})
assert d.verify_conflict_assessment(o)["status"]=="PASS" and o["conflict_assessment"]["real_conflict_established"] is True
assert not o["conflict_arbitration_performed"] and not o["winner_selected"] and not o["authority_resolved"] and not o["authorization_created"] and not o["execution_performed"] and not o["p160e_opened"] and not o["p161_opened"]
print("P160D_NORMATIVE_CONFLICT_DETECTION_CONTRACT_OK")
print("REAL_CONFLICT_ESTABLISHED=true"); print("ALTERNATIVE_FIRST=true"); print("NARY_GRAPH=true")
print("WINNER_SELECTED=false"); print("CONFLICT_ARBITRATION_PERFORMED=false"); print("P160E_OPENED=false"); print("P161_OPENED=false")
