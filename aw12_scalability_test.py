import copy
import time
import tracemalloc
from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine

engine = EcologicalPredictionEngine()
measurements = []
for population_size in (100, 500, 1000, 5000):
    context = copy.deepcopy(build_context())
    context["rf_population"] = [
        {"rf_id": f"RF-{index:05d}", "weight": (index % 100) / 100.0}
        for index in range(population_size)
    ]
    context["forecast_horizons"] = list(range(1, 366, 7))
    tracemalloc.start()
    started = time.perf_counter()
    result = engine.step(inputs=context, persist=False)
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert result["prediction_status"] == "RF_ECOLOGY_PREDICTION_READY"
    assert len(result["ecological_forecast"]) == len(context["forecast_horizons"])
    assert elapsed < 5.0
    assert peak < 128 * 1024 * 1024
    measurements.append((population_size, elapsed, peak))
assert measurements[-1][1] < max(5.0, measurements[0][1] * 20.0 + 0.5)
print("AW12_SCALABILITY_OK")
