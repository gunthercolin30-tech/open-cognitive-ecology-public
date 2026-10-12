from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
from ontology.consciousness_distance_metric import ConsciousnessDistanceMetric
from ontology.clustering_engine import ClusteringEngine
from ontology.taxonomy_builder import TaxonomyBuilder

READY_CONTEXT = {
    "comparison_dimensions": ["RF", "OMEGA", "PI", "MEI", "CRI", "GOV", "LONG", "AUDIT"],
    "architecture_profiles": ComparativeSimilarityEngine.DEFAULT_PROFILES,
}


def main():
    similarity = ComparativeSimilarityEngine().step(inputs=READY_CONTEXT, persist=False)
    distance = ConsciousnessDistanceMetric().step(
        inputs={"comparative_similarity_engine": similarity}, persist=False
    )
    clustering = ClusteringEngine().step(
        inputs={"consciousness_distance_metric": distance, "clustering_threshold": 0.35},
        persist=False,
    )
    result = TaxonomyBuilder().step(
        inputs={
            "rf_profile_builder": {
                "rf_profile_ready": True,
                "canonical_profile_id": "oce_rf_star",
                "architecture_profiles": ComparativeSimilarityEngine.DEFAULT_PROFILES,
            },
            "comparative_similarity_engine": similarity,
            "consciousness_distance_metric": distance,
            "clustering_engine": clustering,
        },
        persist=False,
    )

    assert result["step"] == "AU7"
    assert result["taxonomy_builder_status"] == "TAXONOMY_BUILDER_READY"
    assert result["taxonomy_builder_ready"] is True
    assert result["architecture_count"] == 3
    assert result["classified_architecture_count"] == 3
    assert result["taxonomy_depth"] == 6
    assert result["assignments_complete"] is True
    assert result["coverage_score"] == 1.0
    assert len(result["taxonomy_hash"]) == 64
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False

    print("AU7_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
