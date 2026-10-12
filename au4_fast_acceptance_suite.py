from pathlib import Path
import py_compile
from ontology.comparative_similarity_engine import ComparativeSimilarityEngine
ROOT = Path.home() / "open-cognitive-ecology"
READY_CONTEXT = {"comparison_dimensions": ComparativeSimilarityEngine.DEFAULT_DIMENSIONS, "architecture_profiles": ComparativeSimilarityEngine.DEFAULT_PROFILES}

def main():
    py_compile.compile(str(ROOT / "ontology" / "comparative_similarity_engine.py"), cfile="/private/tmp/au4_comparative_similarity_engine.pyc", doraise=True)
    r = ComparativeSimilarityEngine().step(inputs=READY_CONTEXT, persist=False)
    assert r["step"] == "AU4"
    assert r["comparative_similarity_engine_ready"] is True
    assert r["similarity_matrix_ready"] is True
    assert r["pairwise_comparison_count"] == 3
    assert r["valid_pairwise_comparison_count"] == 3
    assert r["core_dimensions_present"] is True
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    degraded = ComparativeSimilarityEngine().step(inputs={"comparison_dimensions":["RF","OMEGA","PI","MEI","CRI"],"architecture_profiles":[{"architecture_id":"single","comparison_ready":True,"profile_confidence":1.0,"rf_profile_vector":{"RF":1.0,"OMEGA":1.0,"PI":1.0,"MEI":1.0,"CRI":1.0}}]}, persist=False)
    assert degraded["comparative_similarity_engine_ready"] is False
    assert degraded["pairwise_comparison_count"] == 0
    print("AU4_FAST_ACCEPTANCE_OK")

if __name__ == "__main__":
    main()
