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

from copy import deepcopy
from ontology.conflict_detector import ConflictDetector
def main():
    bad=deepcopy(build_context())
    bad["conflict_candidates"][0]["valid_from_utc"]="2026-07-12T00:00:00Z"
    bad["conflict_candidates"][0]["valid_until_utc"]="2026-07-01T00:00:00Z"
    r=ConflictDetector().step(inputs=bad,persist=False)
    assert r["invalid_conflict_count"]==1 and r["conflict_detection_ready"] is False
    resolved=deepcopy(build_context())
    resolved["conflict_candidates"][0]["resolution_score"]=0.95
    rr=ConflictDetector().step(inputs=resolved,persist=False)
    assert rr["detected_conflict_count"]==0
    assert rr["conflicts"][0]["resolution_status"]=="RESOLVED"
    escalated=ConflictDetector().step(inputs=build_context(),persist=False)
    assert escalated["conflicts"][0]["escalation_detected"] is True
    print("AW5_TEMPORAL_ESCALATION_RESOLUTION_OK")
if __name__=="__main__": main()
