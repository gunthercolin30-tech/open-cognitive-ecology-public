from pathlib import Path
import json, py_compile, tempfile
from aw9_context import build_context
from ontology.collective_consciousness_analyzer import CollectiveConsciousnessAnalyzer


def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw9_compile_") as tmp:
        py_compile.compile("ontology/collective_consciousness_analyzer.py", cfile=str(Path(tmp)/"collective_consciousness_analyzer.pyc"), doraise=True)
    with tempfile.TemporaryDirectory(prefix="oce_aw9_") as tmp:
        analyzer = CollectiveConsciousnessAnalyzer(root=Path(tmp))
        first = analyzer.step(inputs=build_context(), persist=True)
        second = analyzer.step(inputs=build_context(), persist=False)
        assert first["status"] == "COLLECTIVE_RF_ANALYSIS_READY"
        assert first["collective_rf_analysis_ready"] is True
        assert first["population_size"] == 3
        assert first["functional_collective_integration"] >= 0.55
        assert first["analysis_hash"] == second["analysis_hash"]
        assert Path(first["output_path"]).exists()
        assert json.loads(Path(first["output_path"]).read_text())["status"] == "COLLECTIVE_RF_ANALYSIS_READY"
        assert first["collective_consciousness_proven"] is False
        assert first["functional_conclusion_only"] is True
    print("AW9_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
