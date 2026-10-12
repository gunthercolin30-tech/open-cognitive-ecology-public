from pathlib import Path
import py_compile
import tempfile
from aw11_context import build_context
from ontology.ecological_stability_analyzer import EcologicalStabilityAnalyzer


def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw11_compile_") as tmp:
        py_compile.compile("ontology/ecological_stability_analyzer.py", cfile=str(Path(tmp) / "aw11.pyc"), doraise=True)
    with tempfile.TemporaryDirectory(prefix="oce_aw11_") as tmp:
        result = EcologicalStabilityAnalyzer(root=Path(tmp)).step(inputs=build_context(), persist=True)
        assert result["status"] == "ECOLOGICAL_STABILITY_ANALYSIS_READY"
        assert result["ecological_stability_analysis_ready"] is True
        assert 0.0 <= result["stability_score"] <= 1.0
        assert 0.0 <= result["resilience_score"] <= 1.0
        assert 0.0 <= result["diversity_score"] <= 1.0
        assert 0.0 <= result["fragility_score"] <= 1.0
        assert len(result["analysis_hash"]) == 64
        assert Path(result["output_path"]).is_file()
        assert result["collective_consciousness_proven"] is False
        assert result["functional_conclusion_only"] is True
    print("AW11_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
