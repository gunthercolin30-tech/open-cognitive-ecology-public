from ontology.multi_rf_registry import MultiRFRegistry
from ontology.interaction_graph import InteractionGraph
from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector
registry=MultiRFRegistry().step(inputs={"rf_records":[{"rf_id":"RF-A"},{"rf_id":"RF-B"}]},persist=False)
graph=InteractionGraph().step(inputs={"multi_rf_registry":registry,"interactions":[{"interaction_id":"I-AB","source_rf_id":"RF-A","target_rf_id":"RF-B"}]},persist=False)
READY_OR_SYNTHETIC_CONTEXT={"multi_rf_registry":registry,"interaction_graph":graph,"pair_evidence":{"RF-A|RF-B":{"similarity":0.9,"alignment":0.9,"symbolic_reference":0.8,"structural_invariance":0.8,"reproducibility":0.8,"evidence_quality":0.9}}}
def main():
 r=SharedReferenceFrameDetector().step(inputs=READY_OR_SYNTHETIC_CONTEXT,persist=False)
 assert r["primitive"]=="SHARED_REFERENCE_FRAME_DETECTOR" and r["step"]=="AW3"
 assert r["shared_reference_frame_detection_ready"] is True and r["detected_pair_count"]==1
 assert r["collective_consciousness_proven"] is False and r["phenomenology_undetermined"] is True
 print("AW3_FINAL_LOCK_OK")
if __name__=="__main__": main()
