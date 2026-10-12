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

import json, py_compile, tempfile
from pathlib import Path
from ontology.conflict_detector import ConflictDetector

ROOT=Path.home()/"open-cognitive-ecology"
def main():
    for p in [ROOT/"ontology/conflict_detector.py",ROOT/"aw5_fast_acceptance_suite.py",ROOT/"conflict_detector_final_lock.py"]:
        py_compile.compile(str(p),cfile=str(Path("/private/tmp")/(p.name+".aw5.pyc")),doraise=True)
    a=ConflictDetector().step(inputs=build_context(),persist=False)
    b=ConflictDetector().step(inputs=build_context(),persist=False)
    assert a["conflict_detection_status"]=="RF_CONFLICT_DETECTION_READY"
    assert a["detected_conflict_count"]==1
    assert a["detection_hash"]==b["detection_hash"]
    with tempfile.TemporaryDirectory(prefix="oce_aw5_") as tmp:
        d=ConflictDetector(root=Path(tmp))
        p=d.step(inputs=build_context(),persist=True)
        assert p["persisted"] is True
        assert json.loads(Path(p["output_path"]).read_text())["detection_hash"]==p["detection_hash"]
    assert a["collective_consciousness_proven"] is False
    assert a["functional_conclusion_only"] is True
    print("AW5_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()
