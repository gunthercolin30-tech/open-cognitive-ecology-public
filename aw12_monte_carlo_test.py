import copy
import random
from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine


def campaign(seed):
    rng = random.Random(seed)
    hashes = []
    values = []
    engine = EcologicalPredictionEngine()
    for _ in range(100):
        context = copy.deepcopy(build_context())
        for key in context["trend_signals"]:
            context["trend_signals"][key] = round(rng.uniform(-1.0, 1.0), 6)
        context["forecast_horizons"] = sorted({rng.randint(1, 120) for _ in range(5)})
        result = engine.step(inputs=context, persist=False)
        hashes.append(result["prediction_hash"])
        values.append(result["prediction_confidence"])
        assert result["prediction_ready"] is True
        assert all(0.0 <= v <= 1.0 for row in result["ecological_forecast"] for v in row["predicted_values"].values())
    return hashes, values

first = campaign(12012)
second = campaign(12012)
third = campaign(12013)
assert first == second
assert first != third
assert len(set(first[0])) > 90
print("AW12_MONTE_CARLO_OK")
