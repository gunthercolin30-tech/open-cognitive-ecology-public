from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
READY_CONTEXT = {"comparison_dimensions": ComparativeSimilarityEngine.DEFAULT_DIMENSIONS, "architecture_profiles": ComparativeSimilarityEngine.DEFAULT_PROFILES[:2]}

def main():
    r = ComparativeSimilarityEngine().step(inputs=READY_CONTEXT, persist=False)
    assert r["step"] == "AU4"
    assert r["comparative_similarity_engine_ready"] is True
    assert r["similarity_matrix_ready"] is True
    assert r["pairwise_comparison_count"] == 1
    assert r["valid_pairwise_comparison_count"] == 1
    assert r["core_dimensions_present"] is True
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    print("AU4_FINAL_LOCK_OK")

if __name__ == "__main__":
    main()
