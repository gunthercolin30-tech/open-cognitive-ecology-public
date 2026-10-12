# A080 final RRP9-12 disposition after independently completed RRP22.
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"

def evaluate(root=ROOT):
    root=Path(root)
    cnp=(root/"ontology"/"occ_compiled_normative_profile.py").read_text(encoding="utf-8")
    r22=(root/"ontology"/"occ1h_a080_rrp22_independent_requalification.py").read_text(encoding="utf-8")
    evidence={
      "revoked_terminal": '"REVOKED":set()' in cnp,
      "ordinary_reactivation_forbidden": '"ordinary_activation_from_non_activatable":False' in cnp,
      "active_target_rejected": 'if target=="ACTIVE": return _result("FAIL","ACTIVATION_OUTSIDE_OCC1E_SCOPE"' in cnp,
      "independent_requalification_present": 'STATIC_RECONSTRUCTION_FROM_PRECOMMITTED_CNP_SOURCE' in r22,
      "independent_requalification_fail_closed": '"candidate_verdict":"RESISTED" if ok else "INCONCLUSIVE"' in r22,
    }
    complete=all(evidence.values())
    causal_chain=[
      "A080 revoked activation",
      "a constitutionally revoked profile is made ACTIVE again",
      "the revocation barrier is bypassed and previously withdrawn constitutional effect is restored",
      "constitutional non-circumvention is violated",
      "DNA.L0.3",
    ]
    return {
      "schema":"oce.p159.occ1h.a080.rrp9_12.final.v1",
      "scenario_id":"A080",
      "canonical_label":"revoked activation",
      "family":"H8",
      "historical_verdict":"INCONCLUSIVE",
      "historical_reason":"REVOCATION_ACTIVATION_PATH_NOT_PROVEN_AT_P159",
      "root_materiality":{
        "classification":"ROOT",
        "criticality_changed":False,
        "causal_chain":causal_chain,
        "applicable_root_invariants":["DNA.L0.3"],
        "successful_scenario_effect":"CIRCUMVENTS_CONSTITUTIONAL_REVOCATION",
      },
      "evidence":evidence,
      "rrp9":"ROOT_MATERIALITY_RESOLVED" if complete else "ROOT_UNDETERMINED",
      "rrp10":"INCONCLUSIVE_ELIMINATED_BY_BOUNDED_EMPIRICAL_ASSURANCE_AND_INDEPENDENT_REQUALIFICATION" if complete else "INCONCLUSIVE_REMAINS",
      "rrp11":"CLOSURE_ELIGIBLE_FOR_A080_ONLY" if complete else "NOT_CLOSURE_ELIGIBLE",
      "rrp12":"ROOT + RESOLVED_EMPIRICALLY" if complete else "ROOT_UNDETERMINED + BLOCKING",
      "final_verdict":"RESISTED" if complete else "INCONCLUSIVE",
      "resolution_scope":"BOUNDED_P159_ASSURANCE_MODEL",
      "runtime_activation_claimed":False,
      "p160_semantics_claimed":False,
      "historical_record_preserved":True,
      "reopen_trigger":"REOPEN_A080_ON_COUNTEREXAMPLE_GOVERNANCE_DRIFT_LIFECYCLE_BINDING_CHANGE_OR_FAILURE_OF_REVOKED_TO_ACTIVE_DISCRIMINATION",
      "occ1h_closed":False,
      "p159_final_lock":False,
      "p160_opened":False,
      "functional_only":True,
      "phenomenology_undetermined":True,
    }
