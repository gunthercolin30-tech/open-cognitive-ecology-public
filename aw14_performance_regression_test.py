import time
import tracemalloc
from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

certifier = EcologicalCertifier()
tracemalloc.start()
start = time.perf_counter()
for _ in range(20):
    result = certifier.step(inputs=build_context(), persist=False)
elapsed = time.perf_counter() - start
_, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
assert result["ecology_complete"] is True
assert elapsed < 20.0, elapsed
assert peak < 128 * 1024 * 1024, peak
print("AW14_PERFORMANCE_REGRESSION_OK")
