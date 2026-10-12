from aw12_context import build_context as build_aw12_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine


def build_context():
    context = build_aw12_context()
    context["ecological_prediction"] = EcologicalPredictionEngine().step(inputs=context, persist=False)
    context["tested_at_utc"] = "2026-07-13T12:00:00Z"
    context["property_scores"] = {
        "distributed_stability": 0.90,
        "coordination": 0.88,
        "civilizational_continuity": 0.91,
        "distributed_memory": 0.89,
        "intergenerational_transmission": 0.86,
        "resilience": 0.90,
        "diversity": 0.87,
        "local_autonomy": 0.84,
        "centralization_resistance": 0.85,
        "future_openness_preservation": 0.92,
        "prediction_capacity": 0.88,
    }
    return context
