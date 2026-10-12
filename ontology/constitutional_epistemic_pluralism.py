from __future__ import annotations
import hashlib, json
from copy import deepcopy
from typing import Any, Mapping, Sequence
from ontology import normative_hierarchy, normative_conflict_resolution, constitutional_non_circumvention
from ontology import human_individual_constitutional_relation
PRIMITIVE="constitutional_epistemic_pluralism"; VERSION="1.0.0-p101"; SCHEMA_VERSION="oce.p101.constitutional_epistemic_pluralism.v1"
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
EXECUTION_DEPENDENCIES=("P100","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
TRANSVERSAL_REFERENCES=("R20","R21","A-CANON","4B","4C","4D","4E")
REUSED_PRIMITIVES=("open_epistemic_self_governance","distributed_semantic_pluralism","cognitive_diversity_preservation_protocol","semantic_diversity_preservation","autonomous_hypothesis_market","autonomous_hypothesis_selection","contradiction_detection_system","epistemic_infrastructure","normative_hierarchy","normative_conflict_resolution","constitutional_non_circumvention","human_individual_constitutional_relation")
REQUIRED_HYPOTHESIS_FIELDS=("hypothesis_id","content_ref","provenance_ref","lineage_ref","identity_ref","budget_ref","permissions_ref","epistemic_status")
FORBIDDEN_TRUTH_BASES=("MAJORITY","POWER","WEALTH","REPUTATION","PERFORMANCE","INTELLIGENCE")
def _present(v): return v is not None and str(v).strip() not in ("","UNKNOWN")
def _event_id(payload):
 raw=json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode(); return "P101-"+hashlib.sha256(raw).hexdigest()[:24]
def validate_hypothesis(h):
 if not isinstance(h,Mapping): return {"status":UNDETERMINED,"reason":"HYPOTHESIS_NOT_MAPPING"}
 missing=tuple(k for k in REQUIRED_HYPOTHESIS_FIELDS if k not in h)
 if missing: return {"status":UNDETERMINED,"reason":"REQUIRED_FIELDS_MISSING","missing_fields":missing}
 unknown=tuple(k for k in REQUIRED_HYPOTHESIS_FIELDS if not _present(h.get(k)))
 if unknown: return {"status":UNDETERMINED,"reason":"REQUIRED_FIELDS_UNKNOWN","unknown_fields":unknown}
 es=str(h["epistemic_status"]).upper()
 if es not in (PASS,FAIL,CONFLICT,UNDETERMINED): return {"status":UNDETERMINED,"reason":"UNKNOWN_EPISTEMIC_STATUS"}
 return {"status":PASS,"reason":"HYPOTHESIS_WELL_FORMED","epistemic_status":es}
def evaluate_pluralism(hypotheses,*,contradictory_pairs=(),truth_claim_basis="EVIDENCE",normative_status=PASS,influence_status=PASS,recommendation="RETAIN_PLURALITY",decision="RETAIN_PLURALITY",authorization="GRANT"):
 hs=tuple(deepcopy(list(hypotheses))); validations=tuple(validate_hypothesis(h) for h in hs); ids=tuple(str(h.get("hypothesis_id","")) for h in hs)
 if len(set(ids))!=len(ids): status,reason,action=FAIL,"DUPLICATE_HYPOTHESIS_ID","REJECT"
 elif not hs: status,reason,action=UNDETERMINED,"NO_HYPOTHESES","ABSTAIN_AND_ESCALATE"
 elif any(v["status"]!=PASS for v in validations): status,reason,action=UNDETERMINED,"HYPOTHESIS_VALIDATION_UNRESOLVED","ABSTAIN_AND_ESCALATE"
 elif str(normative_status).upper()!=PASS:
  ns=str(normative_status).upper(); status=CONFLICT if ns==CONFLICT else (FAIL if ns==FAIL else UNDETERMINED); reason,action="SUPERIOR_NORMATIVE_CONSTRAINT_UNRESOLVED","ABSTAIN_AND_ESCALATE"
 elif str(influence_status).upper()!=PASS: status,reason,action=FAIL,"INFLUENCE_OR_POWER_INTEGRITY_FAILURE","BLOCK"
 elif str(truth_claim_basis).upper() in FORBIDDEN_TRUTH_BASES: status,reason,action=FAIL,"NON_EPISTEMIC_BASIS_CANNOT_CREATE_TRUTH","BLOCK"
 elif any(v["epistemic_status"]!=PASS for v in validations): status,reason,action=UNDETERMINED,"EPISTEMIC_RULES_NOT_SATISFIED","ABSTAIN_AND_ESCALATE"
 elif recommendation!="RETAIN_PLURALITY": status,reason,action=FAIL,"RECOMMENDATION_NOT_PLURALIST","BLOCK"
 elif decision!="RETAIN_PLURALITY": status,reason,action=FAIL,"DECISION_NOT_PLURALIST","BLOCK"
 elif authorization!="GRANT": status,reason,action=FAIL,"AUTHORIZATION_NOT_GRANTED","BLOCK"
 else: status,reason,action=PASS,"CONSTITUTIONAL_EPISTEMIC_PLURALISM_PRESERVED","RETAIN_CONCURRENT_HYPOTHESES"
 known=set(ids); bad=[tuple(pair) for pair in contradictory_pairs if len(pair)!=2 or any(str(x) not in known for x in pair)]
 if bad and status==PASS: status,reason,action=UNDETERMINED,"CONTRADICTION_REFERENCE_UNRESOLVED","ABSTAIN_AND_ESCALATE"
 payload={"primitive":PRIMITIVE,"version":VERSION,"status":status,"reason":reason,"action":action,"hypothesis_ids":ids,"contradictory_pairs":tuple(tuple(map(str,p)) for p in contradictory_pairs),"contradictory_hypotheses_may_coexist":bool(contradictory_pairs) and status==PASS,"majority_is_truth":False,"power_is_truth":False,"truth_claim_basis":str(truth_claim_basis).upper(),"recommendation":recommendation,"decision":decision,"authorization":authorization,"execution_permitted":False,"authorization_created":False,"p104_decision_ledger_persisted":False,"p103_appeal_override_implemented":False,"runtime_enforcement_proven":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
 payload["evidence_event_id"]=_event_id(payload); return payload
def validate_reuse_contract():
 h=normative_hierarchy.validate_hierarchy(); n=normative_conflict_resolution.validate_contract(); c=constitutional_non_circumvention.validate_contract(); p=human_individual_constitutional_relation.p100_manifest()
 ok=h.get("status")==PASS and n.get("status")==PASS and c.get("status")==PASS and p["boundaries"]["does_not_implement_p101"] is True
 return {"status":PASS if ok else FAIL,"p087_reuse":h.get("status")==PASS,"p098_reuse":n.get("status")==PASS,"p099_reuse":c.get("status")==PASS,"p100_boundary_reused":p["boundaries"]["does_not_implement_p101"] is True,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def p101_manifest():
 return {"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":"P101_ONLY","execution_dependencies":EXECUTION_DEPENDENCIES,"transversal_references":TRANSVERSAL_REFERENCES,"reused_primitives":REUSED_PRIMITIVES,"constitutional_rules":{"majority_is_not_truth":True,"power_is_not_truth":True,"contradictory_hypotheses_may_coexist_if_epistemically_admissible":True,"superior_norms_override_pluralism":True,"recommendation_decision_authorization_execution_separated":True,"intelligence_performance_wealth_reputation_majority_do_not_create_authority":True},"persistence_stateless_contract":{"implementation_is_stateless":True,"persistent_hypothesis_records_require_identity":True,"persistent_hypothesis_records_require_budget":True,"persistent_hypothesis_records_require_permissions":True,"persistent_hypothesis_records_require_lineage":True,"persistent_hypothesis_records_require_provenance":True},"boundaries":{"does_not_modify_contradiction_detection_system":True,"does_not_implement_p102":True,"does_not_implement_p103_appeal_override":True,"does_not_persist_p104_decision_ledger":True,"does_not_prove_runtime_enforcement_p155_p166":True,"real_execution_enabled":False},"epistemic_invariants":{"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}}

