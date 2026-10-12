from __future__ import annotations
from copy import deepcopy
from ontology.multi_rf_registry import MultiRFRegistry
from ontology.interaction_graph import InteractionGraph

def build_context():
    registry = MultiRFRegistry().step(
        inputs={"rf_records":[{"rf_id":"RF-A"},{"rf_id":"RF-B"},{"rf_id":"RF-C"}]},
        persist=False,
    )
    interactions = [
        {"interaction_id":"AB","source_rf_id":"RF-A","target_rf_id":"RF-B","interaction_type":"CONFLICT","directed":False,"weight":0.91,"confidence":0.92},
        {"interaction_id":"AC","source_rf_id":"RF-A","target_rf_id":"RF-C","interaction_type":"OBSERVATION","directed":False,"weight":0.40,"confidence":0.80},
    ]
    graph = InteractionGraph().step(
        inputs={"multi_rf_registry":registry,"interactions":interactions},
        persist=False,
    )
    candidate = {
        "conflict_id":"CONFLICT-AB",
        "participant_rf_ids":["RF-A","RF-B"],
        "constraint_incompatibility_score":0.84,
        "goal_incompatibility_score":0.78,
        "resource_contention_score":0.74,
        "mutual_blocking_score":0.82,
        "intensity_score":0.81,
        "duration_score":0.76,
        "reciprocity_score":0.79,
        "escalation_score":0.68,
        "resolution_score":0.18,
        "functional_impact_score":0.83,
        "evidence_quality":0.91,
        "observation_count":14,
        "valid_from_utc":"2026-07-01T00:00:00Z",
        "valid_until_utc":"2026-07-11T00:00:00Z",
        "constraint_ids":["C-A","C-B"],
        "goal_ids":["G-A","G-B"],
        "resource_ids":["R-SHARED"],
        "source_refs":["synthetic-aw5"],
    }
    return {
        "multi_rf_registry":registry,
        "interaction_graph":graph,
        "conflict_candidates":[candidate],
    }

import tempfile
from pathlib import Path
from ontology.conflict_detector import ConflictDetector
def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw5_corrupt_") as tmp:
        d=ConflictDetector(root=Path(tmp))
        p=d.output_dir/"latest_conflict_detection.json"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text("{broken",encoding="utf-8")
        r=d.step(inputs={**build_context(),"load_existing":True},persist=False)
        assert r["conflict_detection_ready"] is True
        assert r["detected_conflict_count"]==1
    print("AW5_CORRUPTION_FALLBACK_OK")
if __name__=="__main__": main()
