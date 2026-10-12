import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "ontology" / "ecological_prediction_engine.py"
ORIGINAL = SOURCE.read_text(encoding="utf-8")
mutations = [
    (
        "horizon_lower_bound",
        "if 1 <= number <= 3650 and number not in values:",
        "if 0 <= number <= 3650 and number not in values:",
        "c=build_context(); c['forecast_horizons']=[0]; r=EcologicalPredictionEngine().step(c,False); assert r['forecast_horizon']==[1,3,6]",
    ),
    (
        "equal_time_leakage",
        "observed_at <= issued_at",
        "observed_at < issued_at",
        "c=build_context(); c['observed_at']=c['issued_at']; c['observed_values']={'stability':0.5}; r=EcologicalPredictionEngine().step(c,False); assert r['temporal_leakage_detected'] is True",
    ),
    (
        "epistemic_guard",
        '"functional_conclusion_only": True,',
        '"functional_conclusion_only": False,',
        "r=EcologicalPredictionEngine().step(build_context(),False); assert r['functional_conclusion_only'] is True",
    ),
    (
        "numeric_bounds",
        "return round(max(0.0, min(1.0, number)), 6)",
        "return round(number, 6)",
        "e=EcologicalPredictionEngine(); assert e._bounded(2.0)==1.0 and e._bounded(-1.0)==0.0",
    ),
]
for name, old, new, assertion in mutations:
    assert old in ORIGINAL, f"mutation anchor missing: {name}"
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        (temp / "ontology").mkdir()
        (temp / "ontology" / "__init__.py").write_text("", encoding="utf-8")
        (temp / "ontology" / "ecological_prediction_engine.py").write_text(ORIGINAL.replace(old, new, 1), encoding="utf-8")
        shutil.copy2(ROOT / "aw12_context.py", temp / "aw12_context.py")
        code = "from aw12_context import build_context\nfrom ontology.ecological_prediction_engine import EcologicalPredictionEngine\n" + assertion
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(temp),
            env={"PYTHONPATH": str(temp)},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert completed.returncode != 0, f"surviving mutation: {name}"
print("AW12_MUTATION_TEST_OK")
