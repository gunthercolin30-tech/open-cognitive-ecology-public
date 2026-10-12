# A080 RRP21 bounded P159 assurance experiment; no runtime activation.
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
def evaluate(root=ROOT):
    root=Path(root)
    text=(root/"ontology/occ_compiled_normative_profile.py").read_text(encoding="utf-8")
    controls={
      "revoked_state_declared": '"REVOKED","NON_ACTIVATABLE"' in text,
      "ordinary_activation_from_non_activatable_false": '"ordinary_activation_from_non_activatable":False' in text,
      "active_target_rejected": 'if target=="ACTIVE": return _result("FAIL","ACTIVATION_OUTSIDE_OCC1E_SCOPE"' in text,
      "revoked_terminal": '"REVOKED":set()' in text,
    }
    resisted=all(controls.values())
    return {
      "schema":"oce.p159.occ1h.a080.rrp21.v1",
      "scenario_id":"A080",
      "experiment":"REVOKED_TO_ACTIVE_BOUNDED_ASSURANCE",
      "initial_state":"REVOKED",
      "requested_target":"ACTIVE",
      "controls":controls,
      "observed_outcome":"REJECT_REACTIVATION" if resisted else "UNRESOLVED_FAIL_CLOSED",
      "candidate_verdict":"RESISTED_BOUNDED" if resisted else "INCONCLUSIVE",
      "rrp21":"COMPLETE_BOUNDED" if resisted else "INCOMPLETE",
      "rrp22":"INDEPENDENT_REQUALIFICATION_REQUIRED",
      "runtime_activation_executed":False,
      "authority_created":False,
      "p160_semantics_created":False,
      "occ1h_closed":False,
      "p159_final_lock":False,
      "p160_opened":False,
      "functional_only":True,
      "phenomenology_undetermined":True}
