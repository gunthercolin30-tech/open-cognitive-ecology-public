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

from copy import deepcopy
from ontology.coalition_detector import CoalitionDetector
def main():
    for blocker in ["dense_cluster_only","shared_rf_only","alignment_only","common_controller","copy_or_clone_explanation","translation_only","external_synchronization","statistical_coincidence","semantic_proximity_only","single_interaction_only","imposed_hierarchy","technical_dependency_only"]:
        c=build_context(); c["coalition_candidates"][0][blocker]=True
        r=CoalitionDetector().step(inputs=c,persist=False)
        assert r["detected_coalition_count"]==0 and blocker in r["coalitions"][0]["false_positive_blockers"]
    print("AW4_FALSE_POSITIVES_BLOCKED_OK")
if __name__=="__main__": main()
