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
    d=ReferenceFrameMerging(); a=d.step(inputs=build_context(),persist=False)["merges"][0]
    ctx=deepcopy(build_context()); c=ctx["merge_candidates"][0]; c["source_rf_ids"].reverse(); c["source_refs"].reverse()
    b=d.step(inputs=ctx,persist=False)["merges"][0]
    assert a["source_rf_ids"]==b["source_rf_ids"] and a["merge_hash"]==b["merge_hash"]
    changed=deepcopy(build_context()); changed["merge_candidates"][0]["information_loss_score"]=0.2
    c=d.step(inputs=changed,persist=False)["merges"][0]
    assert a["merge_hash"]!=c["merge_hash"]
    print("AW6_ORDER_AND_HASH_OK")
if __name__=="__main__": main()
