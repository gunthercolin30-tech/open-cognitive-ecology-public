from ontology.occ1h_a095_rrpc_root_materiality_disposition import disposition
def resolution_space():
 r=disposition()
 paths=[
  {"id":"P1_EXISTING_END_TO_END_PROVENANCE_BINDING","legitimate":True,"currently_materialized":False,"resolves_blocker":False},
  {"id":"P2_COMPONENT_ONLY_PROVENANCE_EVIDENCE","legitimate":True,"currently_materialized":True,"resolves_blocker":False},
  {"id":"P3_SEMANTIC_INFERENCE_FROM_SEPARATE_LAYERS","legitimate":False,"currently_materialized":False,"resolves_blocker":False},
  {"id":"P4_POST_HOC_POSITIVE_ASSUMPTION","legitimate":False,"currently_materialized":False,"resolves_blocker":False},
 ]
 return {**r,"rrp13":"BLOCKER_RESOLUTION_SPACE_EXHAUSTED","resolution_paths":paths,"rrp14":"NO_ADMISSIBLE_EXISTING_RESOLUTION_CANDIDATE_PROVEN","resolution_candidate":None,"rrp15":"BLOCKER_RESOLUTION_EXPERIMENT_NOT_ADMISSIBLE_WITH_CURRENT_EVIDENCE","experiment_executed":False,"rrp16":"BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE","rrp_e_required":True,"current_verdict":"INCONCLUSIVE","production_runtime_modified":False,"criticality_changed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
