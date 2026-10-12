from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine
c=build_context(); good=EcologicalPredictionEngine().step(c,False)
c["ecological_stability"]["stability_score"]=0.05
c["ecological_stability"]["resilience_score"]=0.05
c["ecological_stability"]["diversity_score"]=0.05
c["trend_signals"].update({"stability":-0.9,"resilience":-0.9,"diversity":-0.9})
bad=EcologicalPredictionEngine().step(c,False)
assert bad["predicted_resilience"][-1] < good["predicted_resilience"][-1]
assert bad["predicted_diversity"][-1] < good["predicted_diversity"][-1]
print("AW12_DEGRADATION_OK")
