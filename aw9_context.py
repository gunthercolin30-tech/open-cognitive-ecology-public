from ontology.multi_rf_registry import MultiRFRegistry
from ontology.interaction_graph import InteractionGraph
from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector
from ontology.coalition_detector import CoalitionDetector
from ontology.conflict_detector import ConflictDetector
from ontology.reference_frame_merging import ReferenceFrameMerging
from ontology.reference_frame_fragmentation import ReferenceFrameFragmentation
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine


def build_context():
    rf_records = [
        {"rf_id":"RF-A","node_ids":["NODE-A"],"lineage_id":"LINEAGE-A"},
        {"rf_id":"RF-B","node_ids":["NODE-B"],"lineage_id":"LINEAGE-B"},
        {"rf_id":"RF-C","node_ids":["NODE-C"],"lineage_id":"LINEAGE-C"},
    ]
    registry = MultiRFRegistry().step(inputs={"rf_records": rf_records}, persist=False)
    interactions = [
        {"interaction_id":"I-AB","source_rf_id":"RF-A","target_rf_id":"RF-B","interaction_type":"COORDINATION","directed":False,"weight":0.9,"confidence":0.95},
        {"interaction_id":"I-AC","source_rf_id":"RF-A","target_rf_id":"RF-C","interaction_type":"COOPERATION","directed":False,"weight":0.85,"confidence":0.92},
        {"interaction_id":"I-BC","source_rf_id":"RF-B","target_rf_id":"RF-C","interaction_type":"INFORMATION_EXCHANGE","directed":False,"weight":0.88,"confidence":0.93},
    ]
    graph = InteractionGraph().step(inputs={"multi_rf_registry":registry,"interactions":interactions}, persist=False)
    pair_evidence = {key:{"similarity":0.9,"alignment":0.88,"symbolic_reference":0.86,"structural_invariance":0.84,"reproducibility":0.9,"evidence_quality":0.95,"source_refs":["AW9-SYNTHETIC"]} for key in ["RF-A|RF-B","RF-A|RF-C","RF-B|RF-C"]}
    shared = SharedReferenceFrameDetector().step(inputs={"multi_rf_registry":registry,"interaction_graph":graph,"pair_evidence":pair_evidence}, persist=False)
    coalition = CoalitionDetector().step(inputs={"multi_rf_registry":registry,"interaction_graph":graph,"shared_reference_frame_detection":shared,"coalition_candidates":[{"coalition_id":"COAL-ABC","member_rf_ids":["RF-A","RF-B","RF-C"],"cohesion_score":0.9,"reciprocity_score":0.9,"shared_goal_score":0.92,"coordination_score":0.9,"temporal_stability_score":0.88,"resilience_score":0.85,"boundary_score":0.8,"evidence_quality":0.95,"observation_count":12,"member_contributions":{"RF-A":0.8,"RF-B":0.8,"RF-C":0.8},"source_refs":["AW9-SYNTHETIC"]}]}, persist=False)
    conflict = ConflictDetector().step(inputs={"multi_rf_registry":registry,"interaction_graph":graph,"conflict_candidates":[]}, persist=False)
    merging = ReferenceFrameMerging().step(inputs={"multi_rf_registry":registry,"merge_candidates":[]}, persist=False)
    fragmentation = ReferenceFrameFragmentation().step(inputs={"multi_rf_registry":registry,"fragmentation_candidates":[]}, persist=False)
    base = {"memory_record_id":"MEM-AW9","memory_namespace":"civilization","memory_scope":"distributed","origin_rf_id":"RF-A","origin_lineage_id":"LINEAGE-A","writer_id":"RF-A","replica_ids":["RF-A","RF-B","RF-C"],"acknowledged_replica_ids":["RF-A","RF-B","RF-C"],"provenance_chain":[{"source":"AW9-SYNTHETIC"}],"transmission_chain":[{"from":"GEN-1","to":"GEN-2"}],"retention_policy":{"mode":"governed"},"forgetting_policy":{"mode":"governed","authorized":False},"availability_score":1.0,"loss_tolerance_score":0.67,"provenance_coverage":1.0,"lineage_preservation_score":1.0,"future_openness_preservation_score":0.95}
    memory = CivilizationalMemoryEngine().step(inputs={"multi_rf_registry":registry,"memory_records":[dict(base,version_id="MEM-AW9-V1",parent_version_ids=[],content={"generation":1}),dict(base,version_id="MEM-AW9-V2",parent_version_ids=["MEM-AW9-V1"],content={"generation":2})]}, persist=False)
    return {"multi_rf_registry":registry,"interaction_graph":graph,"shared_reference_frame_detection":shared,"coalition_detection":coalition,"conflict_detection":conflict,"reference_frame_merging":merging,"reference_frame_fragmentation":fragmentation,"civilizational_memory":memory}
