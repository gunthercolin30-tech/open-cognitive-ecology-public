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
import json, py_compile, tempfile
from ontology.reference_frame_merging import ReferenceFrameMerging

def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw6_compile_") as tmp:
        py_compile.compile(str(Path("ontology/reference_frame_merging.py")), cfile=str(Path(tmp)/"reference_frame_merging.pyc"), doraise=True)
    with tempfile.TemporaryDirectory(prefix="oce_aw6_") as tmp:
        detector=ReferenceFrameMerging(root=Path(tmp))
        first=detector.step(inputs=build_context(),persist=True)
        second=detector.step(inputs=build_context(),persist=False)
        assert first["reference_frame_merging_ready"] is True
        assert first["detected_merge_count"]==1
        assert first["merges"][0]["merge_status"]=="REFERENCE_FRAME_MERGE_DETECTED_FUNCTIONALLY"
        assert first["result_hash"]==second["result_hash"]
        p=Path(first["output_path"])
        assert p.exists() and json.loads(p.read_text())["detected_merge_count"]==1
        assert first["collective_consciousness_proven"] is False
    print("AW6_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()
