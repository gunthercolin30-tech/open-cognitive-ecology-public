from pathlib import Path
import py_compile

from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
from ontology.consciousness_distance_metric import ConsciousnessDistanceMetric
from ontology.clustering_engine import ClusteringEngine

ROOT = Path.home() / "open-cognitive-ecology"

SIMILARITY_INPUTS = {
    "comparison_dimensions": ["RF", "OMEGA", "PI", "MEI", "CRI", "GOV", "LONG", "AUDIT"],
    "architecture_profiles": ComparativeSimilarityEngine.DEFAULT_PROFILES,
}


def main():
    py_compile.compile(
        str(ROOT / "ontology" / "clustering_engine.py"),
        cfile="/private/tmp/au6_clustering_engine.pyc",
        doraise=True,
    )

    similarity = ComparativeSimilarityEngine().step(
        inputs=SIMILARITY_INPUTS,
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
    assert result["clustering_engine_ready"] is True
    assert result["cluster_model_ready"] is True
    assert result["architecture_count"] == 3
    assert result["cluster_count"] >= 1
    assert result["assignments_complete"] is True
    assert len(result["cluster_assignments"]) == 3
    assert 0.0 <= result["mean_silhouette_like_score"] <= 1.0
    assert 0.0 <= result["cluster_stability_score"] <= 1.0

    for record in result["clusters"]:
        assert record["member_count"] == len(record["members"])
        assert 0.0 <= record["mean_intra_cluster_distance"] <= 1.0
        assert 0.0 <= record["mean_inter_cluster_distance"] <= 1.0
        assert 0.0 <= record["silhouette_like_score"] <= 1.0

    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False

    degraded = ClusteringEngine().step(
        inputs={
            "consciousness_distance_metric": {
                "consciousness_distance_metric_ready": False,
                "distance_matrix": {"only": {"only": 0.0}},
            },
            "clustering_threshold": 0.35,
        },
        persist=False,
    )
    assert degraded["clustering_engine_ready"] is False
    assert degraded["architecture_count"] == 1
    assert degraded["consciousness_proven"] is False

    print("AU6_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
