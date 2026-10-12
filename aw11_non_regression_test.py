from copy import deepcopy
from aw11_context import build_context
from ontology.ecological_stability_analyzer import EcologicalStabilityAnalyzer

engine = EcologicalStabilityAnalyzer()
ctx = build_context()
original = deepcopy(ctx)
a = engine.step(inputs=ctx, persist=False)
b = engine.step(inputs=deepcopy(ctx), persist=False)
assert ctx == original
assert a["analysis_hash"] == b["analysis_hash"]
assert a["stability_score"] == b["stability_score"]
assert a["timestamp_utc"] != ""
print("AW11_NON_REGRESSION_OK")
