from __future__ import annotations
import json, py_compile, tempfile
from pathlib import Path
from ontology.coalition_detector import CoalitionDetector
from ontology.multi_rf_registry import MultiRFRegistry
from ontology.interaction_graph import InteractionGraph
from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector

def build_context():
    registry = MultiRFRegistry().step(inputs={"rf_records":[{"rf_id":"RF-A"},{"rf_id":"RF-B"},{"rf_id":"RF-C"}]}, persist=False)
    interactions = [
        {"interaction_id":"AB","source_rf_id":"RF-A","target_rf_id":"RF-B","interaction_type":"COOPERATION","directed":False,"weight":0.9,"confidence":0.9},
        {"interaction_id":"AC","source_rf_id":"RF-A","target_rf_id":"RF-C","interaction_type":"COORDINATION","directed":False,"weight":0.85,"confidence":0.9},
        {"interaction_id":"BC","source_rf_id":"RF-B","target_rf_id":"RF-C","interaction_type":"COOPERATION","directed":False,"weight":0.88,"confidence":0.9},
    ]
    graph = InteractionGraph().step(inputs={"multi_rf_registry":registry,"interactions":interactions}, persist=False)
    pair = {key:{"similarity":0.82,"alignment":0.81,"symbolic_reference":0.78,"structural_invariance":0.8,"reproducibility":0.84,"evidence_quality":0.9,"source_refs":["synthetic-aw4"]} for key in ["RF-A|RF-B","RF-A|RF-C","RF-B|RF-C"]}
    shared = SharedReferenceFrameDetector().step(inputs={"multi_rf_registry":registry,"interaction_graph":graph,"pair_evidence":pair}, persist=False)
    candidate = {"coalition_id":"COAL-ABC","member_rf_ids":["RF-A","RF-B","RF-C"],"cohesion_score":0.86,"reciprocity_score":0.82,"shared_goal_score":0.9,"coordination_score":0.88,"temporal_stability_score":0.8,"resilience_score":0.76,"boundary_score":0.73,"evidence_quality":0.91,"observation_count":12,"valid_from_utc":"2026-07-01T00:00:00Z","valid_until_utc":"2026-07-11T00:00:00Z","member_contributions":{"RF-A":0.8,"RF-B":0.76,"RF-C":0.72},"source_refs":["synthetic-aw4"]}
    return {"multi_rf_registry":registry,"interaction_graph":graph,"shared_reference_frame_detection":shared,"coalition_candidates":[candidate]}

ROOT=Path.home()/"open-cognitive-ecology"
def main():
    for p in [ROOT/"ontology/coalition_detector.py",ROOT/"aw4_fast_acceptance_suite.py",ROOT/"coalition_detector_final_lock.py"]:
        py_compile.compile(str(p),cfile=str(Path("/private/tmp")/(p.name+".aw4.pyc")),doraise=True)
    a=CoalitionDetector().step(inputs=build_context(),persist=False); b=CoalitionDetector().step(inputs=build_context(),persist=False)
    assert a["coalition_detection_status"]=="RF_COALITION_DETECTION_READY"
    assert a["detected_coalition_count"]==1 and a["detection_hash"]==b["detection_hash"]
    with tempfile.TemporaryDirectory(prefix="oce_aw4_") as tmp:
        d=CoalitionDetector(root=Path(tmp)); p=d.step(inputs=build_context(),persist=True)
        assert p["persisted"] is True and json.loads(Path(p["output_path"]).read_text())["detection_hash"]==p["detection_hash"]
    assert a["collective_consciousness_proven"] is False and a["functional_conclusion_only"] is True
    print("AW4_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()
