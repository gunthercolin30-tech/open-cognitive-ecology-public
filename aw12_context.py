from aw11_context import build_context as build_aw11_context
from ontology.ecological_stability_analyzer import EcologicalStabilityAnalyzer


def build_context():
    context = build_aw11_context()
    context["ecological_stability"] = EcologicalStabilityAnalyzer().step(
        inputs=context,
        persist=False,
    )
    context["issued_at"] = "2026-07-13T08:00:00Z"
    context["forecast_horizons"] = [1, 7, 30]
    context["trend_signals"] = {
        "stability": 0.08,
        "resilience": 0.06,
        "diversity": 0.04,
        "memory_continuity": 0.05,
        "future_openness": 0.07,
        "centralization_risk": -0.05,
        "conflict_pressure": -0.04,
        "fragmentation_pressure": -0.03,
        "integration": 0.05,
    }
    return context
