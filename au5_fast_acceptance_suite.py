from pathlib import Path
import py_compile

from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
from ontology.consciousness_distance_metric import ConsciousnessDistanceMetric

ROOT = Path.home() / "open-cognitive-ecology"

SIMILARITY_INPUTS = {
    "comparison_dimensions": ["RF", "OMEGA", "PI", "MEI", "CRI", "GOV", "LONG", "AUDIT"],
    "architecture_profiles": ComparativeSimilarityEngine.DEFAULT_PROFILES,
}


def main():
    py_compile.compile(
        str(ROOT / "ontology" / "consciousness_distance_metric.py"),
        cfile="/private/tmp/au5_consciousness_distance_metric.pyc",
        doraise=True,
    )

    similarity = ComparativeSimilarityEngine().step(
        inputs=SIMILARITY_INPUTS,
        persist=False,
    )
    result = ConsciousnessDistanceMetric().step(
        inputs={"comparative_similarity_engine": similarity},
        persist=False,
    )

    assert result["step"] == "AU5"
    assert result["consciousness_distance_metric_ready"] is True
    assert result["distance_matrix_ready"] is True
    assert result["distance_metric_id"] == "D_RF"
    assert result["architecture_count"] == 3
    assert result["pairwise_distance_count"] == 3
    assert result["valid_pairwise_distance_count"] == 3
    assert result["identity_axiom_satisfied"] is True
    assert result["symmetry_axiom_satisfied"] is True
    assert result["boundedness_axiom_satisfied"] is True

    matrix = result["distance_matrix"]
    for architecture_id in matrix:
        assert matrix[architecture_id][architecture_id] == 0.0
        for other_id, value in matrix[architecture_id].items():
            assert 0.0 <= value <= 1.0
            assert value == matrix[other_id][architecture_id]

    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False

    degraded = ConsciousnessDistanceMetric().step(
        inputs={
            "comparative_similarity_engine": {
                "comparative_similarity_engine_ready": False,
                "similarity_matrix": {"only": {"only": 1.0}},
                "pairwise_similarities": [],
            }
        },
        persist=False,
    )
    assert degraded["consciousness_distance_metric_ready"] is False
    assert degraded["pairwise_distance_count"] == 0
    assert degraded["consciousness_proven"] is False

    print("AU5_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
