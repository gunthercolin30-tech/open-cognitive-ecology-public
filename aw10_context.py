from aw9_context import build_context as build_aw9_context
from ontology.collective_consciousness_analyzer import CollectiveConsciousnessAnalyzer


def build_context():
    context = build_aw9_context()
    context["collective_rf_analysis"] = CollectiveConsciousnessAnalyzer().step(
        inputs=context,
        persist=False,
    )
    return context
