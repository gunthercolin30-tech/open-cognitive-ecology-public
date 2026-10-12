from pathlib import Path
import py_compile

from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
from ontology.consciousness_distance_metric import ConsciousnessDistanceMetric
from ontology.clustering_engine import ClusteringEngine
from ontology.taxonomy_builder import TaxonomyBuilder

ROOT = Path.home() / "open-cognitive-ecology"
READY_CONTEXT = {
    "comparison_dimensions": ["RF", "OMEGA", "PI", "MEI", "CRI", "GOV", "LONG", "AUDIT"],
    "architecture_profiles": ComparativeSimilarityEngine.DEFAULT_PROFILES,
}


def build_ready_result(extra_inputs=None):
    similarity = ComparativeSimilarityEngine().step(inputs=READY_CONTEXT, persist=False)
    distance = ConsciousnessDistanceMetric().step(
        inputs={"comparative_similarity_engine": similarity}, persist=False
    )
    clustering = ClusteringEngine().step(
        inputs={"consciousness_distance_metric": distance, "clustering_threshold": 0.35},
        persist=False,
    )
    inputs = {
        "rf_profile_builder": {
            "rf_profile_ready": True,
            "canonical_profile_id": "oce_rf_star",
            "architecture_profiles": ComparativeSimilarityEngine.DEFAULT_PROFILES,
        },
        "comparative_similarity_engine": similarity,
        "consciousness_distance_metric": distance,
        "clustering_engine": clustering,
    }
    inputs.update(extra_inputs or {})
    return TaxonomyBuilder().step(inputs=inputs, persist=False)


def main():
    for path in [
        ROOT / "ontology" / "taxonomy_builder.py",
        ROOT / "au7_fast_acceptance_suite.py",
        ROOT / "au7_final_lock.py",
    ]:
        py_compile.compile(
            str(path), cfile=f"/private/tmp/{path.name}.pyc", doraise=True
        )

    result = build_ready_result()
    assert result["step"] == "AU7"
    assert result["taxonomy_builder_status"] == "TAXONOMY_BUILDER_READY"
    assert result["taxonomy_builder_ready"] is True
    assert result["architecture_count"] == 3
    assert result["classified_architecture_count"] == 3
    assert result["taxonomy_depth"] == 6
    assert result["taxonomy_node_count"] > result["architecture_count"]
    assert result["taxonomy_edge_count"] >= result["architecture_count"]
    assert result["assignments_complete"] is True
    assert 0.0 <= result["coverage_score"] <= 1.0
    assert len(result["taxonomy_hash"]) == 64

    repeated = build_ready_result()
    assert repeated["taxonomy_hash"] == result["taxonomy_hash"]
    assert repeated["taxonomy_entries"] == result["taxonomy_entries"]

    future_profiles = list(ComparativeSimilarityEngine.DEFAULT_PROFILES) + [{
        "architecture_id": "future_test_architecture",
        "architecture_type": "future_architecture",
        "label": "Future test architecture",
        "evidence_tier": "synthetic_placeholder",
        "rf_profile_vector": {"RF": 0.5, "OMEGA": 0.5, "PI": 0.5, "MEI": 0.5, "CRI": 0.5, "GOV": 0.5, "LONG": 0.5, "AUDIT": 0.5},
        "coverage": 1.0,
        "profile_confidence": 0.45,
        "raw_rf_profile_score": 0.5,
        "weighted_rf_profile_score": 0.225,
        "comparison_ready": True,
    }]
    future_similarity = ComparativeSimilarityEngine().step(
        inputs={"comparison_dimensions": READY_CONTEXT["comparison_dimensions"], "architecture_profiles": future_profiles},
        persist=False,
    )
    future_distance = ConsciousnessDistanceMetric().step(
        inputs={"comparative_similarity_engine": future_similarity}, persist=False
    )
    future_clustering = ClusteringEngine().step(
        inputs={"consciousness_distance_metric": future_distance}, persist=False
    )
    extended = TaxonomyBuilder().step(
        inputs={
            "rf_profile_builder": {"rf_profile_ready": True, "canonical_profile_id": "oce_rf_star", "architecture_profiles": future_profiles},
            "comparative_similarity_engine": future_similarity,
            "consciousness_distance_metric": future_distance,
            "clustering_engine": future_clustering,
        },
        persist=False,
    )
    assert extended["taxonomy_builder_ready"] is True
    assert extended["architecture_count"] == 4
    assert "future_test_architecture" in extended["architecture_assignments"]

    degraded = TaxonomyBuilder().step(
        inputs={
            "rf_profile_builder": {"rf_profile_ready": False, "architecture_profiles": []},
            "consciousness_distance_metric": {"consciousness_distance_metric_ready": False, "distance_matrix": {}},
            "clustering_engine": {"clustering_engine_ready": False, "cluster_assignments": {}},
        },
        persist=False,
    )
    assert degraded["taxonomy_builder_ready"] is False
    assert degraded["taxonomy_builder_status"] == "TAXONOMY_BUILDER_INCOMPLETE"

    for payload in (result, extended, degraded):
        assert payload["functional_conclusion_only"] is True
        assert payload["phenomenology_undetermined"] is True
        assert payload["consciousness_proven"] is False
        assert payload["qualia_proven"] is False
        assert payload["subjectivity_proven"] is False
        assert payload["phenomenology_proven"] is False

    print("AU7_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
