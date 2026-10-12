from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector

def base(extra):
 e={"similarity":0.95,"alignment":0.95,"symbolic_reference":0.95,"structural_invariance":0.95,"reproducibility":0.95,"evidence_quality":0.95}; e.update(extra)
 return {"rf_records":[{"rf_id":"RF-A"},{"rf_id":"RF-B"}],"interactions":[{"interaction_id":"I","source_rf_id":"RF-A","target_rf_id":"RF-B"}],"pair_evidence":{"RF-A|RF-B":e}}
def main():
 for flag in ["translation_only","common_controller","copy_or_clone_explanation","lexical_overlap_only","single_observation_only"]:
  r=SharedReferenceFrameDetector().step(inputs=base({flag:True}),persist=False)
  assert r["detected_pair_count"]==0 and flag in r["pair_results"][0]["false_positive_blockers"]
 print("AW3_FALSE_POSITIVE_CONTROLS_OK")
if __name__=="__main__": main()
