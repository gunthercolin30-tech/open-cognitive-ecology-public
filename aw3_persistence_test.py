import tempfile
from pathlib import Path
from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector

def main():
 ctx={"rf_records":[{"rf_id":"RF-A"},{"rf_id":"RF-B"}],"interactions":[{"interaction_id":"I","source_rf_id":"RF-A","target_rf_id":"RF-B"}],"pair_evidence":{"RF-A|RF-B":{"similarity":0.9,"alignment":0.9,"symbolic_reference":0.9,"structural_invariance":0.9,"reproducibility":0.9,"evidence_quality":0.9}}}
 with tempfile.TemporaryDirectory(prefix="oce_aw3_persist_") as tmp:
  d=SharedReferenceFrameDetector(root=Path(tmp)); a=d.step(inputs=ctx,persist=True); b=d.step(inputs=ctx,persist=True)
  assert a["detection_hash"]==b["detection_hash"] and a["persisted"] is True
  c=d.step(inputs={**ctx,"load_existing":True},persist=False); assert c["detection_hash"]==a["detection_hash"]
 print("AW3_PERSISTENCE_AND_RESTART_OK")
if __name__=="__main__": main()
