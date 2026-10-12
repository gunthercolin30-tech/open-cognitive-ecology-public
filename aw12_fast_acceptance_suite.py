from pathlib import Path
import py_compile
import tempfile
from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine


def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw12_compile_") as tmp:
        py_compile.compile("ontology/ecological_prediction_engine.py", cfile=str(Path(tmp) / "aw12.pyc"), doraise=True)
    with tempfile.TemporaryDirectory(prefix="oce_aw12_") as tmp:
        result = EcologicalPredictionEngine(root=Path(tmp)).step(inputs=build_context(), persist=True)
        assert result["prediction_status"] == "RF_ECOLOGY_PREDICTION_READY"
        assert result["prediction_ready"] is True
        assert len(result["ecological_forecast"]) == 3
        assert result["forecast_horizon"] == [1, 7, 30]
        assert 0.0 <= result["prediction_confidence"] <= 1.0
        assert 0.0 <= result["prediction_uncertainty"] <= 1.0
        assert len(result["prediction_hash"]) == 64
        assert Path(result["output_path"]).is_file()
        assert Path(result["history_path"]).is_file()
        assert result["collective_consciousness_proven"] is False
        assert result["functional_conclusion_only"] is True
    print("AW12_FAST_ACCEPTANCE_OK")

if __name__ == "__main__":
    main()
