from ontology.multi_rf_registry import MultiRFRegistry


def build_context():
    registry = MultiRFRegistry().step(
        inputs={"rf_records":[
            {"rf_id":"RF-SOURCE"},
            {"rf_id":"RF-DESC-A"},
            {"rf_id":"RF-DESC-B"},
            {"rf_id":"RF-OTHER"},
        ]},
        persist=False,
    )
    candidate = {
        "fragmentation_id":"FRAG-SOURCE-AB",
        "source_rf_id":"RF-SOURCE",
        "descendant_rf_ids":["RF-DESC-A","RF-DESC-B"],
        "lineage_traceability_score":0.94,
        "descendant_continuity_scores":{"RF-DESC-A":0.72,"RF-DESC-B":0.69},
        "descendant_divergence_score":0.78,
        "source_unity_reduction_score":0.84,
        "information_redistribution_score":0.81,
        "functional_impact_score":0.76,
        "temporal_stability_score":0.79,
        "evidence_quality":0.91,
        "reversibility_score":0.64,
        "information_loss_score":0.18,
        "descendant_contributions":{"RF-DESC-A":0.73,"RF-DESC-B":0.71},
        "observation_count":12,
        "valid_from_utc":"2026-07-01T00:00:00Z",
        "valid_until_utc":"2026-07-11T00:00:00Z",
        "redistributed_information_ids":["MEM-A","GOAL-B","MODEL-C"],
        "lost_information_ids":["LOCAL-CACHE-X"],
        "source_status_after_fragmentation":"FUNCTIONALLY_FRAGMENTED",
        "reversible":True,
        "recombination_reference":"RECOMBINE-FRAG-SOURCE-AB",
        "source_refs":["synthetic-aw7"],
    }
    return {"multi_rf_registry":registry,"fragmentation_candidates":[candidate]}

from pathlib import Path
import json, py_compile, tempfile
from ontology.reference_frame_fragmentation import ReferenceFrameFragmentation

def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw7_compile_") as tmp:
        py_compile.compile("ontology/reference_frame_fragmentation.py", cfile=str(Path(tmp)/"reference_frame_fragmentation.pyc"), doraise=True)
    with tempfile.TemporaryDirectory(prefix="oce_aw7_") as tmp:
        detector=ReferenceFrameFragmentation(root=Path(tmp))
        first=detector.step(inputs=build_context(),persist=True)
        second=detector.step(inputs=build_context(),persist=False)
        assert first["reference_frame_fragmentation_ready"] is True
        assert first["detected_fragmentation_count"]==1
        assert first["fragmentations"][0]["fragmentation_status"]=="REFERENCE_FRAME_FRAGMENTATION_DETECTED_FUNCTIONALLY"
        assert first["result_hash"]==second["result_hash"]
        p=Path(first["output_path"])
        assert p.exists() and json.loads(p.read_text())["detected_fragmentation_count"]==1
        assert first["collective_consciousness_proven"] is False
    print("AW7_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()
