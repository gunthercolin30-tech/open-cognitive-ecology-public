from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
from ontology.consciousness_distance_metric import ConsciousnessDistanceMetric

READY_CONTEXT = {
    "comparison_dimensions": ["RF", "OMEGA", "PI", "MEI", "CRI", "GOV", "LONG", "AUDIT"],
    "architecture_profiles": ComparativeSimilarityEngine.DEFAULT_PROFILES[:2],
}


def main():
    similarity = ComparativeSimilarityEngine().step(
        inputs=READY_CONTEXT,
        persist=False,
    )
    result = ConsciousnessDistanceMetric().step(
        inputs={"comparative_similarity_engine": similarity},
        persist=False,
    )

    assert result["step"] == "AU5"
    assert result["consciousness_distance_metric_status"] == "CONSCIOUSNESS_DISTANCE_METRIC_READY"
    assert result["consciousness_distance_metric_ready"] is True
    assert result["distance_matrix_ready"] is True
    assert result["pairwise_distance_count"] == 1
    assert result["identity_axiom_satisfied"] is True
    assert result["symmetry_axiom_satisfied"] is True
    assert result["boundedness_axiom_satisfied"] is True
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False

    print("AU5_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
