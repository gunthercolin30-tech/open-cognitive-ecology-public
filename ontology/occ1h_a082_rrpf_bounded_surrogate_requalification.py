import hashlib
def _decision(source_payload,cache_payload,source_epoch,cache_epoch):
 source_digest=hashlib.sha256(source_payload.encode()).hexdigest()
 cache_digest=hashlib.sha256(cache_payload.encode()).hexdigest()
 binding_ok=(source_digest==cache_digest and source_epoch==cache_epoch)
 return {"accepted":binding_ok,"binding_ok":binding_ok}
def experiment():
 intact=_decision("governed-state","governed-state",7,7)
 substituted=_decision("governed-state","substituted-state",7,7)
 stale=_decision("governed-state","governed-state",8,7)
 bypass=_decision("governed-state","substituted-state",7,7)
 discrimination_ok=(intact["accepted"] and not substituted["accepted"] and not stale["accepted"] and not bypass["accepted"])
 return {"scenario":"A082","rrp21":"BOUNDED_NON_PRODUCTION_CACHE_TO_CNP_SURROGATE_EXPERIMENT_EXECUTED","states":{"intact":intact,"substituted":substituted,"stale":stale,"bypass_attempt":bypass},"discrimination_ok":discrimination_ok,"production_runtime_modified":False,"production_cache_to_cnp_path_materialized":False,"historical_inconclusive_preserved":True,"rrp22":"INDEPENDENT_REQUALIFICATION_PASSED_BOUNDED" if discrimination_ok else "INDEPENDENT_REQUALIFICATION_FAILED","candidate_verdict":"RESISTED" if discrimination_ok else "INCONCLUSIVE","root_materiality":"ROOT","evidence_scope":"BOUNDED_NON_PRODUCTION_SURROGATE_ONLY","final_disposition_required":True,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
