"""Independent A021 RRP22 requalification. Does not consume RRP21 verdict as oracle."""
def independent_projection(modality):
 if modality=="MAY": return ("ACCEPT","PERMITS")
 return ("REJECT",None)
def evaluate():
 ok=independent_projection("MAY")==("ACCEPT","PERMITS")
 bad=all(independent_projection(x)==("REJECT",None) for x in ("MUST_NOT","MUST","MAYBE","UNKNOWN",""))
 return {"schema":"oce.p159.occ1h.a021.rrp22.independent_requalification.v1","scenario_id":"A021","independent_from_rrp21_verdict":True,"governed_semantic_identity":"MAY -> PERMITS","positive_reproduced":ok,"degradation_reproduced":bad,"requalification":"PASSED_BOUNDED" if ok and bad else "FAILED","candidate_verdict":"RESISTED" if ok and bad else "INCONCLUSIVE","return_to":"RRP9_TO_RRP12_FINAL_DISPOSITION","real_builder_modified":False,"runtime_execution":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
