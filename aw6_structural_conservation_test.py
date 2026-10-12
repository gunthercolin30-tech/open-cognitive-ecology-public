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

from copy import deepcopy
from ontology.reference_frame_merging import ReferenceFrameMerging

def main():
    ctx=deepcopy(build_context()); ctx["merge_candidates"][0]["structural_conservation_score"]=0.1
    r=ReferenceFrameMerging().step(inputs=ctx,persist=False)
    assert r["detected_merge_count"]==0 and r["merges"][0]["dimension_pass"]["structural_conservation"] is False
    print("AW6_STRUCTURAL_CONSERVATION_OK")
if __name__=="__main__": main()
