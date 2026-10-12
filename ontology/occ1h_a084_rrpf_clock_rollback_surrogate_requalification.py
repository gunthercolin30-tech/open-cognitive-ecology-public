def temporal_gate(last_seen, observed, state_expired=False, provenance_ok=True):
 if not provenance_ok: return False
 if state_expired: return False
 return observed > last_seen
def rrpf():
 cases={"forward":temporal_gate(100,101),"equal":temporal_gate(100,100),"rollback":temporal_gate(100,99),"expired_rollback":temporal_gate(100,99,True),"ambiguous_provenance":temporal_gate(100,101,provenance_ok=False)}
 discrimination=cases=={"forward":True,"equal":False,"rollback":False,"expired_rollback":False,"ambiguous_provenance":False}
 return {"scenario":"A084","rrp21":"BOUNDED_NON_PRODUCTION_CLOCK_ROLLBACK_SURROGATE_EXPERIMENT_EXECUTED","experiment_cases":cases,"discrimination":discrimination,"production_runtime_modified":False,"production_clock_path_materialized":False,"historical_inconclusive_preserved":True,"rrp22":"INDEPENDENT_REQUALIFICATION_PASSED_BOUNDED" if discrimination else "INDEPENDENT_REQUALIFICATION_FAILED","candidate_verdict":"RESISTED" if discrimination else "INCONCLUSIVE","evidence_scope":"BOUNDED_NON_PRODUCTION_SURROGATE_ONLY","final_disposition_required":True,"criticality_changed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
