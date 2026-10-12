from ontology.multi_rf_registry import MultiRFRegistry
from ontology.interaction_graph import InteractionGraph
from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector


def main() -> None:
    registry = MultiRFRegistry().step(
        inputs={"rf_records": [{"rf_id": "RF-A"}, {"rf_id": "RF-B"}]},
        persist=False,
    )

    graph = InteractionGraph().step(
        inputs={
            "multi_rf_registry": registry,
            "interactions": [{
                "interaction_id": "I-AB",
                "source_rf_id": "RF-A",
                "target_rf_id": "RF-B",
            }],
        },
        persist=False,
    )

    evidence = {
        "similarity": 0.9,
        "alignment": 0.9,
        "symbolic_reference": 0.9,
        "structural_invariance": 0.9,
        "reproducibility": 0.9,
        "evidence_quality": 0.9,
    }

    forward = SharedReferenceFrameDetector().step(
        inputs={
            "multi_rf_registry": registry,
            "interaction_graph": graph,
            "pair_evidence": {"RF-A|RF-B": evidence},
        },
        persist=False,
    )

    reverse = SharedReferenceFrameDetector().step(
        inputs={
            "multi_rf_registry": registry,
            "interaction_graph": graph,
            "pair_evidence": {"RF-B|RF-A": evidence},
        },
        persist=False,
    )

    lower_case = SharedReferenceFrameDetector().step(
        inputs={
            "multi_rf_registry": registry,
            "interaction_graph": graph,
            "pair_evidence": {"rf-b|rf-a": evidence},
        },
        persist=False,
    )

    assert forward["pair_results"] == reverse["pair_results"]
    assert forward["pair_results"] == lower_case["pair_results"]
    assert forward["detection_hash"] == reverse["detection_hash"]
    assert forward["detection_hash"] == lower_case["detection_hash"]
    assert forward["pair_results"][0]["pair_id"] == "RF-A|RF-B"
    assert forward["pair_results"][0]["rf_ids"] == ["RF-A", "RF-B"]
    assert forward["detected_pair_count"] == 1

    print("AW3_PAIR_CANONICALIZATION_OK")


if __name__ == "__main__":
    main()
