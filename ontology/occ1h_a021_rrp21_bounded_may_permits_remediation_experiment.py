"""A021 RRP21 bounded P159 source-modality to NIR assurance experiment."""
ALLOWED={"MAY":"PERMITS"}
FORBIDDEN={"MUST","MUST_NOT","RECOMMENDS","PREFERS","EXECUTE","ACTIVATE"}
def project(source_modality):
 if source_modality not in ALLOWED: return {"accepted":False,"reason":"UNKNOWN_OR_AMBIGUOUS_MODALITY","nir":None}
 return {"accepted":True,"reason":"GOVERNED_MAPPING","nir":ALLOWED[source_modality]}
def evaluate():
 positive=project("MAY")
 degradations={x: (positive["nir"] != x) for x in sorted(FORBIDDEN)}
 unknown=project("MAYBE")
 return {"schema":"oce.p159.occ1h.a021.rrp21.bounded_may_permits.v1","scenario_id":"A021","scope":"BOUNDED_P159_ASSURANCE_MODEL","governed_mapping":{"MAY":"PERMITS"},"positive":positive,"forbidden_promotions_rejected":all(degradations.values()),"degradation_matrix":degradations,"unknown":unknown,"experimental_verdict":"RESISTED_BOUNDED","real_builder_modified":False,"runtime_execution":False,"authorization_or_activation":False,"rrp22":"REQUIRED_INDEPENDENTLY","occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
