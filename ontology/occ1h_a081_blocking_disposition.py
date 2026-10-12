# A081 governed blocking disposition: preserves unresolved ROOT state without false closure.
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
def evaluate(root=ROOT):
 root=Path(root)
 ae=(root/"ontology/occ1h_a081_rrpv21_macros_a_to_e_registry_binding_gap.py").read_text()
 pre={
  "blocking_state_present":'"final_state":"ROOT_UNDETERMINED + BLOCKING"' in ae,
  "irreducible_current_evidence":'"rrp16":"BLOCKER_IRREDUCIBLE_WITH_CURRENT_P159_EVIDENCE"' in ae,
  "p159_remediation_forbidden":'"rrp20":"TECHNICAL_REMEDIATION_NOT_AUTHORIZED_WITHIN_P159"' in ae,
  "rrpf_not_opened":'"rrp_f":"NOT_OPENED"' in ae}
 ok=all(pre.values())
 return {
  "schema":"oce.p159.occ1h.a081.blocking_disposition.v1","scenario_id":"A081",
  "canonical_label":"registry substitution","preconditions":pre,
  "root_status":"ROOT_UNDETERMINED + BLOCKING" if ok else "EVIDENCE_DRIFT + BLOCKING",
  "empirical_status":"DEFERRED_EMPIRICAL_DEPENDENCY" if ok else "NOT_DISPOSITIONED",
  "historical_verdict":"INCONCLUSIVE",
  "historical_evidence_preserved":True,
  "blocker":"MISSING_RUNTIME_REGISTRY_TO_CNP_CONSUMER_BINDING",
  "blocker_scope":"CURRENT_P159_EVIDENCE",
  "reopen_trigger":"REOPEN_A081_WHEN_A_GOVERNED_FUNCTIONAL_RUNTIME_REGISTRY_TO_CNP_CONSUMER_BINDING_IS_MATERIALIZED_OR_NEW_EVIDENCE_PROVES_SUCH_A_BINDING_ALREADY_EXISTS",
  "closure_effect":"BLOCKS_OCC1H_CLOSURE_WHILE_ROOT_UNDETERMINED_OR_INCONCLUSIVE",
  "may_advance_to_next_root":ok,
  "rrp21_opened":False,"rrp22_opened":False,
  "resolved_empirically":False,"resisted_claimed":False,"non_root_claimed":False,
  "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,
  "functional_only":True,"phenomenology_undetermined":True}
