from ontology.multi_rf_registry import MultiRFRegistry


def build_context():
    registry = MultiRFRegistry().step(
        inputs={"rf_records":[
            {"rf_id":"RF-A"},
            {"rf_id":"RF-B"},
            {"rf_id":"RF-MERGED"},
            {"rf_id":"RF-C"},
        ]},
        persist=False,
    )
    candidate = {
        "merge_id":"MERGE-AB",
        "source_rf_ids":["RF-A","RF-B"],
        "successor_rf_id":"RF-MERGED",
        "compatibility_score":0.86,
        "structural_conservation_score":0.84,
        "functional_continuity_score":0.88,
        "lineage_traceability_score":0.95,
        "source_independence_reduction_score":0.82,
        "temporal_stability_score":0.79,
        "evidence_quality":0.91,
        "reversibility_score":0.72,
        "information_loss_score":0.12,
        "source_contributions":{"RF-A":0.76,"RF-B":0.74},
        "observation_count":12,
        "valid_from_utc":"2026-07-01T00:00:00Z",
        "valid_until_utc":"2026-07-11T00:00:00Z",
        "preserved_invariant_ids":["INV-IDENTITY","INV-GOAL","INV-MEMORY"],
        "lost_information_ids":["LOCAL-CACHE-B"],
        "source_status_after_merge":"TRANSFORMED_INTO_SUCCESSOR",
        "reversible":True,
        "rollback_reference":"ROLLBACK-MERGE-AB",
        "source_refs":["synthetic-aw6"],
    }
    return {"multi_rf_registry":registry,"merge_candidates":[candidate]}

from pathlib import Path
import tempfile
from ontology.reference_frame_merging import ReferenceFrameMerging

def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw6_corrupt_") as tmp:
        d=ReferenceFrameMerging(root=Path(tmp)); p=d.output_dir/"latest_reference_frame_merging.json"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text("{broken",encoding="utf-8")
        r=d.step(inputs={**build_context(),"load_existing":True},persist=False)
        assert r["reference_frame_merging_ready"] is True and r["detected_merge_count"]==1
    print("AW6_CORRUPTION_FALLBACK_OK")
if __name__=="__main__": main()
