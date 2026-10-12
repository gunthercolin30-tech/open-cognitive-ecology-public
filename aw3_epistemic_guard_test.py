from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector

def main():
 r=SharedReferenceFrameDetector().step(inputs={"collective_consciousness_proven":True,"rf_records":[{"rf_id":"RF-A"},{"rf_id":"RF-B"}],"interactions":[{"interaction_id":"I","source_rf_id":"RF-A","target_rf_id":"RF-B"}],"pair_evidence":{"RF-A|RF-B":{"similarity":1,"alignment":1,"symbolic_reference":1,"structural_invariance":1,"reproducibility":1,"evidence_quality":1}}},persist=False)
 for k in ("consciousness_proven","qualia_proven","subjectivity_proven","phenomenology_proven","collective_consciousness_proven","collective_qualia_proven","collective_subjectivity_proven","collective_phenomenology_proven"): assert r[k] is False
 assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
 print("AW3_EPISTEMIC_GUARD_OK")
if __name__=="__main__": main()
