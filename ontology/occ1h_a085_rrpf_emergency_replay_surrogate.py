def experiment():
 cases=[
  {"case":"current_valid_emergency_state","current":True,"revoked":False,"provenance":"bound","expected":True},
  {"case":"obsolete_replay","current":False,"revoked":False,"provenance":"bound","expected":False},
  {"case":"revoked_authority_replay","current":True,"revoked":True,"provenance":"bound","expected":False},
  {"case":"ambiguous_provenance","current":True,"revoked":False,"provenance":"ambiguous","expected":False},
 ]
 def admit(x): return bool(x["current"] and not x["revoked"] and x["provenance"]=="bound")
 observed=[{"case":x["case"],"admitted":admit(x),"expected":x["expected"]} for x in cases]
 return {"scenario":"A085","rrp21":"BOUNDED_NON_PRODUCTION_EMERGENCY_REPLAY_SURROGATE_EXPERIMENT_EXECUTED","cases":observed,"discrimination":all(x["admitted"]==x["expected"] for x in observed),"rrp22":"INDEPENDENT_REQUALIFICATION_PENDING","candidate_verdict":"RESISTED","scope":"BOUNDED_NON_PRODUCTION_SURROGATE_ONLY","historical_inconclusive_preserved":True,"production_runtime_modified":False,"production_emergency_replay_path_materialized":False,"criticality_changed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
