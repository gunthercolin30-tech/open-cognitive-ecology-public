# A081 RRP17-20 reopening: bounded assurance remediation, not real runtime materialization.
import json
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
def evaluate(root=ROOT):
 root=Path(root)
 cnp=(root/"ontology/occ_compiled_normative_profile.py").read_text()
 auth=json.loads((root/"oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json").read_text())
 ric=json.loads((root/"validation_artifacts/p159/occ1e/runtime_interface_contract_v1.json").read_text())
 a078=json.loads((root/"validation_artifacts/p159/occ1h/a078/a078_rrpv21_macros_a_to_e_existing_authority_v1.json").read_text())
 facts={
  "cnp_content_addressed":'"content_addressed":True' in cnp,
  "cnp_declares_consumer_types":'CONSUMERS=("NormResolver","CCAD","AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine")' in cnp,
  "cnp_runtime_graph_unproven":'"runtime_consumer_graph_proven":False' in cnp,
  "runtime_contract_is_contract_only":ric.get("contract_only") is True and ric.get("runtime_consumer_graph_proven") is False,
  "runtime_contract_no_execution_or_authorization":ric.get("execution_capability") is False and ric.get("authorization_capability") is False,
  "existing_development_authority":auth.get("human_confirmed") is True and auth.get("role")=="CONSTITUTIONAL_AUTHORITY" and "CONSTITUTIONAL_CHANGE" in auth.get("scope",[]),
  "a078_precedent_zero_dof_bounded_assurance":a078.get("RRP_E",{}).get("new_normative_degrees_of_freedom")==0 and a078.get("RRP_E",{}).get("rrp20")=="EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT"}
 ok=all(facts.values())
 return {"schema":"oce.p159.occ1h.a081.rrp17_20.bounded_registry_assurance_authorization.v1","scenario_id":"A081","facts":facts,
 "new_evidence_effect":"SUPERSEDES_PRIOR_NO_P159_REMEDIATION_CANDIDATE_ONLY_FOR_A_BOUNDED_ASSURANCE_FIXTURE" if ok else "NO_CHANGE",
 "RRP17":"BLOCKER_CAUSALLY_DECOMPOSED_AS_MISSING_REGISTRY_TO_CNP_IDENTITY_CHECK_AT_ASSURANCE_CONSUMER_BOUNDARY",
 "RRP18":"TECHNICAL_ASSURANCE_FORMALIZATION_GAP",
 "RRP19":{"design":"ISOLATED_CONTENT_ADDRESSED_REGISTRY_ASSURANCE_FIXTURE","consumer_domain":"CNP_DECLARED_CONSUMER_TYPES_ONLY","binding":"consumer_type -> exact CNP artifact_hash","substitution_discrimination":"reject registry entry whose bound CNP artifact_hash differs from independently supplied expected CNP artifact_hash","real_runtime_binding_claimed":False,"new_normative_degrees_of_freedom":0,"minimality":{"necessary":True,"independent":True,"sufficiently_exhaustive":True,"fixed_cardinality_forbidden":True}},
 "RRP20":"EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT" if ok else "BLOCKED",
 "technical_remediation_authorized":ok,
 "rrp21":"OPEN_FOR_BOUNDED_P159_ASSURANCE_EXPERIMENT" if ok else "NOT_OPENED",
 "rrp22":"REQUIRED_INDEPENDENTLY_AFTER_RRP21" if ok else "NOT_OPENED",
 "real_runtime_consumer_graph_materialized":False,"p160_semantics_invented":False,"canonical_source_modified":False,"authorization_created":False,"execution_performed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
