import run_publication_pipeline


def test_functional_benchmark_uses_current_pipeline():
    result = run_publication_pipeline.run_functional_benchmark()

    assert result["primitive"] == "functional_consciousness_behavioral_benchmark"
    assert result["functional_consciousness_benchmark_score"] > 0
