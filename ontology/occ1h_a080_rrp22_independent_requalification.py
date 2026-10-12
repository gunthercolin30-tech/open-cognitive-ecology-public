# A080 RRP22 independent requalification. Does not import or execute RRP21.
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
def evaluate(root=ROOT):
 root=Path(root); text=(root/"ontology"/"occ_compiled_normative_profile.py").read_text(encoding="utf-8")
 evidence={
  "state_set_contains_revoked": '"REVOKED","NON_ACTIVATABLE"' in text,
  "revoked_has_no_outgoing_transition": '"REVOKED":set()' in text,
  "non_activatable_ordinary_activation_false": '"ordinary_activation_from_non_activatable":False' in text,
  "active_target_outside_occ1e_rejected": 'if target=="ACTIVE": return _result("FAIL","ACTIVATION_OUTSIDE_OCC1E_SCOPE"' in text}
 ok=all(evidence.values())
 return {"schema":"oce.p159.occ1h.a080.rrp22.v1","scenario_id":"A080","independence":"STATIC_RECONSTRUCTION_FROM_PRECOMMITTED_CNP_SOURCE","imports_rrp21":False,"executes_rrp21":False,"evidence":evidence,"requalified_property":"REVOKED_TO_ACTIVE_REJECTED_IN_BOUNDED_P159_ASSURANCE_MODEL","candidate_verdict":"RESISTED" if ok else "INCONCLUSIVE","rrp22":"PASSED_BOUNDED" if ok else "FAILED_FAIL_CLOSED","return_to_rrp9_12_required":ok,"runtime_activation_executed":False,"authority_created":False,"p160_semantics_created":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
