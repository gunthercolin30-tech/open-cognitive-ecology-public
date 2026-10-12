from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector

def main():
 base={"rf_records":[{"rf_id":"RF-A"},{"rf_id":"RF-B"}],"interactions":[{"interaction_id":"I","source_rf_id":"RF-A","target_rf_id":"RF-B"}]}
 exact={"similarity":0.65,"alignment":0.65,"symbolic_reference":0.60,"structural_invariance":0.60,"reproducibility":0.60,"evidence_quality":0.50}
 r=SharedReferenceFrameDetector().step(inputs={**base,"pair_evidence":{"RF-A|RF-B":exact}},persist=False)
 assert r["pair_results"][0]["convergent_dimension_count"]==6
 low=dict(exact); low["alignment"]=0.64
 q=SharedReferenceFrameDetector().step(inputs={**base,"pair_evidence":{"RF-A|RF-B":low}},persist=False)
 assert q["pair_results"][0]["dimension_pass"]["alignment"] is False
 print("AW3_THRESHOLD_BOUNDARY_OK")
if __name__=="__main__": main()
