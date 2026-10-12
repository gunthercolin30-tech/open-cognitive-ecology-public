from ontology.occ1h_a100_rrpc_materiality_closure import materiality
def blocker_space():
 r=materiality()
 assert r["rrp12"]=="ROOT + BLOCKING_INCONCLUSIVE"
 return {**r,
  "resolution_space_checked":[
   "existing P159 executable CIS→permanent-sovereignty transition",
   "existing constitutional authorization binding for that transition",
   "existing end-to-end provenance/continuity evidence for that transition",
   "existing independent empirical evidence sufficient to requalify A100"],
  "rrp13":"BLOCKER_RESOLUTION_SPACE_EXHAUSTED",
  "rrp14":"NO_ADMISSIBLE_EXISTING_RESOLUTION_CANDIDATE_PROVEN",
  "rrp15":"BLOCKER_RESOLUTION_EXPERIMENT_NOT_ADMISSIBLE_WITH_CURRENT_EVIDENCE",
  "rrp16":"BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE",
  "resolution_candidate":"NONE","experiment_executed":False,"rrp_e_required":True,
  "current_verdict":"INCONCLUSIVE","transition_materialized":False,
  "production_runtime_modified":False,"criticality_changed":False,
  "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
