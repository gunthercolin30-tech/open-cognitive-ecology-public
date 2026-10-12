from __future__ import annotations
import json, py_compile, tempfile
from pathlib import Path
from ontology.multi_rf_registry import MultiRFRegistry
from ontology.interaction_graph import InteractionGraph
from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector

ROOT = Path.home() / "open-cognitive-ecology"

def context():
    registry = MultiRFRegistry().step(inputs={"rf_records":[{"rf_id":"RF-A"},{"rf_id":"RF-B"}]},persist=False)
    graph = InteractionGraph().step(inputs={"multi_rf_registry":registry,"interactions":[{"interaction_id":"I-AB","source_rf_id":"RF-A","target_rf_id":"RF-B"}]},persist=False)
    evidence = {"RF-A|RF-B": {"similarity":0.9,"alignment":0.85,"symbolic_reference":0.8,"structural_invariance":0.82,"reproducibility":0.78,"evidence_quality":0.9,"source_refs":["synthetic-aw3"]}}
    return {"multi_rf_registry":registry,"interaction_graph":graph,"pair_evidence":evidence}

def main():
    for p in [ROOT/"ontology/shared_reference_frame_detector.py",ROOT/"aw3_fast_acceptance_suite.py",ROOT/"shared_reference_frame_detector_final_lock.py"]:
        py_compile.compile(str(p),cfile=str(Path("/private/tmp")/(p.name+".aw3.pyc")),doraise=True)
    a=SharedReferenceFrameDetector().step(inputs=context(),persist=False); b=SharedReferenceFrameDetector().step(inputs=context(),persist=False)
    assert a["shared_reference_frame_detection_status"]=="SHARED_REFERENCE_FRAME_DETECTION_READY"
    assert a["detected_pair_count"]==1 and a["pair_count"]==1 and a["detection_hash"]==b["detection_hash"]
    with tempfile.TemporaryDirectory(prefix="oce_aw3_") as tmp:
        d=SharedReferenceFrameDetector(root=Path(tmp)); p=d.step(inputs=context(),persist=True)
        assert p["persisted"] is True; payload=json.loads(Path(p["output_path"]).read_text()); assert payload["detection_hash"]==p["detection_hash"]
    assert a["collective_consciousness_proven"] is False and a["functional_conclusion_only"] is True
    print("AW3_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()
