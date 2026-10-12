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
import tempfile
from ontology.reference_frame_fragmentation import ReferenceFrameFragmentation
def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw7_corrupt_") as tmp:
        d=ReferenceFrameFragmentation(root=Path(tmp)); p=d.output_dir/"latest_reference_frame_fragmentation.json"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text("{broken",encoding="utf-8")
        r=d.step(inputs={**build_context(),"load_existing":True},persist=False)
        assert r["reference_frame_fragmentation_ready"] is True and r["detected_fragmentation_count"]==1 and r["previous_result_loaded"] is False
    print("AW7_CORRUPTION_FALLBACK_OK")
if __name__=="__main__": main()
