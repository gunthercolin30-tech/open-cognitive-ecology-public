from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
from ontology.consciousness_distance_metric import ConsciousnessDistanceMetric
from ontology.clustering_engine import ClusteringEngine

READY_CONTEXT = {
    "comparison_dimensions": ["RF", "OMEGA", "PI", "MEI", "CRI", "GOV", "LONG", "AUDIT"],
    "architecture_profiles": ComparativeSimilarityEngine.DEFAULT_PROFILES,
}


def main():
    similarity = ComparativeSimilarityEngine().step(
        inputs=READY_CONTEXT,
        persist=False,
    )
    distance = ConsciousnessDistanceMetric().step(
        inputs={"comparative_similarity_engine": similarity},
        persist=False,
    )
    result = ClusteringEngine().step(
        inputs={
            "consciousness_distance_metric": distance,
            "clustering_threshold": 0.35,
        },
        persist=False,
    )

    assert result["step"] == "AU6"
    assert result["clustering_engine_status"] == "CLUSTERING_ENGINE_READY"
    assert result["clustering_engine_ready"] is True
    assert result["cluster_model_ready"] is True
    assert result["architecture_count"] == 3
    assert result["cluster_count"] >= 1
    assert result["assignments_complete"] is True
    assert result["coverage_sufficient"] is True
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False

    print("AU6_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
